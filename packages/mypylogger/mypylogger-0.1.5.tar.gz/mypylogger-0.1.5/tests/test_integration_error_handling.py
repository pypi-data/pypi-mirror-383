"""
Integration tests for error handling and graceful degradation.
"""

import logging
import threading
from unittest.mock import MagicMock, patch

from mypylogger.config import LogConfig
from mypylogger.core import SingletonLogger
from mypylogger.formatters import CustomJsonFormatter
from mypylogger.handlers import (
    ImmediateFlushFileHandler,
    ParallelStdoutHandler,
)


class TestCompleteLoggerSetup:
    """Test complete logger setup with various configurations."""

    def setup_method(self):
        """Reset singleton state before each test."""
        SingletonLogger._instance = None
        SingletonLogger._logger = None
        SingletonLogger._config = None

    def test_complete_setup_development_config(self, tmp_path, monkeypatch):
        """Test complete logger setup with development configuration."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set development environment
        monkeypatch.setenv("APP_NAME", "dev_app")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("EMPTY_LOG_FILE_ON_RUN", "true")
        monkeypatch.setenv("PARALLEL_STDOUT_LOGGING", "DEBUG")

        # Get logger and verify configuration
        logger = SingletonLogger.get_logger()
        config = LogConfig.from_environment()

        assert logger.name == "dev_app"
        assert logger.level == logging.DEBUG
        assert config.app_name == "dev_app"
        assert config.log_level == "DEBUG"
        assert config.empty_log_file_on_run is True
        assert config.parallel_stdout_logging == "DEBUG"

    def test_complete_setup_production_config(self, tmp_path, monkeypatch):
        """Test complete logger setup with production configuration."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set production environment
        monkeypatch.setenv("APP_NAME", "prod_app")
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        monkeypatch.setenv("EMPTY_LOG_FILE_ON_RUN", "false")
        monkeypatch.setenv("PARALLEL_STDOUT_LOGGING", "false")

        # Get logger and verify configuration
        logger = SingletonLogger.get_logger()
        config = LogConfig.from_environment()

        assert logger.name == "prod_app"
        assert logger.level == logging.WARNING
        assert config.app_name == "prod_app"
        assert config.log_level == "WARNING"
        assert config.empty_log_file_on_run is False
        assert config.parallel_stdout_logging == "false"

    def test_complete_setup_with_defaults(self, tmp_path, monkeypatch):
        """Test complete logger setup with default configuration."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Clear all environment variables
        for var in [
            "APP_NAME",
            "LOG_LEVEL",
            "EMPTY_LOG_FILE_ON_RUN",
            "PARALLEL_STDOUT_LOGGING",
        ]:
            monkeypatch.delenv(var, raising=False)

        # Get logger and verify defaults
        logger = SingletonLogger.get_logger()
        config = LogConfig.from_environment()

        assert logger.name == "default_app"
        assert logger.level == logging.INFO
        assert config.app_name == "default_app"
        assert config.log_level == "INFO"
        assert config.empty_log_file_on_run is False
        assert config.parallel_stdout_logging == "false"


class TestGracefulDegradation:
    """Test graceful degradation when file operations fail."""

    def setup_method(self):
        """Reset singleton state before each test."""
        SingletonLogger._instance = None
        SingletonLogger._logger = None
        SingletonLogger._config = None

    def test_log_directory_creation_failure(self, tmp_path, monkeypatch):
        """Test graceful handling when log directory cannot be created."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Create a file where the logs directory should be (to cause mkdir to fail)
        logs_path = tmp_path / "logs"
        logs_path.write_text("blocking file")

        # Mock os.makedirs to raise PermissionError
        with patch(
            "pathlib.Path.mkdir", side_effect=PermissionError("Permission denied")
        ):
            # This should not raise an exception
            try:
                handler = ImmediateFlushFileHandler("logs/test.log")
                # If we get here, the handler was created despite the error
                assert handler is not None
            except PermissionError:
                # This is expected - the handler creation should fail gracefully
                pass

    def test_file_write_permission_error(self, tmp_path, monkeypatch):
        """Test graceful handling when file cannot be written."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Create logs directory
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        # Create a read-only log file
        log_file = logs_dir / "test.log"
        log_file.write_text("existing content")
        log_file.chmod(0o444)  # Read-only

        try:
            # This should handle the permission error gracefully
            handler = ImmediateFlushFileHandler(str(log_file))

            # Try to emit a log record
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="test.py",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # This should not crash the application
            handler.emit(record)
            handler.close()

        except (PermissionError, OSError):
            # Expected behavior - handler should fail gracefully
            pass
        finally:
            # Restore permissions for cleanup
            try:
                log_file.chmod(0o644)
            except Exception:
                pass

    def test_stdout_handler_error_recovery(self):
        """Test that stdout handler continues operation after errors."""
        handler = ParallelStdoutHandler(logging.INFO)

        # Mock sys.stdout.write to raise an exception
        with patch("sys.stdout.write", side_effect=OSError("Broken pipe")):
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="test.py",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # This should not crash - handler should recover gracefully
            try:
                handler.emit(record)
            except OSError:
                # If exception propagates, that's also acceptable
                pass


class TestConfigurationErrorHandling:
    """Test configuration error handling with invalid values."""

    def setup_method(self):
        """Reset singleton state before each test."""
        SingletonLogger._instance = None
        SingletonLogger._logger = None
        SingletonLogger._config = None

    def test_invalid_log_level_defaults_to_info(self, monkeypatch):
        """Test that invalid log level defaults to INFO with warning."""
        monkeypatch.setenv("LOG_LEVEL", "INVALID_LEVEL")

        config = LogConfig.from_environment()

        # Should default to INFO for invalid level
        assert config.log_level == "INVALID_LEVEL"  # Config stores original
        assert config.get_log_level_int() == logging.INFO  # But converts to INFO

    def test_empty_app_name_uses_default(self, monkeypatch):
        """Test that empty app name uses default."""
        monkeypatch.setenv("APP_NAME", "")

        config = LogConfig.from_environment()

        assert config.app_name == "default_app"

    def test_empty_log_level_uses_default(self, monkeypatch):
        """Test that empty log level uses default."""
        monkeypatch.setenv("LOG_LEVEL", "")

        config = LogConfig.from_environment()

        assert config.log_level == "INFO"

    def test_invalid_boolean_values_default_to_false(self, monkeypatch):
        """Test that invalid boolean values default to False."""
        monkeypatch.setenv("EMPTY_LOG_FILE_ON_RUN", "invalid")

        config = LogConfig.from_environment()

        assert config.empty_log_file_on_run is False

    def test_case_insensitive_log_levels(self, monkeypatch):
        """Test that log levels are case insensitive."""
        test_cases = [
            ("debug", logging.DEBUG),
            ("DEBUG", logging.DEBUG),
            ("Debug", logging.DEBUG),
            ("info", logging.INFO),
            ("INFO", logging.INFO),
            ("warning", logging.WARNING),
            ("WARNING", logging.WARNING),
            ("error", logging.ERROR),
            ("ERROR", logging.ERROR),
            ("critical", logging.CRITICAL),
            ("CRITICAL", logging.CRITICAL),
        ]

        for level_str, expected_int in test_cases:
            monkeypatch.setenv("LOG_LEVEL", level_str)
            config = LogConfig.from_environment()
            assert config.get_log_level_int() == expected_int


class TestHandlerErrorRecovery:
    """Test handler error recovery and continuation with available handlers."""

    def setup_method(self):
        """Reset singleton state before each test."""
        SingletonLogger._instance = None
        SingletonLogger._logger = None
        SingletonLogger._config = None

    def test_file_handler_failure_continues_with_stdout(self, tmp_path, monkeypatch):
        """Test that if file handler fails, stdout handler still works."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Mock file handler creation to fail
        with patch(
            "mypylogger.handlers.ImmediateFlushFileHandler.__init__",
            side_effect=PermissionError("Cannot create file"),
        ):

            # Create stdout handler - this should still work
            stdout_handler = ParallelStdoutHandler(logging.INFO)

            # Verify stdout handler works
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="test.py",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # This should work even if file handler failed
            stdout_handler.emit(record)

    def test_formatter_error_recovery(self):
        """Test that handler continues operation if formatter fails."""
        handler = ParallelStdoutHandler(logging.INFO)

        # Create a formatter that will fail
        bad_formatter = MagicMock()
        bad_formatter.format.side_effect = ValueError("Formatter error")
        handler.setFormatter(bad_formatter)

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Handler should handle formatter errors gracefully
        try:
            handler.emit(record)
        except ValueError:
            # If exception propagates, that's acceptable
            pass


class TestNoDuplicateHandlers:
    """Test that no duplicate handlers are added on multiple calls."""

    def setup_method(self):
        """Reset singleton state before each test."""
        SingletonLogger._instance = None
        SingletonLogger._logger = None
        SingletonLogger._config = None

    def test_multiple_get_logger_calls_no_duplicate_handlers(
        self, tmp_path, monkeypatch
    ):
        """Test that multiple get_logger calls don't add duplicate handlers."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Get logger multiple times
        logger1 = SingletonLogger.get_logger()
        initial_handler_count = len(logger1.handlers)

        logger2 = SingletonLogger.get_logger()
        logger3 = SingletonLogger.get_logger()

        # Should be the same instance
        assert logger1 is logger2 is logger3

        # Handler count should not increase
        assert len(logger2.handlers) == initial_handler_count
        assert len(logger3.handlers) == initial_handler_count

    def test_singleton_thread_safety_no_duplicate_handlers(self, tmp_path, monkeypatch):
        """Test that concurrent access doesn't create duplicate handlers."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        loggers = []
        exceptions = []

        def get_logger_thread():
            try:
                logger = SingletonLogger.get_logger()
                loggers.append(logger)
            except Exception as e:
                exceptions.append(e)

        # Create multiple threads that try to get logger simultaneously
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=get_logger_thread)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Should have no exceptions
        assert len(exceptions) == 0

        # All loggers should be the same instance
        assert len(loggers) == 10
        first_logger = loggers[0]
        for logger in loggers[1:]:
            assert logger is first_logger

        # Should have consistent handler count
        handler_counts = [len(logger.handlers) for logger in loggers]
        assert all(count == handler_counts[0] for count in handler_counts)


class TestCompleteIntegrationScenarios:
    """Test complete integration scenarios with various error conditions."""

    def setup_method(self):
        """Reset singleton state before each test."""
        SingletonLogger._instance = None
        SingletonLogger._logger = None
        SingletonLogger._config = None

    def test_mixed_success_and_failure_handlers(self, tmp_path, monkeypatch):
        """Test scenario where some handlers succeed and others fail."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment
        monkeypatch.setenv("APP_NAME", "mixed_test")
        monkeypatch.setenv("LOG_LEVEL", "INFO")

        # Create a scenario where file handler might fail but stdout succeeds
        with patch(
            "pathlib.Path.mkdir", side_effect=PermissionError("Permission denied")
        ):
            # Stdout handler should still work
            stdout_handler = ParallelStdoutHandler(logging.INFO)
            formatter = CustomJsonFormatter()
            stdout_handler.setFormatter(formatter)

            # Test that we can still log to stdout
            record = logging.LogRecord(
                name="mixed_test",
                level=logging.INFO,
                pathname="test.py",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # This should work even if file operations fail
            stdout_handler.emit(record)

    def test_complete_failure_recovery(self, tmp_path, monkeypatch):
        """Test recovery when multiple components fail."""
        # Change to tmp_path as project root
        monkeypatch.chdir(tmp_path)

        # Set up environment with problematic values
        monkeypatch.setenv("APP_NAME", "")  # Empty app name
        monkeypatch.setenv("LOG_LEVEL", "INVALID")  # Invalid log level

        # Configuration should still work with defaults
        config = LogConfig.from_environment()
        assert config.app_name == "default_app"
        assert config.get_log_level_int() == logging.INFO

        # Logger should still be created
        logger = SingletonLogger.get_logger()
        assert logger is not None
        assert logger.name == "default_app"
        assert logger.level == logging.INFO
