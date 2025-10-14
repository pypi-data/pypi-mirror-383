"""Vertical console renderer with colored output and multi-line key-value pairs."""

from __future__ import annotations

from typing import Any, cast

import structlog
from structlog.dev import ConsoleRenderer, KeyValueColumnFormatter, LogLevelColumnFormatter

try:
    import colorama  # type: ignore[import-untyped]
except ImportError:
    colorama = None


class TimeOnlyFormatter:
    """Timestamp formatter that displays only time (no date) for console output.

    Console renderer is used during local development where server runs are typically
    short and do not cross date boundaries, so displaying the date is unnecessary clutter.

    Format: HH:MM:SS.mmm (e.g., "14:23:45.123")
    Millisecond precision (3 digits) is sufficient for local development.

    This formatter follows structlog's ColumnFormatter protocol and wraps a
    KeyValueColumnFormatter to preserve the original timestamp styling.

    Args:
        base_formatter: The original KeyValueColumnFormatter with timestamp styles
    """

    def __init__(self, base_formatter: KeyValueColumnFormatter):
        """Initialize with the base formatter for styling.

        Args:
            base_formatter: KeyValueColumnFormatter with timestamp styling
        """
        self.base_formatter = base_formatter

    def __call__(self, key: str, value: Any) -> str:
        """Format timestamp to show only time portion with millisecond precision.

        Follows structlog's ColumnFormatter protocol: (key, value) -> str

        Args:
            key: The key name (typically "timestamp")
            value: The timestamp string in ISO format

        Returns:
            Formatted time-only string with original styling applied
        """
        # value is expected to be an ISO timestamp like "2025-10-12T12:21:15.690873Z"
        # Extract just the time portion after the 'T'
        timestamp_str = str(value)
        time_part = timestamp_str

        if "T" in timestamp_str:
            # Extract time portion: "12:21:15.690873Z" -> "12:21:15.690873"
            time_part = timestamp_str.split("T")[1].rstrip("Z")
            # Truncate fractional seconds to 3 digits (milliseconds)
            if "." in time_part:
                time_base, fractional = time_part.split(".", 1)
                # Keep only first 3 digits of fractional seconds
                time_part = f"{time_base}.{fractional[:3]}"

        # Use the base formatter to apply styling (returns with trailing space)
        return self.base_formatter(key, time_part)


class AbbreviatedLogLevelColumnFormatter:
    """Log level column formatter that displays 3-character abbreviations.

    Formats log levels as compact 3-character codes for cleaner output:
    - debug -> [DBG]
    - info -> [INF]
    - warning -> [WAR]
    - error -> [ERR]
    - critical -> [CRI]

    Args:
        level_styles: Dictionary mapping level names to ANSI color codes
        reset_style: ANSI reset code to clear styling
    """

    # Standard log level abbreviations (3 characters)
    LEVEL_ABBREVIATIONS = {
        "debug": "DBG",
        "info": "INF",
        "warning": "WAR",
        "error": "ERR",
        "critical": "CRI",
        # Uppercase variants (for compatibility)
        "DEBUG": "DBG",
        "INFO": "INF",
        "WARNING": "WAR",
        "ERROR": "ERR",
        "CRITICAL": "CRI",
    }

    def __init__(
        self,
        level_styles: dict[str, str] | None,
        reset_style: str,
    ):
        self.level_styles = level_styles
        self.reset_style = reset_style if level_styles is not None else ""

    def __call__(self, key: str, value: Any) -> str:
        """Format log level as 3-character abbreviation inside brackets."""
        level = str(value)

        # Get abbreviation (fallback to first 3 chars uppercased if not found)
        abbreviated = self.LEVEL_ABBREVIATIONS.get(level, level[:3].upper() if len(level) >= 3 else level.upper())

        style = "" if self.level_styles is None else self.level_styles.get(level, "")

        return f"[{style}{abbreviated}{self.reset_style}]"


class CallsiteFormatter:
    """Formatter for callsite field that displays it in brackets without key name.

    Format: [relative/path/to/file.py:function:line]
    """

    def __call__(self, key: str, value: Any) -> str:
        """Format callsite value in brackets.

        Args:
            key: The key name (ignored, callsite doesn't show key)
            value: The callsite string

        Returns:
            Callsite value wrapped in brackets: [value]
        """
        return f"[{value}]"


class VerticalKeyValueColumnFormatter:
    """Column formatter that displays key-value pairs below the event message.

    This formatter is designed to be used as the default column formatter
    (with key="") in ConsoleRenderer's columns list. All key-value pairs are
    displayed on separate lines below the main log entry, aligned to a fixed
    column position.

    Args:
        target_column: Column position where key-value pairs start (default: 70)
        logger_name_formatter: Optional formatter for logger_name field
        callsite_formatter: Optional formatter for callsite field
        default_formatter: Optional default formatter for colored key-value pairs
    """

    def __init__(
        self,
        target_column: int = 70,
        logger_name_formatter: KeyValueColumnFormatter | None = None,
        callsite_formatter: CallsiteFormatter | None = None,
        default_formatter: KeyValueColumnFormatter | None = None,
    ):
        self.target_column = target_column
        self.logger_name_formatter = logger_name_formatter
        self.callsite_formatter = callsite_formatter
        self.default_formatter = default_formatter

    def __call__(self, key: str, value: Any) -> str:
        """Format a key-value pair on a new line with column alignment.

        Args:
            key: The key name
            value: The value to format

        Returns:
            Formatted string with newline and column spacing
        """
        # Special handling for logger and logger_name using KeyValueColumnFormatter
        if key in ("logger", "logger_name") and self.logger_name_formatter is not None:
            formatted = self.logger_name_formatter(key, value)
        elif key == "callsite" and self.callsite_formatter is not None:
            # Format callsite with brackets, no key name
            formatted = self.callsite_formatter(key, value)
        elif self.default_formatter is not None:
            # Use the default formatter for colored key-value pairs
            formatted = self.default_formatter(key, value)
        else:
            # Fallback: simple key=value formatting
            if isinstance(value, str):
                formatted_value = value
            elif isinstance(value, (int, float, bool)):
                formatted_value = str(value)
            else:
                formatted_value = repr(value)
            formatted = f"{key}={formatted_value}"

        # All key-value pairs on new lines with column alignment
        return f"\n{' ' * self.target_column}{formatted}"


class VerticalConsoleRenderer(ConsoleRenderer):
    """Console renderer that displays all fields below the event message.

    This renderer extends ConsoleRenderer to display the main log information
    (timestamp, level, event message) on the first line, with all additional
    key-value pairs displayed on separate lines below, aligned to a fixed column.

    The main line shows: timestamp, level, and event message (not padded).
    All additional fields (including logger name) are displayed below,
    each on a separate line, aligned to the same column position.

    Features:
    - Time-only timestamp: HH:MM:SS.mmm (no date for local development)
    - Abbreviated log level: [INF], [WAR], [ERR] (3-character codes)
    - All key-value pairs displayed on separate lines below event
    - Logger name formatted with brackets: [__main__]
    - Callsite formatted with brackets: [path/to/file.py:function:line]
    - Colored output with customizable target column

    Example Output:
        12:34:56.123 [INF] User logged in                [__main__]
                           user_id=123
                           session_id=abc-123
                           [src/api/handler.py:login:42]

    This implementation leverages ConsoleRenderer's column mechanism:
    - Custom TimeOnlyFormatter for compact timestamps
    - Custom AbbreviatedLogLevelColumnFormatter for 3-character log levels
    - Logger name moved to vertical section with special formatting
    - Callsite formatter for bracketed file location
    - Default column uses VerticalKeyValueColumnFormatter for all other fields
    - Inherits exception handling and Rich integration from ConsoleRenderer

    Args:
        colors: Enable colored output (default: True)
        target_column_offset: Offset to add/subtract from auto-computed target column (default: 0)
            The target column is computed as: timestamp_width + level_width + 1 + offset
    """

    def __init__(
        self,
        colors: bool = True,
        target_column_offset: int = 0,
    ):
        """Initialize the vertical console renderer.

        Args:
            colors: Enable colored output
            target_column_offset: Offset to add/subtract from auto-computed target column (default: 0)
        """
        # Store parameters
        self._colors = colors
        self._target_column_offset = target_column_offset

        # Initialize parent ConsoleRenderer with minimal event padding
        # Since we're displaying keys below, we don't need to pad for horizontal alignment
        super().__init__(
            colors=colors,
            pad_event=30,  # Keep some padding for event readability
        )

        # Save the default column formatter for colored key-value pairs
        self._saved_default_formatter = cast(KeyValueColumnFormatter, self._default_column_formatter)

        # Replace the level column formatter with centered version
        # and extract the logger_name_formatter before removing logger columns
        self._logger_name_formatter: KeyValueColumnFormatter | None = None
        timestamp_width = 0
        level_width = 0

        for column in self._columns:
            if column.key == "level":
                # Extract the existing formatter to copy its styles
                # The formatter should be LogLevelColumnFormatter at this point
                existing_formatter = cast(LogLevelColumnFormatter, column.formatter)
                # Create an abbreviated log level formatter with the same styles
                abbreviated_formatter = AbbreviatedLogLevelColumnFormatter(
                    level_styles=existing_formatter.level_styles,
                    reset_style=existing_formatter.reset_style,
                )
                column.formatter = abbreviated_formatter
                # Level width is fixed: [XXX] = 5 characters (3 chars + 2 brackets)
                level_width = 5
            elif column.key == "timestamp":
                # Save the existing KeyValueColumnFormatter to preserve styling
                existing_timestamp_formatter = cast(KeyValueColumnFormatter, column.formatter)
                # Replace with time-only formatter that wraps the existing formatter
                # Time format like "14:23:45.123 " (HH:MM:SS.mmm + space) is 13 chars
                column.formatter = TimeOnlyFormatter(existing_timestamp_formatter)
                timestamp_width = 13
            elif column.key in ("logger", "logger_name"):
                # Save the logger_name formatter before removing the column
                self._logger_name_formatter = cast(KeyValueColumnFormatter, column.formatter)

        # Compute target column: align key-value pairs below where the event message starts
        # This is: timestamp_width + level_width + small indent for visual hierarchy
        self._target_column = timestamp_width + level_width + 1 + self._target_column_offset

        # Keep logger columns on the main line (don't remove them)
        # They will appear after the event message

        # Disable key sorting to preserve the order we specify in event_dict
        self._sort_keys = False

        # Create the vertical formatter once - no need to recreate per log entry
        # since we no longer track _is_first_key state
        self._vertical_formatter = VerticalKeyValueColumnFormatter(
            target_column=self._target_column,
            logger_name_formatter=None,  # Logger is on main line now
            callsite_formatter=CallsiteFormatter(),
            default_formatter=self._saved_default_formatter,
        )

        # Set it as the default column formatter
        self._default_column_formatter = self._vertical_formatter

    def __call__(
        self,
        logger: structlog.types.WrappedLogger,
        name: str,
        event_dict: structlog.types.EventDict,
    ) -> str:
        """Render the log event with key-value pairs displayed below.

        Args:
            logger: The wrapped logger instance
            name: The name of the logger
            event_dict: The event dictionary to render

        Returns:
            Formatted log string with key-value pairs below the event
        """
        # Truncate long event messages and add full_event
        if "event" in event_dict and isinstance(event_dict["event"], str):
            event_text = event_dict["event"]
            if len(event_text) > 30:
                event_dict = dict(event_dict)  # Make a mutable copy
                event_dict["event"] = event_text[:27] + "..."
                event_dict["full_event"] = event_text

        # Reorder event_dict to put full_event first, then other keys, then callsite last
        reordered_dict: structlog.types.EventDict = {}

        # Add full_event first if it exists
        if "full_event" in event_dict:
            reordered_dict["full_event"] = event_dict["full_event"]

        # Add all other keys (including logger/logger_name which will appear on main line)
        for key, value in event_dict.items():
            if key not in ("callsite", "full_event"):
                reordered_dict[key] = value

        # Add callsite last in vertical section
        if "callsite" in event_dict:
            reordered_dict["callsite"] = event_dict["callsite"]

        # Call parent's __call__ to do the actual rendering with reordered dict
        result = super().__call__(logger, name, reordered_dict)

        # Add a blank line after each log entry
        return result + "\n"
