"""Custom processors for structlog."""

import asyncio

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
