"""Configuration for structlog-opinionated."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogConfig(BaseSettings):
    """Configuration for structured logging.

    All settings can be overridden via environment variables with the
    LOG_ prefix. For example, to set the log level:
        LOG_LEVEL=DEBUG

    For module-specific debug logging, use the nested delimiter:
        LOG_DEBUG__MAIN=1
        LOG_DEBUG__HARNESS_PROCESSOR=1

    Attributes:
        level: Minimum log level (default: "INFO")
        debug: Dictionary mapping module names to debug flags
        force_json: Force JSON output even in TTY/console environments
        force_console: Force console output even in non-TTY environments
        console_vertical_keys: Use vertical console renderer (one key per line) instead of default console renderer
        file_prefix: File prefix for JSONL log files (e.g., /var/log/myapp)
    """

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
        nested_model_default_partial_update=True,
    )

    level: str = Field(
        default="INFO",
        description="Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    debug: dict[str, bool] = Field(
        default_factory=dict,
        description="Module-specific debug logging (e.g., LOG_DEBUG__MAIN=1)",
    )

    force_json: bool = Field(
        default=False,
        description="Force JSON output even in TTY/console environments",
    )

    force_console: bool = Field(
        default=False,
        description="Force console output even in non-TTY environments",
    )

    console_vertical_keys: bool = Field(
        default=True,
        description="Use vertical console renderer (one key per line) instead of default console renderer",
    )

    file_prefix: str | None = Field(
        default=None,
        description="File prefix for JSONL log files. Creates {prefix}_yyyy-mm-dd_hh-mm-ss.jsonl",
    )
