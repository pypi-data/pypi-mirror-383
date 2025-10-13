#!/usr/bin/env python3
"""
Unit tests for GitHub Status Reporter

Tests the status reporting functionality including formatting,
progress indicators, output formats, and terminal compatibility.
"""

import io
import json
import sys
from typing import Any, List, Optional

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, "scripts")

from github_data_models import PipelineStatus, WorkflowRun  # noqa: E402
from github_monitor_config import MonitoringConfig, OutputFormat  # noqa: E402
from github_status_reporter import StatusReporter  # noqa: E402


class TestStatusReporter:
    """Test the StatusReporter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = MonitoringConfig()
        self.config.colors_enabled = True
        self.config.progress_indicators = True
        self.config.verbose = False

        self.output_stream = io.StringIO()
        self.reporter = StatusReporter(self.config, self.output_stream)

    def create_test_workflow_run(
        self,
        id: int = 1,
        name: str = "Test Workflow",
        status: str = "completed",
        conclusion: str = "success",
        duration_seconds: int = 60,
    ) -> WorkflowRun:
        """Create a test workflow run."""
        return WorkflowRun(
            id=id,
            name=name,
            status=status,
            conclusion=conclusion,
            html_url=f"https://github.com/test/repo/actions/runs/{id}",
            created_at="2024-01-01T10:00:00Z",
            updated_at="2024-01-01T10:01:00Z",
            head_sha="abc123def456",
            duration_seconds=duration_seconds,
        )

    def create_test_pipeline_status(
        self,
        overall_status: str = "success",
        workflow_runs: Optional[List[Any]] = None,
        failed_workflows: Optional[List[Any]] = None,
        pending_workflows: Optional[List[Any]] = None,
        success_workflows: Optional[List[Any]] = None,
    ) -> PipelineStatus:
        """Create a test pipeline status."""
        if workflow_runs is None:
            workflow_runs = [self.create_test_workflow_run()]

        return PipelineStatus(
            commit_sha="abc123def456",
            workflow_runs=workflow_runs,
            overall_status=overall_status,
            failed_workflows=failed_workflows or [],
            pending_workflows=pending_workflows or [],
            success_workflows=success_workflows or ["Test Workflow"],
            total_duration_seconds=60,
            estimated_completion_seconds=None,
        )


class TestStatusFormatting:
    """Test status formatting for different pipeline states."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = MonitoringConfig()
        self.config.colors_enabled = True
        self.output_stream = io.StringIO()
        self.reporter = StatusReporter(self.config, self.output_stream)

    def test_successful_pipeline_display(self):
        """Test display of successful pipeline status."""
        workflow = WorkflowRun(
            id=1,
            name="CI Tests",
            status="completed",
            conclusion="success",
            html_url="https://github.com/test/repo/actions/runs/1",
            created_at="2024-01-01T10:00:00Z",
            updated_at="2024-01-01T10:01:00Z",
            head_sha="abc123",
            duration_seconds=120,
        )

        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=[workflow],
            overall_status="success",
            failed_workflows=[],
            pending_workflows=[],
            success_workflows=["CI Tests"],
            total_duration_seconds=120,
        )

        self.reporter.display_status(status)
        output = self.output_stream.getvalue()

        assert "Pipeline Status" in output
        assert "abc123de" in output  # Truncated commit SHA
        assert "SUCCESS" in output
        assert "CI Tests" in output
        assert "success" in output
        assert "2m 0s" in output  # Duration formatting

    def test_failed_pipeline_display(self):
        """Test display of failed pipeline status."""
        workflow = WorkflowRun(
            id=1,
            name="Security Scan",
            status="completed",
            conclusion="failure",
            html_url="https://github.com/test/repo/actions/runs/1",
            created_at="2024-01-01T10:00:00Z",
            updated_at="2024-01-01T10:01:00Z",
            head_sha="abc123",
            duration_seconds=45,
        )

        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=[workflow],
            overall_status="failure",
            failed_workflows=["Security Scan"],
            pending_workflows=[],
            success_workflows=[],
            total_duration_seconds=45,
        )

        self.reporter.display_status(status)
        output = self.output_stream.getvalue()

        assert "FAILURE" in output
        assert "Security Scan" in output
        assert "failure" in output
        assert "45s" in output
        assert "1 failed" in output

    def test_pending_pipeline_display(self):
        """Test display of pending pipeline status."""
        workflows = [
            WorkflowRun(
                id=1,
                name="Build",
                status="completed",
                conclusion="success",
                html_url="https://github.com/test/repo/actions/runs/1",
                created_at="2024-01-01T10:00:00Z",
                updated_at="2024-01-01T10:01:00Z",
                head_sha="abc123",
                duration_seconds=60,
            ),
            WorkflowRun(
                id=2,
                name="Deploy",
                status="in_progress",
                conclusion=None,
                html_url="https://github.com/test/repo/actions/runs/2",
                created_at="2024-01-01T10:01:00Z",
                updated_at="2024-01-01T10:01:00Z",
                head_sha="abc123",
                duration_seconds=None,
            ),
        ]

        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=workflows,
            overall_status="pending",
            failed_workflows=[],
            pending_workflows=["Deploy"],
            success_workflows=["Build"],
            total_duration_seconds=60,
            estimated_completion_seconds=60,
        )

        self.reporter.display_status(status)
        output = self.output_stream.getvalue()

        assert "PENDING" in output
        assert "Build" in output
        assert "Deploy" in output
        assert "in_progress" in output
        assert "1 successful" in output
        assert "1 pending" in output
        assert "Est. completion: ~1m 0s" in output

    def test_no_workflows_display(self):
        """Test display when no workflows are found."""
        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=[],
            overall_status="no_workflows",
            failed_workflows=[],
            pending_workflows=[],
            success_workflows=[],
        )

        self.reporter.display_status(status)
        output = self.output_stream.getvalue()

        assert "No workflows found" in output


class TestProgressIndicators:
    """Test progress indicator updates and completion estimation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = MonitoringConfig()
        self.config.progress_indicators = True
        self.output_stream = io.StringIO()
        self.reporter = StatusReporter(self.config, self.output_stream)

    def test_progress_display_with_pending_workflows(self):
        """Test progress indicators for pending workflows."""
        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=[
                WorkflowRun(
                    id=1,
                    name="Test",
                    status="in_progress",
                    conclusion=None,
                    html_url="https://github.com/test/repo/actions/runs/1",
                    created_at="2024-01-01T10:00:00Z",
                    updated_at="2024-01-01T10:01:00Z",
                    head_sha="abc123",
                ),
            ],
            overall_status="pending",
            failed_workflows=[],
            pending_workflows=["Test"],
            success_workflows=[],
            estimated_completion_seconds=120,
        )

        self.reporter.display_progress(status)
        output = self.output_stream.getvalue()

        assert "Monitoring 1 workflow" in output
        assert "Estimated completion: ~2m 0s" in output

    def test_progress_display_no_pending_workflows(self):
        """Test progress display when no workflows are pending."""
        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=[],
            overall_status="success",
            failed_workflows=[],
            pending_workflows=[],
            success_workflows=[],
        )

        self.reporter.display_progress(status)
        output = self.output_stream.getvalue()

        # Should not display progress for completed workflows
        assert output.strip() == ""

    def test_completion_display_success(self):
        """Test completion display for successful pipeline."""
        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=[
                WorkflowRun(
                    id=1,
                    name="Test",
                    status="completed",
                    conclusion="success",
                    html_url="https://github.com/test/repo/actions/runs/1",
                    created_at="2024-01-01T10:00:00Z",
                    updated_at="2024-01-01T10:02:00Z",
                    head_sha="abc123",
                    duration_seconds=120,
                ),
            ],
            overall_status="success",
            failed_workflows=[],
            pending_workflows=[],
            success_workflows=["Test"],
            total_duration_seconds=120,
        )

        self.reporter.display_completion(status)
        output = self.output_stream.getvalue()

        assert "All workflows completed successfully" in output
        assert "Total execution time: 2m 0s" in output

    def test_completion_display_failure(self):
        """Test completion display for failed pipeline."""
        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=[
                WorkflowRun(
                    id=1,
                    name="Test",
                    status="completed",
                    conclusion="failure",
                    html_url="https://github.com/test/repo/actions/runs/1",
                    created_at="2024-01-01T10:00:00Z",
                    updated_at="2024-01-01T10:01:00Z",
                    head_sha="abc123",
                    duration_seconds=60,
                ),
            ],
            overall_status="failure",
            failed_workflows=["Test"],
            pending_workflows=[],
            success_workflows=[],
        )

        self.reporter.display_completion(status)
        output = self.output_stream.getvalue()

        assert "Pipeline failed" in output
        assert "1 workflow(s) failed" in output
        assert "✗ Test" in output


class TestOutputFormats:
    """Test output format variations (console, JSON, minimal)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = MonitoringConfig()
        self.output_stream = io.StringIO()

    def test_console_output_format(self):
        """Test console output format."""
        self.config.output_format = OutputFormat.CONSOLE
        reporter = StatusReporter(self.config, self.output_stream)

        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=[
                WorkflowRun(
                    id=1,
                    name="Test",
                    status="completed",
                    conclusion="success",
                    html_url="https://github.com/test/repo/actions/runs/1",
                    created_at="2024-01-01T10:00:00Z",
                    updated_at="2024-01-01T10:01:00Z",
                    head_sha="abc123",
                    duration_seconds=60,
                ),
            ],
            overall_status="success",
            failed_workflows=[],
            pending_workflows=[],
            success_workflows=["Test"],
        )

        reporter.display_status(status)
        output = self.output_stream.getvalue()

        assert "📊 Pipeline Status" in output
        assert "📝 Commit:" in output
        assert "✅" in output  # Success icon
        assert "Test" in output

    def test_json_output_format(self):
        """Test JSON output format."""
        self.config.output_format = OutputFormat.JSON
        reporter = StatusReporter(self.config, self.output_stream)

        status = PipelineStatus(
            commit_sha="abc123def456",
            workflow_runs=[
                WorkflowRun(
                    id=1,
                    name="Test",
                    status="completed",
                    conclusion="success",
                    html_url="https://github.com/test/repo/actions/runs/1",
                    created_at="2024-01-01T10:00:00Z",
                    updated_at="2024-01-01T10:01:00Z",
                    head_sha="abc123",
                    duration_seconds=60,
                ),
            ],
            overall_status="success",
            failed_workflows=[],
            pending_workflows=[],
            success_workflows=["Test"],
        )

        reporter.display_status(status)
        output = self.output_stream.getvalue()

        # Parse JSON to verify structure
        json_data = json.loads(output)
        assert json_data["type"] == "status"
        assert json_data["commit_sha"] == "abc123def456"
        assert json_data["overall_status"] == "success"
        assert len(json_data["workflow_runs"]) == 1
        assert json_data["workflow_runs"][0]["name"] == "Test"
        assert json_data["workflow_runs"][0]["conclusion"] == "success"

    def test_minimal_output_format(self):
        """Test minimal output format."""
        self.config.output_format = OutputFormat.MINIMAL
        reporter = StatusReporter(self.config, self.output_stream)

        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=[
                WorkflowRun(
                    id=1,
                    name="Test",
                    status="completed",
                    conclusion="success",
                    html_url="https://github.com/test/repo/actions/runs/1",
                    created_at="2024-01-01T10:00:00Z",
                    updated_at="2024-01-01T10:01:00Z",
                    head_sha="abc123",
                    duration_seconds=60,
                ),
            ],
            overall_status="success",
            failed_workflows=[],
            pending_workflows=[],
            success_workflows=["Test"],
        )

        reporter.display_status(status)
        output = self.output_stream.getvalue()

        assert "✓ success" in output
        # Should be much shorter than console format
        assert "Pipeline Status" not in output
        assert len(output.split("\n")) <= 3


class TestColorCoding:
    """Test color coding and terminal compatibility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.output_stream = io.StringIO()

    def test_colors_enabled(self):
        """Test output with colors enabled."""
        config = MonitoringConfig()
        config.colors_enabled = True
        reporter = StatusReporter(config, self.output_stream)

        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=[
                WorkflowRun(
                    id=1,
                    name="Test",
                    status="completed",
                    conclusion="success",
                    html_url="https://github.com/test/repo/actions/runs/1",
                    created_at="2024-01-01T10:00:00Z",
                    updated_at="2024-01-01T10:01:00Z",
                    head_sha="abc123",
                    duration_seconds=60,
                ),
            ],
            overall_status="success",
            failed_workflows=[],
            pending_workflows=[],
            success_workflows=["Test"],
        )

        reporter.display_status(status)
        output = self.output_stream.getvalue()

        # Should contain ANSI color codes
        assert "\033[" in output  # ANSI escape sequence
        assert "\033[0m" in output  # Reset color code

    def test_colors_disabled(self):
        """Test output with colors disabled (terminal compatibility)."""
        config = MonitoringConfig()
        config.colors_enabled = False
        reporter = StatusReporter(config, self.output_stream)

        status = PipelineStatus(
            commit_sha="abc123def",
            workflow_runs=[
                WorkflowRun(
                    id=1,
                    name="Test",
                    status="completed",
                    conclusion="success",
                    html_url="https://github.com/test/repo/actions/runs/1",
                    created_at="2024-01-01T10:00:00Z",
                    updated_at="2024-01-01T10:01:00Z",
                    head_sha="abc123",
                    duration_seconds=60,
                ),
            ],
            overall_status="success",
            failed_workflows=[],
            pending_workflows=[],
            success_workflows=["Test"],
        )

        reporter.display_status(status)
        output = self.output_stream.getvalue()

        # Should not contain ANSI color codes
        assert "\033[" not in output
        # But should still have icons and formatting
        assert "✅" in output
        assert "📊" in output
        assert "Test" in output

    def test_status_icons_mapping(self):
        """Test that different statuses get appropriate icons."""
        config = MonitoringConfig()
        config.colors_enabled = False  # Focus on icons, not colors
        reporter = StatusReporter(config, self.output_stream)

        # Test success status
        success_status = PipelineStatus(
            commit_sha="abc123",
            workflow_runs=[
                WorkflowRun(
                    id=1,
                    name="Test",
                    status="completed",
                    conclusion="success",
                    html_url="https://github.com/test/repo/actions/runs/1",
                    created_at="2024-01-01T10:00:00Z",
                    updated_at="2024-01-01T10:01:00Z",
                    head_sha="abc123",
                    duration_seconds=60,
                ),
            ],
            overall_status="success",
            failed_workflows=[],
            pending_workflows=[],
            success_workflows=["Test"],
        )

        reporter.display_status(success_status)
        success_output = self.output_stream.getvalue()
        assert "✅" in success_output

        # Reset stream for next test
        self.output_stream = io.StringIO()
        reporter = StatusReporter(config, self.output_stream)

        # Test failure status
        failure_status = PipelineStatus(
            commit_sha="abc123",
            workflow_runs=[
                WorkflowRun(
                    id=1,
                    name="Test",
                    status="completed",
                    conclusion="failure",
                    html_url="https://github.com/test/repo/actions/runs/1",
                    created_at="2024-01-01T10:00:00Z",
                    updated_at="2024-01-01T10:01:00Z",
                    head_sha="abc123",
                    duration_seconds=60,
                ),
            ],
            overall_status="failure",
            failed_workflows=["Test"],
            pending_workflows=[],
            success_workflows=[],
        )

        reporter.display_status(failure_status)
        failure_output = self.output_stream.getvalue()
        assert "❌" in failure_output

        # Reset stream for pending test
        self.output_stream = io.StringIO()
        reporter = StatusReporter(config, self.output_stream)

        # Test pending status
        pending_status = PipelineStatus(
            commit_sha="abc123",
            workflow_runs=[
                WorkflowRun(
                    id=1,
                    name="Test",
                    status="in_progress",
                    conclusion=None,
                    html_url="https://github.com/test/repo/actions/runs/1",
                    created_at="2024-01-01T10:00:00Z",
                    updated_at="2024-01-01T10:01:00Z",
                    head_sha="abc123",
                    duration_seconds=None,
                ),
            ],
            overall_status="pending",
            failed_workflows=[],
            pending_workflows=["Test"],
            success_workflows=[],
        )

        reporter.display_status(pending_status)
        pending_output = self.output_stream.getvalue()
        assert "🔄" in pending_output


class TestErrorHandling:
    """Test error handling and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = MonitoringConfig()
        self.output_stream = io.StringIO()
        self.reporter = StatusReporter(self.config, self.output_stream)

    def test_display_error(self):
        """Test error display functionality."""
        test_error = Exception("Test error message")
        self.reporter.display_error(test_error, "Test context")
        output = self.output_stream.getvalue()

        assert "Error: Test error message" in output
        assert "Context: Test context" in output

    def test_display_warning(self):
        """Test warning display functionality."""
        # Test with verbose mode to show context
        self.config.verbose = True
        self.reporter = StatusReporter(self.config, self.output_stream)

        self.reporter.display_warning("Test warning", "Test context")
        output = self.output_stream.getvalue()

        assert "Warning: Test warning" in output
        # Context only shows in verbose mode
        if self.config.verbose:
            assert "Context: Test context" in output

    def test_display_info(self):
        """Test info display functionality."""
        # Test with verbose mode to show context
        self.config.verbose = True
        self.reporter = StatusReporter(self.config, self.output_stream)

        self.reporter.display_info("Test info", "Test context")
        output = self.output_stream.getvalue()

        assert "Test info" in output
        # Context only shows in verbose mode
        if self.config.verbose:
            assert "Context: Test context" in output

    def test_duration_formatting(self):
        """Test duration formatting edge cases."""
        # Test seconds only
        assert self.reporter._format_duration(45) == "45s"

        # Test minutes and seconds
        assert self.reporter._format_duration(125) == "2m 5s"

        # Test hours, minutes
        assert self.reporter._format_duration(3665) == "1h 1m"

        # Test zero duration
        assert self.reporter._format_duration(0) == "0s"

    def test_progress_percentage_calculation(self):
        """Test progress percentage calculation."""
        # Test with completed workflows
        status = PipelineStatus(
            commit_sha="abc123",
            workflow_runs=[
                WorkflowRun(
                    1, "Test1", "completed", "success", "url", "time", "time", "sha", 60
                ),
                WorkflowRun(
                    2, "Test2", "in_progress", None, "url", "time", "time", "sha", None
                ),
                WorkflowRun(
                    3, "Test3", "queued", None, "url", "time", "time", "sha", None
                ),
            ],
            overall_status="pending",
            failed_workflows=[],
            pending_workflows=["Test2", "Test3"],
            success_workflows=["Test1"],
        )

        percentage = self.reporter._calculate_progress_percentage(status)
        assert percentage is not None  # Type narrowing for MyPy
        assert (
            abs(percentage - 33.33333333333333) < 0.0001
        )  # 1 out of 3 completed (floating point tolerance)

        # Test with no workflows
        empty_status = PipelineStatus(
            commit_sha="abc123",
            workflow_runs=[],
            overall_status="no_workflows",
            failed_workflows=[],
            pending_workflows=[],
            success_workflows=[],
        )

        percentage = self.reporter._calculate_progress_percentage(empty_status)
        assert percentage is None


if __name__ == "__main__":
    pytest.main([__file__])
