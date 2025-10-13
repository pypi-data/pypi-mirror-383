"""mypylogger - Production-quality Python logging library.

This library provides structured JSON logging with real-time development support
and environment-driven configuration. It's designed for production applications
that need consistent, parseable log output with immediate visibility during development.

Copyright (c) 2024 Stephen Abbot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Example:
    Basic usage:
        >>> import mypylogger
        >>> logger = mypylogger.get_logger()
        >>> logger.info("Application started")

    With environment configuration:
        >>> import os
        >>> os.environ['APP_NAME'] = 'my_app'
        >>> os.environ['LOG_LEVEL'] = 'DEBUG'
        >>> logger = mypylogger.get_logger()
        >>> logger.debug("Debug message")
"""

import logging

from .config import LogConfig
from .core import SingletonLogger
from .formatters import CustomJsonFormatter
from .handlers import ImmediateFlushFileHandler, ParallelStdoutHandler

__version__ = "0.1.5"
__author__ = "Stephen Abbot"


# Public API exports
def get_logger() -> logging.Logger:
    """Get the configured logger instance.

    Returns the singleton logger instance configured with environment variables.
    The logger uses JSON formatting and writes to both file and optionally stdout.

    Returns:
        logging.Logger: Configured logger instance with JSON formatting.

    Example:
        >>> logger = get_logger()
        >>> logger.info("Hello, world!")
        # Outputs JSON to logs/{APP_NAME}_{YYYY_MM_DD}.log
    """
    return SingletonLogger.get_logger()


def get_effective_level() -> int:
    """Get the effective logging level.

    Returns the current logging level as an integer. This reflects the level
    set via the LOG_LEVEL environment variable or the default (INFO).

    Returns:
        int: The effective logging level (e.g., 10 for DEBUG, 20 for INFO).

    Example:
        >>> level = get_effective_level()
        >>> print(f"Current log level: {level}")
        Current log level: 20
    """
    return SingletonLogger.get_effective_level()


# Expose logging constants for convenience
DEBUG = SingletonLogger.DEBUG
INFO = SingletonLogger.INFO
WARNING = SingletonLogger.WARNING
ERROR = SingletonLogger.ERROR
CRITICAL = SingletonLogger.CRITICAL

__all__ = [
    "get_logger",
    "get_effective_level",
    "SingletonLogger",
    "LogConfig",
    "CustomJsonFormatter",
    "ImmediateFlushFileHandler",
    "ParallelStdoutHandler",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]
