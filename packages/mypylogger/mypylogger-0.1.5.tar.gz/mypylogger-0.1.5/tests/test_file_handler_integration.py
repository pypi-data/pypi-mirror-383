"""
Integration tests for file handler functionality.
"""

import logging
import os
from datetime import datetime
from pathlib import Path

from mypylogger.config import LogConfig
from mypylogger.handlers import ImmediateFlushFileHandler, get_log_file_path


class TestFileHandlerIntegration:
    """Integration tests for file handler with configuration."""

    def test_get_log_file_path_format(self):
        """Test that get_log_file_path generates correct format."""
        app_name = "test_app"
        expected_date = datetime.now().strftime("%Y_%m_%d")
        expected_filename = f"{app_name}_{expected_date}.log"

        result = get_log_file_path(app_name)

        expected_path = os.path.join("logs", expected_filename)
        assert result == expected_path

    def test_get_log_file_path_custom_directory(self):
        """Test that get_log_file_path works with custom directory."""
        app_name = "test_app"
        custom_dir = "custom_logs"
        expected_date = datetime.now().strftime("%Y_%m_%d")
        expected_filename = f"{app_name}_{expected_date}.log"

        result = get_log_file_path(app_name, custom_dir)

        expected_path = os.path.join(custom_dir, expected_filename)
        assert result == expected_path

    def test_file_handler_with_config_integration(self, tmp_path, monkeypatch):
        """Test file handler integration with configuration."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment variables
        monkeypatch.setenv("APP_NAME", "integration_test")
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv("EMPTY_LOG_FILE_ON_RUN", "false")

        # Create configuration
        config = LogConfig.from_environment()

        # Generate log file path
        log_file_path = get_log_file_path(config.app_name)

        # Create handler
        handler = ImmediateFlushFileHandler(log_file_path)

        # Verify logs directory was created
        logs_dir = Path("logs")
        assert logs_dir.exists()
        assert logs_dir.is_dir()

        # Verify log file was created with correct name
        expected_date = datetime.now().strftime("%Y_%m_%d")
        expected_filename = f"integration_test_{expected_date}.log"
        log_file = logs_dir / expected_filename
        assert log_file.exists()

        # Test logging
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Integration test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        # Verify content was written and flushed
        content = log_file.read_text()
        assert "Integration test message" in content

        handler.close()

    def test_file_truncation_with_config(self, tmp_path, monkeypatch):
        """Test file truncation behavior with configuration."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment for truncation
        monkeypatch.setenv("APP_NAME", "truncate_test")
        monkeypatch.setenv("EMPTY_LOG_FILE_ON_RUN", "true")

        config = LogConfig.from_environment()
        log_file_path = get_log_file_path(config.app_name)

        # Create logs directory and file with existing content
        logs_dir = Path("logs")
        logs_dir.mkdir()
        log_file = Path(log_file_path)
        log_file.write_text("Existing content\n")

        # Create handler with truncation mode based on config
        mode = "w" if config.empty_log_file_on_run else "a"
        handler = ImmediateFlushFileHandler(log_file_path, mode=mode)

        # File should be empty after handler creation (truncated)
        handler.close()
        assert log_file.read_text() == ""

    def test_file_append_with_config(self, tmp_path, monkeypatch):
        """Test file append behavior with configuration."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment for append mode
        monkeypatch.setenv("APP_NAME", "append_test")
        monkeypatch.setenv("EMPTY_LOG_FILE_ON_RUN", "false")

        config = LogConfig.from_environment()
        log_file_path = get_log_file_path(config.app_name)

        # Create logs directory and file with existing content
        logs_dir = Path("logs")
        logs_dir.mkdir()
        log_file = Path(log_file_path)
        existing_content = "Existing content\n"
        log_file.write_text(existing_content)

        # Create handler with append mode based on config
        mode = "w" if config.empty_log_file_on_run else "a"
        handler = ImmediateFlushFileHandler(log_file_path, mode=mode)

        # Add new content
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="New content",
            args=(),
            exc_info=None,
        )

        handler.emit(record)
        handler.close()

        # File should contain both old and new content
        content = log_file.read_text()
        assert existing_content in content
        assert "New content" in content
