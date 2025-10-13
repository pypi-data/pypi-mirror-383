"""
Copyright (c) 2024 Stephen Abbot. Licensed under MIT License.

Custom logging handlers for file and stdout output.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_log_file_path(app_name: str, logs_dir: str = "logs") -> str:
    """Generate log file path with format: {logs_dir}/{APP_NAME}_{YYYY_MM_DD}.log.

    Creates a standardized log file path using the application name and current date.
    This ensures log files are organized by date and application.

    Args:
        app_name (str): Application name for the log file prefix.
        logs_dir (str, optional): Directory where log files should be stored.
            Defaults to "logs".

    Returns:
        str: Full path to the log file.

    Example:
        >>> path = get_log_file_path("my_app")
        >>> print(path)
        logs/my_app_2024_01_15.log
    """
    today = datetime.now().strftime("%Y_%m_%d")
    filename = f"{app_name}_{today}.log"
    return str(Path(logs_dir) / filename)


class ImmediateFlushFileHandler(logging.FileHandler):
    """File handler that flushes immediately after each log entry.

    This handler extends the standard FileHandler to provide immediate flushing
    of log entries to disk. This ensures real-time visibility of log entries,
    which is especially useful during development and debugging.

    The handler automatically creates the log directory if it doesn't exist.
    """

    def __init__(self, filename: str, mode: str = "a", encoding: Optional[str] = None):
        # Create directory if it doesn't exist
        log_path = Path(filename)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        super().__init__(filename, mode, encoding)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record with immediate flush.

        Writes the log record to the file and immediately flushes the buffer
        to ensure the log entry is visible on disk without waiting for the
        buffer to fill or the program to exit.

        Args:
            record (logging.LogRecord): The log record to emit.
        """
        super().emit(record)
        # Flush immediately after each log entry for real-time visibility
        self.flush()


class ParallelStdoutHandler(logging.StreamHandler):
    """Handler that outputs to stdout with level filtering.

    This handler provides optional stdout output alongside file logging.
    It filters messages based on a minimum log level, allowing different
    verbosity levels for console vs file output.

    Unlike the file handler, this uses a simple text format rather than JSON
    for better readability in the console.
    """

    def __init__(self, stdout_level: int = logging.INFO):
        """
        Initialize the stdout handler with level filtering.

        Args:
            stdout_level: Minimum log level to output to stdout (default: INFO)
        """
        super().__init__(sys.stdout)
        self.stdout_level = stdout_level

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to stdout if level is appropriate.

        Args:
            record: The log record to emit
        """
        # Only emit if the record level is at or above our threshold
        if record.levelno >= self.stdout_level:
            try:
                super().emit(record)
            except Exception:
                # Handle any errors during emission gracefully
                # This prevents stdout logging errors from breaking the application
                self.handleError(record)
