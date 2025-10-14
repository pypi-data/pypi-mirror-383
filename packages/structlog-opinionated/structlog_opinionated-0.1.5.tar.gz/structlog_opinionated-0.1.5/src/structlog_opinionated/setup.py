"""Setup functions for configuring structlog."""

import logging
import logging.config
import sys
from datetime import datetime
from typing import Any, cast

import structlog

from .config import LogConfig
from .opinionated_bound_logger import OpinionatedBoundLogger
from .processors import add_asyncio_context, combine_callsite
from .vertical_console_renderer import VerticalConsoleRenderer

# Track whether logging has been configured
_logging_configured = False


class ModuleDebugFilter(logging.Filter):
    """Filter that enables DEBUG level for loggers matching debug patterns.

    Uses a cache for efficiency - exact logger names are checked first,
    then substring matching is performed and cached.
    """

    def __init__(self, debug_patterns: dict[str, bool], base_level: str):
        super().__init__()
        # Convert underscore to dot and keep only enabled patterns
        self.debug_patterns = [pattern.replace("_", ".") for pattern, enabled in debug_patterns.items() if enabled]
        self.base_level_num = logging.getLevelName(base_level.upper())
        # Cache: logger_name -> should_allow_debug (bool)
        self.cache: dict[str, bool] = {}

    def _should_allow_debug(self, logger_name: str) -> bool:
        """Check if logger name matches any debug pattern (with caching)."""
        # Fast path: check cache
        if logger_name in self.cache:
            return self.cache[logger_name]

        # Slow path: check all patterns
        result = any(pattern in logger_name for pattern in self.debug_patterns)

        # Store in cache for next time
        self.cache[logger_name] = result
        return result

    def filter(self, record: logging.LogRecord) -> bool:
        # If record level >= base level, always allow
        if record.levelno >= self.base_level_num:
            return True

        # If record is DEBUG, check if logger matches any pattern
        if record.levelno == logging.DEBUG:
            return self._should_allow_debug(record.name)

        return False


def setup(config: LogConfig | None = None) -> None:
    """Configure structlog with opinionated defaults for asyncio servers.

    This function sets up structlog with a unified ProcessorFormatter configuration
    that works seamlessly with both structlog loggers and standard library loggers.
    It configures:
    - JSON output via ProcessorFormatter
    - ISO8601 timestamps
    - Asyncio task tracking
    - Contextvars support for request-scoped logging
    - Proper exception formatting
    - Unified formatting for all loggers (structlog and stdlib)

    Note: This function is automatically called on the first call to get_logger()
    if it hasn't been called explicitly. You only need to call it explicitly if you
    want to customize the configuration.

    Example:
        ```python
        import structlog_opinionated

        # Automatic setup with defaults (no setup() call needed)
        logger = structlog_opinionated.get_logger(__name__)
        logger.info("Server started")

        # Or customize configuration explicitly
        from structlog_opinionated import LogConfig
        config = LogConfig(level="DEBUG")
        structlog_opinionated.setup(config)

        # Or use environment variables (no code needed)
        # export LOG_LEVEL=DEBUG
        # export LOG_DEBUG__MAIN=1
        logger = structlog_opinionated.get_logger(__name__)
        ```

    Args:
        config: Optional LogConfig instance. If None, uses default configuration.
    """
    global _logging_configured

    if config is None:
        config = LogConfig()

    _logging_configured = True

    # Determine if we should use JSON or Console rendering for stdout
    # Priority: force_json > force_console > TTY detection
    # Note: ConsoleRenderer automatically uses Rich for beautiful tracebacks if Rich is installed
    if config.force_json:
        use_json_console = True
    elif config.force_console:
        use_json_console = False
    else:
        # Default: Use JSON for non-TTY, console for TTY
        use_json_console = not sys.stdout.isatty()

    # Shared processors for both structlog and stdlib logging
    # These run on ALL log entries before the final rendering
    shared_processors: list[structlog.types.Processor] = [
        structlog.processors.TimeStamper(fmt="iso"),  # Add timestamp
        structlog.stdlib.add_log_level,  # Add log level to event dict
        structlog.stdlib.add_logger_name,  # Add logger name to event dict
        structlog.stdlib.ExtraAdder(),  # Add extra attributes from stdlib logging (e.g., logger.info("msg", extra={...}))
        add_asyncio_context,  # Add asyncio task information
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.PATHNAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),  # Add caller info using structlog's standard processor
        combine_callsite,  # Combine pathname, lineno into single callsite field
        structlog.contextvars.merge_contextvars,  # Merge in context from structlog's contextvars
        structlog.processors.StackInfoRenderer(),  # Format stack info if present
        # NOTE: Do NOT add format_exc_info here - ConsoleRenderer handles exceptions automatically
        # and will use Rich for beautiful tracebacks if Rich is installed
        structlog.processors.UnicodeDecoder(),  # Decode unicode escape sequences
    ]

    # Determine handler level - if debug patterns are configured, handlers must accept DEBUG
    # so the filter can decide whether to allow the record through
    handler_level = "DEBUG" if config.debug else config.level.upper()

    # Build logging configuration
    log_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.ExceptionRenderer(
                        exception_formatter=structlog.tracebacks.ExceptionDictTransformer()
                    ),  # Format exceptions as structured JSON for the json formatter
                    structlog.processors.JSONRenderer(),
                ],
                "foreign_pre_chain": shared_processors,
            },
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    # Use VerticalConsoleRenderer if console_vertical_keys is True
                    VerticalConsoleRenderer(colors=True) if config.console_vertical_keys else structlog.dev.ConsoleRenderer(colors=True),
                ],
                "foreign_pre_chain": shared_processors,
            },
        },
        "handlers": {
            "default": {
                "level": handler_level,
                "class": "logging.StreamHandler",
                "formatter": "json" if use_json_console else "console",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "DEBUG",  # Root logger always at DEBUG, filtering happens at handler level
                "propagate": True,
            },
        },
    }

    # Add file handler if file_prefix is configured
    if config.file_prefix:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"{config.file_prefix}_{timestamp}.jsonl"

        log_config["handlers"]["file"] = {
            "level": handler_level,
            "class": "logging.FileHandler",
            "formatter": "json",
            "filename": log_filename,
            "mode": "a",
        }
        # Add file handler to root logger ("" = root logger, parent of all loggers)
        log_config["loggers"][""]["handlers"].append("file")

    # Configure standard library logging with ProcessorFormatter
    logging.config.dictConfig(log_config)

    # Add module-specific debug filter if debug patterns are configured
    if config.debug:
        debug_filter = ModuleDebugFilter(config.debug, config.level)
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            handler.addFilter(debug_filter)

    # Configure structlog to use the same processors + ProcessorFormatter
    structlog.configure(
        processors=[
            *shared_processors,
            # Prepare event dict for logging stdlib
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=OpinionatedBoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        context_class=dict,  # Python's dict is ordered, and we want it ordered so do not change this
    )


def get_logger(name: str | None = None) -> OpinionatedBoundLogger:
    """Get a configured logger instance.

    This is a convenience wrapper around structlog.stdlib.get_logger() with
    proper type hints. Returns an OpinionatedBoundLogger with additional
    .context() method for scoped temporary bindings.

    If setup() has not been called yet, this function will automatically call
    it with default configuration. You only need to call setup() explicitly if
    you want to customize the configuration.

    Args:
        name: Optional logger name. If None, uses the calling module's name.

    Returns:
        A configured OpinionatedBoundLogger instance

    Context Management:
        - .bind(**kwargs) - Returns NEW logger with permanent bindings
          IMPORTANT: Reassign the variable since it returns a new instance
        - .context(**kwargs) - Temporary bindings with auto-cleanup

    Example:
        ```python
        # No need to call setup() - it's automatic!
        logger = get_logger(__name__)

        # .bind() returns NEW logger - must reassign!
        logger = logger.bind(service="api", version="1.0")

        # Temporary bindings with auto-cleanup
        with logger.context(request_id="123"):
            logger.info("Processing request")
            # Includes: service, version, request_id
        # request_id automatically removed

        logger.info("Next request")
        # Includes: service, version only
        ```
    """
    global _logging_configured

    if not _logging_configured:
        setup()

    return cast(OpinionatedBoundLogger, structlog.stdlib.get_logger(name))
