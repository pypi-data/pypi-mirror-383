"""Custom processors for structlog."""

import asyncio
from pathlib import Path

import structlog


def add_asyncio_context(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """Add asyncio task information to log events.

    This processor adds the current asyncio task name and ID to the log event,
    which is useful for tracing logs across async operations.

    Args:
        logger: The wrapped logger instance
        method_name: The name of the method called on the logger
        event_dict: The event dictionary to process

    Returns:
        The event dictionary with asyncio context added
    """
    try:
        task = asyncio.current_task()
        if task is not None:
            event_dict["task_name"] = task.get_name()
            event_dict["task_id"] = id(task)
    except RuntimeError:
        # Not in an async context
        pass

    return event_dict


def combine_callsite(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """Combine pathname and lineno into a single callsite field.

    This processor removes the individual pathname and lineno fields
    and combines them into a single "callsite" field with the format:
    "relative_path:lineno"

    The pathname is converted to a relative path from the current working directory.
    If it cannot be made relative, the absolute path is used as a fallback.

    Args:
        logger: The wrapped logger instance
        method_name: The name of the method called on the logger
        event_dict: The event dictionary to process

    Returns:
        The event dictionary with combined callsite field
    """
    pathname = event_dict.pop("pathname", None)
    lineno = event_dict.pop("lineno", None)

    if pathname is not None and lineno is not None:
        # Convert pathname to relative path from cwd
        try:
            path = Path(pathname)
            cwd = Path.cwd()
            relative_path = path.relative_to(cwd)
            pathname_str = str(relative_path)
        except (ValueError, RuntimeError):
            # If we can't make it relative (e.g., different drive on Windows),
            # fall back to using the pathname as-is
            pathname_str = pathname

        event_dict["callsite"] = f"{pathname_str}:{lineno}"

    return event_dict
