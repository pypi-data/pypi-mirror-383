"""structlog-opinionated: Opinionated structlog configuration for asyncio servers.

This package provides a pre-configured setup for structlog that's optimized
for long-running asyncio servers with sensible defaults and best practices.

Quick Start:
    ```python
    import structlog_opinionated

    # Setup with defaults
    structlog_opinionated.setup()

    # Get a logger instance
    logger = structlog_opinionated.get_logger(__name__)

    # .bind() returns NEW logger - must reassign!
    logger = logger.bind(service="api", version="1.0")

    # Temporary scoped bindings with auto-cleanup
    with logger.context(request_id="req_123", user_id=42):
        logger.info("Processing request", action="create")
        # Includes: service, version, request_id, user_id, action
    # request_id and user_id automatically removed

    logger.info("Done")
    # Includes: service, version only
    ```
"""

from .config import LogConfig
from .opinionated_bound_logger import OpinionatedBoundLogger
from .setup import get_logger, setup
from .vertical_console_renderer import VerticalConsoleRenderer

__version__ = "0.1.5"

__all__ = [
    "LogConfig",
    "OpinionatedBoundLogger",
    "VerticalConsoleRenderer",
    "setup",
    "get_logger",
    "__version__",
]
