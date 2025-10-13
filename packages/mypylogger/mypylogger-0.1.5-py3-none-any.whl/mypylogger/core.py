"""
Copyright (c) 2024 Stephen Abbot. Licensed under MIT License.

Core singleton logger implementation.
"""

import logging
import threading
from typing import Optional

from .config import LogConfig


class SingletonLogger:
    """Singleton logger class that provides consistent logging configuration.

    This class implements the singleton pattern to ensure that all parts of an
    application use the same logger configuration. It automatically configures
    JSON formatting, file output, and optional stdout output based on environment
    variables.

    The logger is thread-safe and uses double-checked locking to ensure proper
    initialization in multi-threaded environments.

    Attributes:
        DEBUG (int): Debug logging level constant (10).
        INFO (int): Info logging level constant (20).
        WARNING (int): Warning logging level constant (30).
        ERROR (int): Error logging level constant (40).
        CRITICAL (int): Critical logging level constant (50).
    """

    _instance: Optional["SingletonLogger"] = None
    _logger: Optional[logging.Logger] = None
    _config: Optional[LogConfig] = None
    _lock = threading.Lock()

    def __new__(cls) -> "SingletonLogger":
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get the configured logger instance.

        Returns the singleton logger instance, initializing it if necessary.
        The logger is configured with JSON formatting, file output to the logs/
        directory, and optional stdout output based on environment variables.

        Returns:
            logging.Logger: The configured logger instance.

        Example:
            >>> logger = SingletonLogger.get_logger()
            >>> logger.info("Application started")
        """
        if cls._logger is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._logger is None:
                    cls._initialize_logger()
        if cls._logger is None:
            raise RuntimeError("Logger initialization failed")
        return cls._logger

    @classmethod
    def _initialize_logger(cls) -> None:
        """Initialize the logger with configuration."""
        from .formatters import CustomJsonFormatter

        # Get configuration from environment
        cls._config = LogConfig.from_environment()

        # Create logger with app name
        cls._logger = logging.getLogger(cls._config.app_name)

        # Set the logging level
        cls._logger.setLevel(cls._config.get_log_level_int())

        # Prevent adding duplicate handlers
        if not cls._logger.handlers:
            # Create JSON formatter
            formatter = CustomJsonFormatter()

            # Add file handler
            cls._add_file_handler(formatter)

            # Add stdout handler if enabled
            cls._add_stdout_handler()

    @classmethod
    def _add_file_handler(cls, formatter: logging.Formatter) -> None:
        """Add file handler with error handling."""
        try:
            from .handlers import ImmediateFlushFileHandler, get_log_file_path

            if cls._config is None:
                raise RuntimeError("Config must be initialized")
            if cls._logger is None:
                raise RuntimeError("Logger must be initialized")

            log_file_path = get_log_file_path(cls._config.app_name)
            file_mode = "w" if cls._config.empty_log_file_on_run else "a"
            file_handler = ImmediateFlushFileHandler(log_file_path, mode=file_mode)
            file_handler.setFormatter(formatter)
            cls._logger.addHandler(file_handler)
        except Exception as e:
            cls._handle_file_handler_error(e)

    @classmethod
    def _add_stdout_handler(cls) -> None:
        """Add stdout handler with error handling."""
        if cls._config is None:
            raise RuntimeError("Config must be initialized")
        if cls._logger is None:
            raise RuntimeError("Logger must be initialized")

        if cls._config.parallel_stdout_logging.lower() != "false":
            try:
                from .handlers import ParallelStdoutHandler

                # Parse stdout logging level
                stdout_level = cls._config.get_stdout_level_int()
                stdout_handler = ParallelStdoutHandler(stdout_level)
                # Use simple formatter for stdout (not JSON)
                stdout_formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                stdout_handler.setFormatter(stdout_formatter)
                cls._logger.addHandler(stdout_handler)
            except Exception as e:
                cls._handle_stdout_handler_error(e)

    @classmethod
    def _handle_file_handler_error(cls, error: Exception) -> None:
        """Handle file handler creation errors with graceful degradation."""
        import sys

        print(f"Warning: Failed to create file handler: {error}", file=sys.stderr)

    @classmethod
    def _handle_stdout_handler_error(cls, error: Exception) -> None:
        """Handle stdout handler creation errors with graceful degradation."""
        import sys

        print(f"Warning: Failed to create stdout handler: {error}", file=sys.stderr)

    @classmethod
    def get_effective_level(cls) -> int:
        """Get the effective logging level.

        Returns the current effective logging level of the configured logger.
        This reflects the level set via the LOG_LEVEL environment variable.

        Returns:
            int: The effective logging level (e.g., 10 for DEBUG, 20 for INFO).

        Example:
            >>> level = SingletonLogger.get_effective_level()
            >>> if level <= logging.DEBUG:
            ...     print("Debug logging is enabled")
        """
        logger = cls.get_logger()
        return logger.getEffectiveLevel()

    # Expose logging constants
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
