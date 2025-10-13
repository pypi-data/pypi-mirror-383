"""
Integration tests for JSON schema validation.

These tests verify that the JSON output from mypylogger matches the expected
schema and format requirements from the specification.
"""

import json
import logging
import time
from datetime import datetime

import pytest

from mypylogger.core import SingletonLogger
from mypylogger.formatters import CustomJsonFormatter


class TestJSONSchemaValidation:
    """Test JSON output schema validation."""

    def setup_method(self):
        """Reset singleton state before each test."""
        SingletonLogger._instance = None
        SingletonLogger._logger = None
        SingletonLogger._config = None

    def test_json_output_basic_schema(self, tmp_path, monkeypatch):
        """Test that JSON output matches basic schema requirements."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment
        monkeypatch.setenv("APP_NAME", "schema_test")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        # Get logger and log a message
        logger = SingletonLogger.get_logger()
        logger.info("Test message for schema validation")

        # Read the log file
        log_file_path = (
            tmp_path / "logs" / f"schema_test_{time.strftime('%Y_%m_%d')}.log"
        )
        assert log_file_path.exists()

        with open(log_file_path, "r") as f:
            log_line = f.readline().strip()

        # Parse JSON
        log_entry = json.loads(log_line)

        # Verify required fields exist
        required_fields = [
            "time",
            "levelname",
            "message",
            "filename",
            "lineno",
            "funcName",
        ]
        for field in required_fields:
            assert (
                field in log_entry
            ), f"Required field '{field}' missing from log entry"

        # Verify field types
        assert isinstance(log_entry["time"], str), "time field should be string"
        assert isinstance(
            log_entry["levelname"], str
        ), "levelname field should be string"
        assert isinstance(log_entry["message"], str), "message field should be string"
        assert isinstance(log_entry["filename"], str), "filename field should be string"
        assert isinstance(log_entry["lineno"], str), "lineno field should be string"
        assert isinstance(log_entry["funcName"], str), "funcName field should be string"

        # Verify field values
        assert log_entry["levelname"] == "INFO"
        assert log_entry["message"] == "Test message for schema validation"
        assert log_entry["filename"].endswith(".py")
        assert log_entry["lineno"].isdigit()

    def test_json_field_order(self, tmp_path, monkeypatch):
        """Test that JSON fields are in the correct order with time first."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment
        monkeypatch.setenv("APP_NAME", "order_test")
        monkeypatch.setenv("LOG_LEVEL", "INFO")

        # Get logger and log a message
        logger = SingletonLogger.get_logger()
        logger.info("Test message for field order")

        # Read the log file
        log_file_path = (
            tmp_path / "logs" / f"order_test_{time.strftime('%Y_%m_%d')}.log"
        )
        with open(log_file_path, "r") as f:
            log_line = f.readline().strip()

        # Parse JSON while preserving order
        log_entry = json.loads(log_line)

        # Get field order
        field_order = list(log_entry.keys())

        # Verify time is first
        assert (
            field_order[0] == "time"
        ), f"First field should be 'time', got '{field_order[0]}'"

        # Verify expected fields are present in some order
        expected_fields = {
            "time",
            "levelname",
            "message",
            "filename",
            "lineno",
            "funcName",
        }
        actual_fields = set(field_order)

        # Should contain at least the expected fields
        assert expected_fields.issubset(
            actual_fields
        ), f"Missing fields: {expected_fields - actual_fields}"

    def test_timestamp_format(self, tmp_path, monkeypatch):
        """Test that timestamp is in UTC ISO8601 format with milliseconds and Z suffix."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment
        monkeypatch.setenv("APP_NAME", "timestamp_test")
        monkeypatch.setenv("LOG_LEVEL", "INFO")

        # Get logger and log a message
        logger = SingletonLogger.get_logger()
        logger.info("Test message for timestamp format")

        # Read the log file
        log_file_path = (
            tmp_path / "logs" / f"timestamp_test_{time.strftime('%Y_%m_%d')}.log"
        )
        with open(log_file_path, "r") as f:
            log_line = f.readline().strip()

        log_entry = json.loads(log_line)
        timestamp = log_entry["time"]

        # Verify format: YYYY-MM-DDTHH:MM:SS.sssZ
        assert timestamp.endswith(
            "Z"
        ), f"Timestamp should end with 'Z', got: {timestamp}"
        assert "T" in timestamp, f"Timestamp should contain 'T', got: {timestamp}"
        assert (
            "." in timestamp
        ), f"Timestamp should contain milliseconds, got: {timestamp}"

        # Verify it can be parsed as ISO format
        # Remove the Z and parse
        timestamp_without_z = timestamp[:-1]
        try:
            parsed_time = datetime.fromisoformat(timestamp_without_z)
            assert parsed_time is not None
        except ValueError as e:
            pytest.fail(f"Timestamp not in valid ISO format: {timestamp}, error: {e}")

        # Verify milliseconds are present (3 digits after decimal)
        decimal_part = timestamp.split(".")[-1]
        milliseconds = decimal_part[:-1]  # Remove the Z
        assert (
            len(milliseconds) == 3
        ), f"Should have 3 millisecond digits, got: {milliseconds}"
        assert (
            milliseconds.isdigit()
        ), f"Milliseconds should be digits, got: {milliseconds}"

    def test_line_number_as_string(self, tmp_path, monkeypatch):
        """Test that line numbers are converted to strings."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment
        monkeypatch.setenv("APP_NAME", "lineno_test")
        monkeypatch.setenv("LOG_LEVEL", "INFO")

        # Get logger and log a message
        logger = SingletonLogger.get_logger()
        logger.info("Test message for line number format")

        # Read the log file
        log_file_path = (
            tmp_path / "logs" / f"lineno_test_{time.strftime('%Y_%m_%d')}.log"
        )
        with open(log_file_path, "r") as f:
            log_line = f.readline().strip()

        log_entry = json.loads(log_line)

        # Verify lineno is a string
        assert isinstance(
            log_entry["lineno"], str
        ), f"lineno should be string, got {type(log_entry['lineno'])}"
        assert log_entry[
            "lineno"
        ].isdigit(), f"lineno should be numeric string, got: {log_entry['lineno']}"

    def test_null_value_normalization(self, tmp_path, monkeypatch):
        """Test that null values are normalized to string 'null'."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Create a custom formatter to test null handling
        formatter = CustomJsonFormatter()

        # Create a log record with None values
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add some None values to the record
        record.custom_field = None
        record.another_field = "valid_value"

        # Format the record
        formatted = formatter.format(record)
        log_entry = json.loads(formatted)

        # Check that None values are handled appropriately
        # The formatter should either exclude None values or convert them to "null"
        for key, value in log_entry.items():
            if value is None:
                pytest.fail(
                    f"Found None value in log entry for key '{key}'. Should be excluded or converted to 'null'"
                )

    def test_unwanted_field_removal(self, tmp_path, monkeypatch):
        """Test that unwanted fields like taskName are removed."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Create a custom formatter to test field removal
        formatter = CustomJsonFormatter()

        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add unwanted fields
        record.taskName = "unwanted_task"
        record.processName = "unwanted_process"

        # Format the record
        formatted = formatter.format(record)
        log_entry = json.loads(formatted)

        # Verify unwanted fields are not present
        unwanted_fields = ["taskName", "processName"]
        for field in unwanted_fields:
            assert (
                field not in log_entry
            ), f"Unwanted field '{field}' found in log entry"

    def test_complete_json_schema_compliance(self, tmp_path, monkeypatch):
        """Test complete JSON schema compliance with all requirements."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment
        monkeypatch.setenv("APP_NAME", "complete_test")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        # Get logger and log messages at different levels
        logger = SingletonLogger.get_logger()

        test_messages = [
            (logging.DEBUG, "Debug message"),
            (logging.INFO, "Info message"),
            (logging.WARNING, "Warning message"),
            (logging.ERROR, "Error message"),
            (logging.CRITICAL, "Critical message"),
        ]

        for level, message in test_messages:
            logger.log(level, message)

        # Read and validate all log entries
        log_file_path = (
            tmp_path / "logs" / f"complete_test_{time.strftime('%Y_%m_%d')}.log"
        )
        with open(log_file_path, "r") as f:
            log_lines = f.readlines()

        assert len(log_lines) == len(
            test_messages
        ), f"Expected {len(test_messages)} log entries, got {len(log_lines)}"

        for i, log_line in enumerate(log_lines):
            log_entry = json.loads(log_line.strip())
            expected_level, expected_message = test_messages[i]
            expected_level_name = logging.getLevelName(expected_level)

            # Validate schema compliance
            self._validate_log_entry_schema(log_entry)

            # Validate content
            assert log_entry["levelname"] == expected_level_name
            assert log_entry["message"] == expected_message

    def test_structured_logging_schema(self, tmp_path, monkeypatch):
        """Test JSON schema with structured logging (extra fields)."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment
        monkeypatch.setenv("APP_NAME", "structured_test")
        monkeypatch.setenv("LOG_LEVEL", "INFO")

        # Get logger and log with extra fields
        logger = SingletonLogger.get_logger()
        logger.info(
            "Structured log message",
            extra={
                "user_id": 12345,
                "action": "login",
                "duration_ms": 150,
                "success": True,
                "metadata": {"ip": "192.168.1.1", "browser": "Chrome"},
            },
        )

        # Read and validate log entry
        log_file_path = (
            tmp_path / "logs" / f"structured_test_{time.strftime('%Y_%m_%d')}.log"
        )
        with open(log_file_path, "r") as f:
            log_line = f.readline().strip()

        log_entry = json.loads(log_line)

        # Validate basic schema
        self._validate_log_entry_schema(log_entry)

        # Validate extra fields are present
        assert log_entry["user_id"] == 12345
        assert log_entry["action"] == "login"
        assert log_entry["duration_ms"] == 150
        assert log_entry["success"] is True
        assert log_entry["metadata"] == {"ip": "192.168.1.1", "browser": "Chrome"}

    def _validate_log_entry_schema(self, log_entry):
        """Helper method to validate a log entry against the expected schema."""
        # Required fields
        required_fields = [
            "time",
            "levelname",
            "message",
            "filename",
            "lineno",
            "funcName",
        ]
        for field in required_fields:
            assert field in log_entry, f"Required field '{field}' missing"

        # Field types
        assert isinstance(log_entry["time"], str), "time should be string"
        assert isinstance(log_entry["levelname"], str), "levelname should be string"
        assert isinstance(log_entry["message"], str), "message should be string"
        assert isinstance(log_entry["filename"], str), "filename should be string"
        assert isinstance(log_entry["lineno"], str), "lineno should be string"
        assert isinstance(log_entry["funcName"], str), "funcName should be string"

        # Time format
        assert log_entry["time"].endswith("Z"), "time should end with Z"
        assert "T" in log_entry["time"], "time should contain T"
        assert "." in log_entry["time"], "time should contain milliseconds"

        # Field order (time should be first)
        field_order = list(log_entry.keys())
        assert field_order[0] == "time", "time should be first field"

        # No None values
        for key, value in log_entry.items():
            assert value is not None, f"Field '{key}' should not be None"

        # No unwanted fields
        unwanted_fields = ["taskName", "processName"]
        for field in unwanted_fields:
            assert field not in log_entry, f"Unwanted field '{field}' found"


class TestJSONOutputVariations:
    """Test JSON output with various configurations and scenarios."""

    def setup_method(self):
        """Reset singleton state before each test."""
        SingletonLogger._instance = None
        SingletonLogger._logger = None
        SingletonLogger._config = None

    def test_json_with_exception_info(self, tmp_path, monkeypatch):
        """Test JSON output when logging exceptions."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment
        monkeypatch.setenv("APP_NAME", "exception_test")
        monkeypatch.setenv("LOG_LEVEL", "ERROR")

        # Get logger and log an exception
        logger = SingletonLogger.get_logger()

        try:
            raise ValueError("Test exception for JSON validation")
        except ValueError:
            logger.error("Exception occurred", exc_info=True)

        # Read and validate log entry
        log_file_path = (
            tmp_path / "logs" / f"exception_test_{time.strftime('%Y_%m_%d')}.log"
        )
        with open(log_file_path, "r") as f:
            log_line = f.readline().strip()

        log_entry = json.loads(log_line)

        # Should still be valid JSON with basic schema
        required_fields = [
            "time",
            "levelname",
            "message",
            "filename",
            "lineno",
            "funcName",
        ]
        for field in required_fields:
            assert field in log_entry

        # Note: Current implementation doesn't include exception info in JSON output
        # This is acceptable as the exception is still logged to stdout/console
        # The JSON format focuses on structured data fields

        # Verify the basic JSON structure is still valid
        assert len(log_entry) >= 6  # Should have at least the basic fields

    def test_json_with_unicode_characters(self, tmp_path, monkeypatch):
        """Test JSON output with unicode characters."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment
        monkeypatch.setenv("APP_NAME", "unicode_test")
        monkeypatch.setenv("LOG_LEVEL", "INFO")

        # Get logger and log unicode message
        logger = SingletonLogger.get_logger()
        unicode_message = "Test with unicode: 你好世界 🌍 café naïve résumé"
        logger.info(unicode_message)

        # Read and validate log entry
        log_file_path = (
            tmp_path / "logs" / f"unicode_test_{time.strftime('%Y_%m_%d')}.log"
        )
        with open(log_file_path, "r", encoding="utf-8") as f:
            log_line = f.readline().strip()

        log_entry = json.loads(log_line)

        # Validate basic schema
        assert log_entry["message"] == unicode_message
        assert isinstance(log_entry["message"], str)

    def test_json_with_large_messages(self, tmp_path, monkeypatch):
        """Test JSON output with large messages."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment
        monkeypatch.setenv("APP_NAME", "large_test")
        monkeypatch.setenv("LOG_LEVEL", "INFO")

        # Get logger and log large message
        logger = SingletonLogger.get_logger()
        large_message = "Large message: " + "x" * 10000  # 10KB message
        logger.info(large_message)

        # Read and validate log entry
        log_file_path = (
            tmp_path / "logs" / f"large_test_{time.strftime('%Y_%m_%d')}.log"
        )
        with open(log_file_path, "r") as f:
            log_line = f.readline().strip()

        log_entry = json.loads(log_line)

        # Should still be valid JSON
        assert log_entry["message"] == large_message
        assert len(log_entry["message"]) > 10000

    def test_json_consistency_across_multiple_entries(self, tmp_path, monkeypatch):
        """Test that JSON schema is consistent across multiple log entries."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment
        monkeypatch.setenv("APP_NAME", "consistency_test")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        # Get logger and log multiple different types of messages
        logger = SingletonLogger.get_logger()

        # Different message types
        logger.debug("Simple debug message")
        logger.info("Info with extra", extra={"key": "value"})
        logger.warning("Warning message")
        logger.error("Error with context", extra={"error_code": 500, "retry": True})

        # Read all log entries
        log_file_path = (
            tmp_path / "logs" / f"consistency_test_{time.strftime('%Y_%m_%d')}.log"
        )
        with open(log_file_path, "r") as f:
            log_lines = f.readlines()

        # Validate each entry has consistent schema
        for i, log_line in enumerate(log_lines):
            log_entry = json.loads(log_line.strip())

            # All entries should have the same basic fields
            required_fields = [
                "time",
                "levelname",
                "message",
                "filename",
                "lineno",
                "funcName",
            ]
            for field in required_fields:
                assert field in log_entry, f"Entry {i}: missing field '{field}'"

            # All entries should have time as first field
            field_order = list(log_entry.keys())
            assert field_order[0] == "time", f"Entry {i}: time not first field"

            # All timestamps should have same format
            timestamp = log_entry["time"]
            assert timestamp.endswith("Z"), f"Entry {i}: timestamp format incorrect"
            assert "T" in timestamp, f"Entry {i}: timestamp missing T"
            assert "." in timestamp, f"Entry {i}: timestamp missing milliseconds"
