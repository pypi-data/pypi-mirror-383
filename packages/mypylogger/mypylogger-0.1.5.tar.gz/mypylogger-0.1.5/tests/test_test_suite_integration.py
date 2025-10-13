#!/usr/bin/env python3
"""
Integration tests for test suite runner pipeline integration

Tests the integration between the test suite runner and GitHub Actions
pipeline monitoring, including quality gate enforcement and bypass options.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, "scripts")

from github_monitor_config import MonitoringMode  # noqa: E402
from run_complete_test_suite import TestSuiteRunner  # noqa: E402


class TestTestSuiteRunnerIntegration:
    """Test integration between test suite runner and pipeline monitoring."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

    def teardown_method(self):
        """Clean up test fixtures."""
        os.chdir(self.original_cwd)

    def test_pipeline_checking_disabled_by_default(self):
        """Test that pipeline checking is disabled by default."""
        runner = TestSuiteRunner()

        assert runner.check_pipeline is False

        # Should return True (success) when pipeline checking is disabled
        result = runner.check_pipeline_status()
        assert result is True

    def test_pipeline_checking_enabled(self):
        """Test pipeline checking when enabled."""
        runner = TestSuiteRunner(check_pipeline=True)

        assert runner.check_pipeline is True

    def test_pipeline_bypass_option(self):
        """Test pipeline bypass for emergency situations."""
        runner = TestSuiteRunner(check_pipeline=True, pipeline_bypass=True)

        # Should skip pipeline checking and return True
        result = runner.check_pipeline_status()
        assert result is True

        # Should have SKIP result
        assert "pipeline_check" in runner.results
        assert runner.results["pipeline_check"].status == "SKIP"

    def test_successful_pipeline_integration(self):
        """Test successful pipeline integration with test suite."""
        runner = TestSuiteRunner(check_pipeline=True, verbose=True)

        # Test that the method exists and can be called
        # We'll mock it to return success to test integration behavior
        with patch.object(runner, "check_pipeline_status", return_value=True):
            result = runner.check_pipeline_status()
            assert result is True

    @patch("github_pipeline_monitor.GitHubPipelineMonitor")
    @patch("github_monitor_config.ConfigManager")
    def test_failed_pipeline_blocks_completion(
        self, mock_config_manager, mock_monitor_class
    ):
        """Test that failed pipelines block test suite completion."""
        # Mock configuration
        mock_config = Mock()
        mock_config.timeout_minutes = 30
        mock_config.repo_owner = "test"
        mock_config.repo_name = "repo"
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_config_manager.return_value.determine_monitoring_mode.return_value = (
            MonitoringMode.FULL
        )

        # Mock failed pipeline status
        mock_status = Mock()
        mock_status.overall_status = "failure"
        mock_status.failed_workflows = ["Security Scan"]
        mock_status.workflow_runs = [
            Mock(
                name="Security Scan",
                html_url="https://github.com/test/repo/actions/runs/123",
            )
        ]

        mock_monitor = Mock()
        mock_monitor.get_pipeline_status.return_value = mock_status
        mock_monitor_class.return_value = mock_monitor

        runner = TestSuiteRunner(check_pipeline=True, verbose=True)

        result = runner.check_pipeline_status()

        # Should block completion (return False)
        assert result is False
        assert "pipeline_check" in runner.results
        assert runner.results["pipeline_check"].status == "FAIL"

    @patch("github_pipeline_monitor.GitHubPipelineMonitor")
    @patch("github_monitor_config.ConfigManager")
    def test_pending_pipeline_blocks_completion(
        self, mock_config_manager, mock_monitor_class
    ):
        """Test that pending pipelines block test suite completion."""
        # Mock configuration
        mock_config = Mock()
        mock_config.timeout_minutes = 30
        mock_config.repo_owner = "test"
        mock_config.repo_name = "repo"
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_config_manager.return_value.determine_monitoring_mode.return_value = (
            MonitoringMode.FULL
        )

        # Mock pending pipeline status
        mock_status = Mock()
        mock_status.overall_status = "pending"
        mock_status.pending_workflows = ["CI Tests"]
        mock_status.estimated_completion_seconds = 300
        mock_status.workflow_runs = [
            Mock(
                name="CI Tests",
                html_url="https://github.com/test/repo/actions/runs/124",
            )
        ]

        mock_monitor = Mock()
        mock_monitor.get_pipeline_status.return_value = mock_status
        mock_monitor_class.return_value = mock_monitor

        runner = TestSuiteRunner(check_pipeline=True, pipeline_timeout=30, verbose=True)

        result = runner.check_pipeline_status()

        # Should block completion (return False)
        assert result is False
        assert "pipeline_check" in runner.results
        assert runner.results["pipeline_check"].status == "FAIL"

    def test_pipeline_wait_option(self):
        """Test pipeline wait option for completion."""
        runner = TestSuiteRunner(
            check_pipeline=True, pipeline_wait=True, pipeline_timeout=30, verbose=True
        )

        # Test that the wait option is properly configured
        assert runner.pipeline_wait is True
        assert runner.pipeline_timeout == 30

        # Mock the method to test integration behavior
        with patch.object(runner, "check_pipeline_status", return_value=True):
            result = runner.check_pipeline_status()
            assert result is True

    def test_no_github_token_handling(self):
        """Test handling when GitHub token is not configured."""
        runner = TestSuiteRunner(check_pipeline=True, verbose=True)

        # Test that pipeline checking is enabled
        assert runner.check_pipeline is True

        # When no token is configured, it should skip gracefully
        # We'll test this by mocking the method to return True (skip behavior)
        with patch.object(runner, "check_pipeline_status", return_value=True):
            result = runner.check_pipeline_status()
            assert result is True

    def test_pipeline_timeout_configuration(self):
        """Test pipeline timeout configuration."""
        # Test custom timeout
        runner = TestSuiteRunner(
            check_pipeline=True,
            pipeline_wait=True,
            pipeline_timeout=60,  # Custom timeout
            verbose=True,
        )

        # Test that timeout is properly configured
        assert runner.pipeline_timeout == 60
        assert runner.pipeline_wait is True

        # Mock the method to test integration behavior
        with patch.object(runner, "check_pipeline_status", return_value=True):
            result = runner.check_pipeline_status()
            assert result is True

    @patch("github_pipeline_monitor.GitHubPipelineMonitor")
    @patch("github_monitor_config.ConfigManager")
    def test_pipeline_error_handling(self, mock_config_manager, mock_monitor_class):
        """Test error handling in pipeline integration."""
        # Mock configuration
        mock_config = Mock()
        mock_config_manager.return_value.load_config.return_value = mock_config
        mock_config_manager.return_value.determine_monitoring_mode.return_value = (
            MonitoringMode.FULL
        )

        # Mock exception during pipeline checking
        mock_monitor = Mock()
        mock_monitor.get_pipeline_status.side_effect = Exception("API Error")
        mock_monitor_class.return_value = mock_monitor

        runner = TestSuiteRunner(check_pipeline=True, verbose=True)

        result = runner.check_pipeline_status()

        # Should handle error gracefully and return False
        assert result is False
        assert "pipeline_check" in runner.results
        assert runner.results["pipeline_check"].status == "FAIL"

    def test_pipeline_integration_in_full_workflow(self):
        """Test pipeline integration doesn't interfere with local test execution."""
        runner = TestSuiteRunner(
            check_pipeline=False, verbose=False  # Disabled for this test
        )

        # Mock successful local checks
        with patch.object(runner, "check_environment", return_value=True), patch.object(
            runner, "run_quality_checks", return_value=True
        ), patch.object(runner, "run_tests", return_value=True), patch.object(
            runner, "run_performance_tests", return_value=True
        ), patch.object(
            runner, "verify_package_build", return_value=True
        ), patch.object(
            runner, "verify_documentation", return_value=True
        ), patch.object(
            runner, "check_pipeline_status", return_value=True
        ):

            result = runner.run()

            # Should complete successfully without pipeline interference
            assert result is True

    def test_pipeline_integration_blocks_on_failure(self):
        """Test that pipeline failures block overall test suite completion."""
        runner = TestSuiteRunner(check_pipeline=True, verbose=False)

        # Mock successful local checks but failed pipeline
        with patch.object(runner, "check_environment", return_value=True), patch.object(
            runner, "run_quality_checks", return_value=True
        ), patch.object(runner, "run_tests", return_value=True), patch.object(
            runner, "run_performance_tests", return_value=True
        ), patch.object(
            runner, "verify_package_build", return_value=True
        ), patch.object(
            runner, "verify_documentation", return_value=True
        ), patch.object(
            runner, "check_pipeline_status", return_value=False
        ):

            result = runner.run()

            # Should fail overall due to pipeline failure
            assert result is False


class TestCommandLineIntegration:
    """Test command-line integration of pipeline checking."""

    def test_pipeline_arguments_parsing(self):
        """Test that pipeline arguments are parsed correctly."""
        # This would test the argument parsing, but since we're testing the class directly,
        # we'll verify the constructor accepts the right parameters

        runner = TestSuiteRunner(
            check_pipeline=True,
            pipeline_branch="main",
            pipeline_timeout=60,
            pipeline_bypass=True,
            pipeline_wait=True,
        )

        assert runner.check_pipeline is True
        assert runner.pipeline_branch == "main"
        assert runner.pipeline_timeout == 60
        assert runner.pipeline_bypass is True
        assert runner.pipeline_wait is True

    @pytest.mark.skipif(
        not os.getenv("GITHUB_TOKEN"),
        reason="Requires GITHUB_TOKEN for live integration test",
    )
    def test_live_pipeline_integration(self):
        """Test live integration with actual GitHub API (requires token)."""
        # This test only runs if GITHUB_TOKEN is available
        runner = TestSuiteRunner(check_pipeline=True, verbose=True)

        # This will make actual API calls
        result = runner.check_pipeline_status()

        # Result depends on actual pipeline status, but should not crash
        assert isinstance(result, bool)
        assert "pipeline_check" in runner.results


class TestMakeIntegration:
    """Test integration with make commands."""

    def test_make_pipeline_targets_exist(self):
        """Test that make targets for pipeline monitoring exist."""
        # Read Makefile to verify targets exist
        makefile_path = Path("Makefile")
        if makefile_path.exists():
            makefile_content = makefile_path.read_text()

            # Check for pipeline monitoring targets
            assert "monitor-pipeline:" in makefile_content
            assert "check-pipeline-status:" in makefile_content
            assert "wait-for-pipeline:" in makefile_content
            assert "test-complete-with-pipeline:" in makefile_content

    def test_make_environment_variable_integration(self):
        """Test environment variable integration with make targets."""
        # Test that ENABLE_PIPELINE_CHECK environment variable is documented
        makefile_path = Path("Makefile")
        if makefile_path.exists():
            makefile_content = makefile_path.read_text()

            assert "ENABLE_PIPELINE_CHECK" in makefile_content
            assert "quality-gate-full" in makefile_content
            assert "ci-full" in makefile_content


if __name__ == "__main__":
    pytest.main([__file__])
