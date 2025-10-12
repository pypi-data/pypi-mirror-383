"""Vertical console renderer with colored output and multi-line key-value pairs."""

from __future__ import annotations

import structlog
from structlog.dev import ConsoleRenderer

try:
    import colorama  # type: ignore[import-untyped]
except ImportError:
    colorama = None


class VerticalConsoleRenderer:
    """Hybrid console renderer that displays extra fields vertically.

    This renderer combines the colored, formatted output of ConsoleRenderer
    for the main log line with vertical display of additional key-value pairs.

    The main line shows: timestamp, level, event message, and location info.
    Additional fields are displayed one per line below the main line, indented,
    formatted as key=value with colored keys.

    Example Output:
        2025-10-09 12:34:56 [info     ] User logged in                  user.py:42
          user_id=123
          session_id=abc-123
          ip_address=192.168.1.1

    Args:
        colors: Enable colored output (default: True)
        pad_event: Pad event message to this many characters (default: 30)
        indent: Indentation for vertical key-value pairs (default: "  ")
        exclude_keys: Additional keys to exclude from vertical display
        include_core_in_vertical: Show core fields vertically too (default: False)
    """

    # Core fields that are shown in the main line by ConsoleRenderer
    CORE_FIELDS = {
        "event",
        "timestamp",
        "level",
        "logger",
        "pathname",
        "lineno",
        "func_name",
        "task_name",
        "task_id",
    }

    def __init__(
        self,
        colors: bool = True,
        pad_event: int = 30,
        indent: str = "  ",
        exclude_keys: set[str] | None = None,
        include_core_in_vertical: bool = False,
    ):
        """Initialize the vertical console renderer.

        Args:
            colors: Enable colored output
            pad_event: Pad event message to this many characters
            indent: String to use for indenting key-value pairs
            exclude_keys: Additional keys to exclude from vertical display
            include_core_in_vertical: If True, show core fields vertically too
        """
        self._console = ConsoleRenderer(colors=colors, pad_event=pad_event)
        self._colors = colors
        self._indent = indent
        self._exclude_keys = exclude_keys or set()
        self._include_core_in_vertical = include_core_in_vertical

        # Set up color codes if colors are enabled
        if self._colors and colorama:
            self._key_color = colorama.Fore.CYAN
            self._reset = colorama.Style.RESET_ALL
        else:
            self._key_color = ""
            self._reset = ""

    def __call__(
        self,
        logger: structlog.types.WrappedLogger,
        name: str,
        event_dict: structlog.types.EventDict,
    ) -> str:
        """Render the log event with vertical key-value display.

        Args:
            logger: The wrapped logger instance
            name: The name of the logger
            event_dict: The event dictionary to render

        Returns:
            Formatted log string with vertical key-value pairs
        """
        # Create filtered event_dict with only core fields for the main line
        core_event_dict = {k: v for k, v in event_dict.items() if k in self.CORE_FIELDS}

        # Let ConsoleRenderer format the main line (only core fields)
        main_line = self._console(logger, name, core_event_dict)

        # Determine which fields to show vertically
        if self._include_core_in_vertical:
            # Show all fields except explicitly excluded
            extra_fields = {k: v for k, v in event_dict.items() if k not in self._exclude_keys}
        else:
            # Show only non-core fields
            extra_fields = {k: v for k, v in event_dict.items() if k not in self.CORE_FIELDS and k not in self._exclude_keys}

        # If no extra fields, just return the main line
        if not extra_fields:
            return main_line

        # Build vertical key-value pairs
        lines = [main_line]
        for key in sorted(extra_fields.keys()):
            value = extra_fields[key]
            # Format value representation
            if isinstance(value, str):
                formatted_value = value
            elif isinstance(value, (int, float, bool)):
                formatted_value = str(value)
            else:
                formatted_value = repr(value)

            # Format as key=value with optional coloring
            lines.append(f"{self._indent}{self._key_color}{key}{self._reset}={formatted_value}")

        return "\n".join(lines)


if __name__ == "__main__":
    """Demo of VerticalConsoleRenderer."""
    import structlog_opinionated

    print("=== VerticalConsoleRenderer Demo ===\n")

    # Configure with vertical renderer
    from structlog_opinionated import LogConfig
    from structlog_opinionated.vertical_console_renderer import VerticalConsoleRenderer

    config = LogConfig(level="INFO")

    # We'll manually configure to show the difference
    import logging.config
    import sys

    shared_processors: list[structlog.types.Processor] = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.ExtraAdder(),
        structlog.contextvars.merge_contextvars,
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.PATHNAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME,
            ]
        ),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionRenderer(exception_formatter=structlog.tracebacks.ExceptionDictTransformer()),
        structlog.processors.UnicodeDecoder(),
    ]

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "vertical": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        VerticalConsoleRenderer(colors=True, pad_event=40),
                    ],
                    "foreign_pre_chain": shared_processors,
                },
            },
            "handlers": {
                "default": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "vertical",
                    "stream": sys.stdout,
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": "INFO",
                },
            },
        }
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog_opinionated.OpinionatedBoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Demo logging
    logger = structlog_opinionated.get_logger(__name__)

    print("--- Simple log with extra fields ---")
    logger.info("User logged in", user_id=123, session_id="abc-123", ip_address="192.168.1.1")

    print("\n--- Log with many fields ---")
    logger = logger.bind(service="api", version="1.0")
    logger.info(
        "Processing request",
        method="POST",
        path="/api/users",
        status_code=201,
        duration_ms=45.2,
        request_id="req_789",
    )

    print("\n--- Log with context ---")
    with logger.context(operation="database_query"):
        logger.info("Executing query", table="users", rows_affected=10, query_time_ms=23.5)

    print("\n--- Warning with fewer fields ---")
    logger.warning("High memory usage", memory_mb=1024)

    print("\n=== Demo Complete ===")
