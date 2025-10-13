"""
Tests for the main API functions - get_logger() and related functionality.
"""

import logging

import mypylogger
from mypylogger.core import SingletonLogger


class TestMainAPI:
    """Test the main public API functions."""

    def test_get_logger_returns_logger_instance(self, mock_logger_instance):
        """Test that get_logger() returns a logging.Logger instance."""
        logger = mypylogger.get_logger()
        assert isinstance(logger, logging.Logger)

    def test_get_logger_singleton_behavior(self, mock_logger_instance):
        """Test that get_logger() returns the same instance on multiple calls."""
        logger1 = mypylogger.get_logger()
        logger2 = mypylogger.get_logger()
        assert logger1 is logger2

    def test_get_effective_level_returns_int(self):
        """Test that get_effective_level() returns an integer."""
        level = mypylogger.get_effective_level()
        assert isinstance(level, int)
        assert level >= 0

    def test_logging_constants_available(self):
        """Test that logging level constants are available."""
        assert hasattr(mypylogger, "DEBUG")
        assert hasattr(mypylogger, "INFO")
        assert hasattr(mypylogger, "WARNING")
        assert hasattr(mypylogger, "ERROR")
        assert hasattr(mypylogger, "CRITICAL")

        # Verify they have correct values
        assert mypylogger.DEBUG == logging.DEBUG
        assert mypylogger.INFO == logging.INFO
        assert mypylogger.WARNING == logging.WARNING
        assert mypylogger.ERROR == logging.ERROR
        assert mypylogger.CRITICAL == logging.CRITICAL


class TestSingletonLogger:
    """Test the SingletonLogger class directly."""

    def test_singleton_pattern(self, mock_logger_instance):
        """Test that SingletonLogger follows singleton pattern."""
        instance1 = SingletonLogger()
        instance2 = SingletonLogger()
        assert instance1 is instance2

    def test_get_logger_static_method(self, mock_logger_instance):
        """Test the static get_logger method."""
        logger = SingletonLogger.get_logger()
        assert isinstance(logger, logging.Logger)

    def test_get_effective_level_static_method(self):
        """Test the static get_effective_level method."""
        level = SingletonLogger.get_effective_level()
        assert isinstance(level, int)

    def test_logging_constants_on_class(self):
        """Test that logging constants are available on the class."""
        assert SingletonLogger.DEBUG == logging.DEBUG
        assert SingletonLogger.INFO == logging.INFO
        assert SingletonLogger.WARNING == logging.WARNING
        assert SingletonLogger.ERROR == logging.ERROR
        assert SingletonLogger.CRITICAL == logging.CRITICAL


class TestPackageImports:
    """Test that all expected components can be imported."""

    def test_main_components_importable(self):
        """Test that main components can be imported from package."""
        from mypylogger import (
            CustomJsonFormatter,
            ImmediateFlushFileHandler,
            LogConfig,
            ParallelStdoutHandler,
            SingletonLogger,
        )

        # Verify they are classes/types
        assert SingletonLogger is not None
        assert LogConfig is not None
        assert CustomJsonFormatter is not None
        assert ImmediateFlushFileHandler is not None
        assert ParallelStdoutHandler is not None

    def test_all_exports_defined(self):
        """Test that __all__ contains expected exports."""
        expected_exports = {
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
        }

        assert set(mypylogger.__all__) == expected_exports
