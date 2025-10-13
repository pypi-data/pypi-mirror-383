"""
Additional tests to improve code coverage to 90%+.

These tests target specific lines that are currently missing coverage
to ensure we meet the quality gate requirements.
"""

import logging
import os
from typing import Any, Dict
from unittest.mock import patch

import mypylogger
from mypylogger.config import LogConfig
from mypylogger.core import SingletonLogger
from mypylogger.formatters import CustomJsonFormatter
from mypylogger.handlers import (
    ParallelStdoutHandler,
)


class TestInitModuleCoverage:
    """Tests to cover missing lines in __init__.py."""

    def test_module_constants_access(self):
        """Test accessing logging level constants from module."""
        # Missing lines 67, 83 - accessing constants
        assert mypylogger.DEBUG == 10
        assert mypylogger.INFO == 20
        assert mypylogger.WARNING == 30
        assert mypylogger.ERROR == 40
        assert mypylogger.CRITICAL == 50

    def test_get_effective_level_function(self):
        """Test the module-level get_effective_level function."""
        # This should cover line 83
        level = mypylogger.get_effective_level()
        assert isinstance(level, int)
        assert level >= 10  # Should be a valid logging level


class TestConfigCoverage:
    """Tests to cover missing lines in config.py."""

    def test_get_stdout_level_int_method(self):
        """Test the get_stdout_level_int method that's missing coverage."""
        # Lines 128-140 - get_stdout_level_int method
        config = LogConfig(parallel_stdout_logging="DEBUG")
        assert config.get_stdout_level_int() == logging.DEBUG

        config = LogConfig(parallel_stdout_logging="WARNING")
        assert config.get_stdout_level_int() == logging.WARNING

        config = LogConfig(parallel_stdout_logging="INVALID")
        assert config.get_stdout_level_int() == logging.INFO  # Default fallback

        # Test case insensitive
        config = LogConfig(parallel_stdout_logging="debug")
        assert config.get_stdout_level_int() == logging.DEBUG


class TestCoreCoverage:
    """Tests to cover missing lines in core.py."""

    def setup_method(self):
        """Reset singleton for each test."""
        SingletonLogger._instance = None
        SingletonLogger._logger = None
        SingletonLogger._config = None

    def test_exception_handling_in_file_handler_creation(self, clean_environment):
        """Test graceful degradation when file handler creation fails."""
        # Lines 94-96 - exception handling in file handler creation
        os.environ["APP_NAME"] = "test_app"

        with patch("mypylogger.handlers.ImmediateFlushFileHandler") as mock_handler:
            mock_handler.side_effect = Exception("File handler creation failed")

            # Should still create logger without file handler
            logger = SingletonLogger.get_logger()
            assert logger is not None
            assert logger.name == "test_app"

    def test_exception_handling_in_stdout_handler_creation(self, clean_environment):
        """Test graceful degradation when stdout handler creation fails."""
        # Lines 100-110 - exception handling in stdout handler creation
        os.environ["APP_NAME"] = "test_app"
        os.environ["PARALLEL_STDOUT_LOGGING"] = "INFO"

        with patch("mypylogger.handlers.ParallelStdoutHandler") as mock_handler:
            mock_handler.side_effect = Exception("Stdout handler creation failed")

            # Should still create logger without stdout handler
            logger = SingletonLogger.get_logger()
            assert logger is not None
            assert logger.name == "test_app"


class TestFormattersCoverage:
    """Tests to cover missing lines in formatters.py."""

    def test_import_error_fallback(self):
        """Test the fallback when pythonjsonlogger is not available."""
        # Lines 15-23 - import error handling
        # This is already covered by the stub, but let's test it explicitly
        from mypylogger.formatters import jsonlogger

        # Create an instance of the stub formatter
        stub_formatter = jsonlogger.JsonFormatter()
        assert stub_formatter is not None

    def test_formatter_with_no_args_or_fmt(self):
        """Test formatter initialization with default format."""
        # Line 100 - default format creation
        formatter = CustomJsonFormatter()
        assert formatter is not None

    def test_parse_method_with_super_parse(self):
        """Test parse method when super().parse() exists."""
        # Line 122 - super().parse() call
        from mypylogger.formatters import jsonlogger

        formatter = CustomJsonFormatter()

        # Mock the super().parse() method
        with patch.object(
            jsonlogger.JsonFormatter, "parse", return_value=["message", "levelname"]
        ):
            fields = formatter.parse()
            assert "time" in fields
            assert fields[0] == "time"  # time should be first

    def test_add_fields_with_missing_attributes(self):
        """Test add_fields method with missing record attributes."""
        # Line 134 - handling missing pathname
        formatter = CustomJsonFormatter()

        # Create a real LogRecord and remove attributes to test fallback logic
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",  # Empty pathname
            lineno=42,
            msg="test message",
            args=(),
            exc_info=None,
        )
        record.pathname = None  # type: ignore[assignment]
        # Remove filename attribute entirely to test the 'unknown' fallback
        if hasattr(record, "filename"):
            delattr(record, "filename")
        record.funcName = None  # type: ignore[assignment]

        log_record: Dict[str, Any] = {}
        message_dict = {"message": "test"}

        formatter.add_fields(log_record, record, message_dict)

        assert log_record["filename"] == "unknown"
        assert log_record["funcName"] == "unknown"

    def test_add_fields_with_exc_text(self):
        """Test add_fields method with exc_text."""
        # Line 194 - handling exc_text
        formatter = CustomJsonFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="/path/to/file.py",
            lineno=42,
            msg="test message",
            args=(),
            exc_info=None,
        )
        record.exc_text = "Exception text here"

        log_record: Dict[str, Any] = {}
        message_dict = {"message": "test"}

        formatter.add_fields(log_record, record, message_dict)

        assert log_record["exc_info"] == "Exception text here"

    def test_json_serialization_error_fallback(self):
        """Test fallback when JSON serialization fails."""
        # Lines 207-209 - JSON serialization error handling
        formatter = CustomJsonFormatter()

        # Create a real record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="test message",
            args=(),
            exc_info=None,
        )

        # Mock json.dumps to raise an exception on first call, then succeed on fallback
        with patch("mypylogger.formatters.json.dumps") as mock_dumps:
            # First call raises exception, second call (fallback) returns the error JSON
            mock_dumps.side_effect = [
                TypeError("Not serializable"),
                '{"time":"2024-01-01T00:00:00.000Z","levelname":"INFO","message":"JSON formatting error: Not serializable","filename":"file.py","lineno":"42","funcName":"unknown"}',
            ]

            result = formatter.format(record)
            assert "JSON formatting error" in result
            assert "Not serializable" in result


class TestHandlersCoverage:
    """Tests to cover missing lines in handlers.py."""

    def test_parallel_stdout_handler_error_handling(self, temp_log_dir):
        """Test error handling in ParallelStdoutHandler.emit()."""
        # Lines 102-105 - error handling in emit
        handler = ParallelStdoutHandler(logging.INFO)

        # Mock the super().emit() to raise an exception
        with patch.object(logging.StreamHandler, "emit") as mock_emit:
            mock_emit.side_effect = Exception("Emit failed")

            # Mock handleError to verify it's called
            with patch.object(handler, "handleError") as mock_handle_error:
                record = logging.LogRecord(
                    name="test",
                    level=logging.INFO,
                    pathname="test.py",
                    lineno=1,
                    msg="test message",
                    args=(),
                    exc_info=None,
                )

                handler.emit(record)
                mock_handle_error.assert_called_once_with(record)


class TestIntegrationCoverage:
    """Integration tests to cover remaining edge cases."""

    def setup_method(self):
        """Reset singleton for each test."""
        SingletonLogger._instance = None
        SingletonLogger._logger = None
        SingletonLogger._config = None

    def test_complete_logging_workflow_with_all_features(
        self, temp_log_dir, clean_environment
    ):
        """Test complete logging workflow to ensure all code paths are covered."""
        # Set up environment for full feature coverage
        os.environ["APP_NAME"] = "coverage_test"
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["EMPTY_LOG_FILE_ON_RUN"] = "true"
        os.environ["PARALLEL_STDOUT_LOGGING"] = "WARNING"

        # Get logger and test all logging levels
        logger = mypylogger.get_logger()

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # Test effective level
        level = mypylogger.get_effective_level()
        assert level == logging.DEBUG

        # Test constants
        assert mypylogger.DEBUG == 10
        assert mypylogger.INFO == 20
        assert mypylogger.WARNING == 30
        assert mypylogger.ERROR == 40
        assert mypylogger.CRITICAL == 50

    def test_config_edge_cases(self):
        """Test configuration edge cases."""
        # Test empty string handling in from_environment
        with patch.dict(
            os.environ,
            {
                "APP_NAME": "   ",  # Whitespace only
                "LOG_LEVEL": "",  # Empty string
                "PARALLEL_STDOUT_LOGGING": "  ",  # Whitespace only
            },
        ):
            config = LogConfig.from_environment()
            assert config.app_name == "default_app"
            assert config.log_level == "INFO"
            assert config.parallel_stdout_logging == "false"

    def test_formatter_edge_cases(self):
        """Test formatter edge cases."""
        formatter = CustomJsonFormatter()

        # Test with record that has args
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Message with %s %s",
            args=("arg1", "arg2"),
            exc_info=None,
        )

        result = formatter.format(record)
        assert "Message with arg1 arg2" in result
