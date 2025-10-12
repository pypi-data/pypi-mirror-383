"""Custom logger class with context manager support."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import structlog


class OpinionatedBoundLogger(structlog.BoundLogger):
    """Custom BoundLogger with enhanced context management.

    This logger extends structlog's BoundLogger to add .context() and .attach()
    methods for managing temporary scoped bindings that are automatically cleaned up.

    Builds on structlog's bound_contextvars() but adds automatic cleanup for mid-block
    context additions via .attach(), providing a complete solution for scoped context
    management with proper nesting and value restoration.

    Context Mechanisms:
        - .bind(**kwargs) - Returns NEW logger with permanent bindings (immutable)
        - .context(**kwargs) - Temporary bindings with auto-cleanup (uses bound_contextvars)
        - .attach(**kwargs) - Attach to current context, cleaned up when .context() exits

    Example:
        ```python
        logger = get_logger(__name__)

        # .bind() returns a NEW logger - reassign the variable!
        logger = logger.bind(service="api", version="1.0")

        # Temporary scoped bindings with auto-cleanup
        with logger.context(request_id="req_123", user_id=42):
            logger.info("Processing request")
            # Log includes: service, version, request_id, user_id

            # Add more context mid-block with .attach()
            logger.attach(endpoint="/users", method="POST")
            logger.info("Processing endpoint")
            # Log includes: service, version, request_id, user_id, endpoint, method

        # request_id, user_id, endpoint, and method all automatically removed
        logger.info("Request completed")
        # Log includes: service, version only

        # Pass logger around - each function can add bindings
        def handle_request(logger, req_id):
            logger = logger.bind(request_id=req_id)  # NEW logger
            with logger.context(status="processing"):
                logger.attach(step="validation")  # Attached to context
                logger.info("Processing")
            return logger
        ```
    """

    @contextmanager
    def context(self, **kwargs: Any) -> Iterator[None]:
        """Temporarily bind context variables with automatic cleanup.

        Context variables are included in all log messages within the with block
        and are automatically removed when exiting. Supports proper nesting.

        Uses structlog's bound_contextvars() internally to handle kwargs binding and
        restoration, then adds additional cleanup for any variables added via .attach()
        during the context block.

        The context is stored in structlog's contextvars (not on the logger instance),
        so you continue to use the same logger variable within the context block.

        Any variables added via .attach() within this context block will also be
        automatically cleaned up when the block exits.

        Args:
            **kwargs: Key-value pairs to temporarily bind

        Usage:
            ```python
            # Request-scoped context
            with logger.context(request_id="req_456", method="POST"):
                logger.info("Processing request")  # Use same logger variable

                # Add more context mid-block
                logger.attach(endpoint="/users")

                await some_async_operation()
                logger.info("Request completed")
            # request_id, method, and endpoint all automatically cleaned up

            # Nested contexts
            with logger.context(operation="outer"):
                logger.info("Outer")  # operation="outer"
                logger.attach(data="A")
                with logger.context(operation="inner", step=1):
                    logger.info("Inner")  # operation="inner", step=1
                    logger.attach(data="B")
                logger.info("Back to outer")  # operation="outer", data="A"
            ```
        """
        # Snapshot the current keys BEFORE entering context
        initial_keys = set(structlog.contextvars.get_contextvars().keys())

        # Use structlog's bound_contextvars to handle kwargs binding/restoration
        with structlog.contextvars.bound_contextvars(**kwargs):
            try:
                yield
            finally:
                # Clean up any keys added via .attach() during the context block
                current_keys = set(structlog.contextvars.get_contextvars().keys())
                attached_keys = current_keys - initial_keys - set(kwargs.keys())
                if attached_keys:
                    structlog.contextvars.unbind_contextvars(*attached_keys)

    def attach(self, **kwargs: Any) -> None:
        """Attach context variables that will be cleaned up with current .context() block.

        Unlike .bind() which returns a NEW logger with permanent bindings,
        .attach() adds variables to the current context (via contextvars) that
        will be automatically cleaned up when the enclosing .context() block exits.

        Can be called multiple times within a context block. Can also be called
        outside a .context() block (behaves like contextvars binding until explicitly
        unbound or cleaned up by a future .context() exit).

        Args:
            **kwargs: Key-value pairs to attach to current context

        Usage:
            ```python
            with logger.context(request_id="req_456"):
                logger.info("Starting request")

                # Attach more context mid-block
                logger.attach(endpoint="/users", method="POST")
                logger.info("Processing")  # Has request_id, endpoint, method

                # Can attach multiple times
                logger.attach(status="validated")
                logger.info("Validated")  # Has all above fields

            # All attached fields automatically cleaned up
            logger.info("After context")  # No request_id, endpoint, method, status

            # Nested contexts
            with logger.context(operation="outer"):
                logger.attach(outer_data="A")
                logger.info("Outer")  # Has operation, outer_data

                with logger.context(operation="inner"):
                    logger.attach(inner_data="B")
                    logger.info("Inner")  # Has operation="inner", inner_data

                logger.info("Back")  # Has operation="outer", outer_data only
            ```
        """
        structlog.contextvars.bind_contextvars(**kwargs)

    def exception(self, event: str | None = None, **kwargs: Any) -> Any:
        """Log an exception with automatic exc_info=True.

        This is a convenience method that automatically includes exception
        information in the log. It's equivalent to calling error() with
        exc_info=True.

        Args:
            event: The log message
            **kwargs: Additional key-value pairs to include

        Usage:
            ```python
            try:
                risky_operation()
            except ValueError:
                logger.exception("Operation failed", operation="risky")
            ```
        """
        # Ensure exc_info is set if not already provided
        if "exc_info" not in kwargs:
            kwargs["exc_info"] = True
        return self.error(event, **kwargs)
