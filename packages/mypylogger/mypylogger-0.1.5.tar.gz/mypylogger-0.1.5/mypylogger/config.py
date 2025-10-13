"""
Copyright (c) 2024 Stephen Abbot. Licensed under MIT License.

Configuration management for environment-driven logging setup.
"""

import logging
import os
from dataclasses import dataclass


@dataclass
class LogConfig:
    """Configuration class for logging settings.

    This class holds all configuration options for the logging system, with
    values typically loaded from environment variables. It provides methods
    to parse and validate configuration values.

    Attributes:
        app_name (str): Application name used for logger naming and file prefixes.
            Defaults to "default_app".
        log_level (str): Logging level as string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            Defaults to "INFO".
        empty_log_file_on_run (bool): Whether to truncate log file on startup.
            Defaults to False.
        parallel_stdout_logging (str): Stdout logging configuration. Can be "false"
            to disable, or a log level string to enable with that minimum level.
            Defaults to "false".
    """

    app_name: str = "default_app"
    log_level: str = "INFO"
    empty_log_file_on_run: bool = False
    parallel_stdout_logging: str = "false"

    @classmethod
    def from_environment(cls) -> "LogConfig":
        """Create configuration from environment variables.

        Reads configuration from the following environment variables:
        - APP_NAME: Application name (default: "default_app")
        - LOG_LEVEL: Logging level (default: "INFO")
        - EMPTY_LOG_FILE_ON_RUN: Whether to truncate log file (default: "false")
        - PARALLEL_STDOUT_LOGGING: Stdout logging level or "false" (default: "false")

        Returns:
            LogConfig: Configuration instance with values from environment or defaults.

        Example:
            >>> import os
            >>> os.environ['APP_NAME'] = 'my_app'
            >>> os.environ['LOG_LEVEL'] = 'DEBUG'
            >>> config = LogConfig.from_environment()
            >>> print(config.app_name)
            my_app
        """
        app_name = os.environ.get("APP_NAME", "default_app")
        log_level = os.environ.get("LOG_LEVEL", "INFO")
        empty_log_file_on_run = cls._parse_boolean(
            os.environ.get("EMPTY_LOG_FILE_ON_RUN", "false")
        )
        parallel_stdout_logging = os.environ.get("PARALLEL_STDOUT_LOGGING", "false")

        # Handle empty strings by using defaults
        if not app_name.strip():
            app_name = "default_app"
        if not log_level.strip():
            log_level = "INFO"
        if not parallel_stdout_logging.strip():
            parallel_stdout_logging = "false"

        return cls(
            app_name=app_name,
            log_level=log_level,
            empty_log_file_on_run=empty_log_file_on_run,
            parallel_stdout_logging=parallel_stdout_logging,
        )

    @staticmethod
    def _parse_boolean(value: str) -> bool:
        """Parse string value to boolean."""
        if not value:
            return False
        return value.lower() in ("true", "1", "yes")

    def get_log_level_int(self) -> int:
        """Convert string log level to integer.

        Converts the log_level string to the corresponding logging module integer.
        Invalid levels default to INFO (20).

        Returns:
            int: Logging level integer (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL).

        Example:
            >>> config = LogConfig(log_level="DEBUG")
            >>> level = config.get_log_level_int()
            >>> print(level)
            10
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        # Convert to uppercase for case-insensitive matching
        level_upper = self.log_level.upper()

        # Return the mapped level or default to INFO if invalid
        return level_map.get(level_upper, logging.INFO)

    def get_stdout_level_int(self) -> int:
        """Convert stdout logging level string to integer.

        Converts the parallel_stdout_logging string to the corresponding logging
        module integer. Invalid levels default to INFO (20).

        Returns:
            int: Logging level integer for stdout output.

        Example:
            >>> config = LogConfig(parallel_stdout_logging="WARNING")
            >>> level = config.get_stdout_level_int()
            >>> print(level)
            30
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        # Convert to uppercase for case-insensitive matching
        level_upper = self.parallel_stdout_logging.upper()

        # Return the mapped level or default to INFO if invalid
        return level_map.get(level_upper, logging.INFO)
