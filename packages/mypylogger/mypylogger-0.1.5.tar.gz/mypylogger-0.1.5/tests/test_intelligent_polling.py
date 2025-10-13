#!/usr/bin/env python3
"""
Tests for GitHub Intelligent Polling System

This module tests the adaptive polling intervals and intelligent monitoring
strategies for GitHub Actions workflows.
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
from github_data_models import WorkflowRun  # noqa: E402
from github_intelligent_polling import (  # noqa: E402
    IntelligentPollingManager,
    PollingStrategy,
    WorkflowHistory,
    WorkflowPhase,
    create_intelligent_polling_manager,
)


class TestWorkflowHistory:
    """Test WorkflowHistory functionality."""

    def test_workflow_history_initialization(self):
        """Test WorkflowHistory initialization."""
        history = WorkflowHistory("test-workflow")

        assert history.workflow_name == "test-workflow"
        assert history.typical_duration_seconds is None
        assert history.last_seen_status is None
        assert history.last_seen_conclusion is None
        assert len(history.phase_transitions) == 0
        assert len(history.duration_samples) == 0

    def test_add_duration_sample_single(self):
        """Test adding a single duration sample."""
        history = WorkflowHistory("test-workflow")
        history.add_duration_sample(120)

        assert len(history.duration_samples) == 1
        assert history.duration_samples[0] == 120
        assert history.typical_duration_seconds == 120

    def test_add_duration_sample_multiple(self):
        """Test adding multiple duration samples and median calculation."""
        history = WorkflowHistory("test-workflow")

        # Add odd number of samples
        for duration in [100, 120, 150]:
            history.add_duration_sample(duration)

        assert len(history.duration_samples) == 3
        assert history.typical_duration_seconds == 120  # Median of [100, 120, 150]

        # Add even number of samples
        history.add_duration_sample(180)
        assert (
            history.typical_duration_seconds == 135
        )  # Average of middle two: (120 + 150) / 2

    def test_duration_sample_limit(self):
        """Test that duration samples are limited to last 10."""
        history = WorkflowHistory("test-workflow")

        # Add 15 samples
        for i in range(15):
            history.add_duration_sample(i * 10)

        assert len(history.duration_samples) == 10
        assert history.duration_samples == [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]

    def test_record_phase_transition(self):
        """Test recording phase transitions."""
        history = WorkflowHistory("test-workflow")

        history.record_phase_transition(WorkflowPhase.QUEUED, WorkflowPhase.ACTIVE)

        assert len(history.phase_transitions) == 1
        timestamp, old_phase, new_phase = history.phase_transitions[0]
        assert old_phase == WorkflowPhase.QUEUED
        assert new_phase == WorkflowPhase.ACTIVE
        assert isinstance(timestamp, datetime)

    def test_phase_transition_limit(self):
        """Test that phase transitions are limited to last 20."""
        history = WorkflowHistory("test-workflow")

        # Add 25 transitions
        for i in range(25):
            history.record_phase_transition(WorkflowPhase.QUEUED, WorkflowPhase.ACTIVE)

        assert len(history.phase_transitions) == 20


class TestPollingStrategy:
    """Test PollingStrategy functionality."""

    def test_polling_strategy_defaults(self):
        """Test PollingStrategy default values."""
        strategy = PollingStrategy()

        assert strategy.queued_interval == 60
        assert strategy.starting_interval == 30
        assert strategy.active_interval == 15
        assert strategy.completing_interval == 10
        assert strategy.max_interval == 300
        assert strategy.backoff_multiplier == 1.5
        assert strategy.completion_threshold_ratio == 0.8
        assert strategy.max_concurrent_workflows == 10

    def test_get_interval_for_phase(self):
        """Test getting intervals for different phases."""
        strategy = PollingStrategy()

        assert strategy.get_interval_for_phase(WorkflowPhase.QUEUED) == 60
        assert strategy.get_interval_for_phase(WorkflowPhase.STARTING) == 30
        assert strategy.get_interval_for_phase(WorkflowPhase.ACTIVE) == 15
        assert strategy.get_interval_for_phase(WorkflowPhase.COMPLETING) == 10
        assert strategy.get_interval_for_phase(WorkflowPhase.COMPLETED) == 0

    def test_custom_polling_strategy(self):
        """Test custom PollingStrategy configuration."""
        strategy = PollingStrategy(
            queued_interval=120, active_interval=5, max_interval=600
        )

        assert strategy.queued_interval == 120
        assert strategy.active_interval == 5
        assert strategy.max_interval == 600
        # Other values should remain default
        assert strategy.starting_interval == 30


class TestIntelligentPollingManager:
    """Test IntelligentPollingManager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = PollingStrategy()
        self.manager = IntelligentPollingManager(self.strategy)

        # Create sample workflow runs
        self.queued_workflow = WorkflowRun(
            id=1,
            name="test-workflow",
            status="queued",
            conclusion=None,
            html_url="https://github.com/test/repo/actions/runs/1",
            created_at="2023-01-01T10:00:00Z",
            updated_at="2023-01-01T10:00:00Z",
            head_sha="abc123",
            duration_seconds=None,
        )

        self.active_workflow = WorkflowRun(
            id=2,
            name="test-workflow",
            status="in_progress",
            conclusion=None,
            html_url="https://github.com/test/repo/actions/runs/2",
            created_at="2023-01-01T10:00:00Z",
            updated_at="2023-01-01T10:05:00Z",
            head_sha="abc123",
            duration_seconds=None,
        )

        self.completed_workflow = WorkflowRun(
            id=3,
            name="test-workflow",
            status="completed",
            conclusion="success",
            html_url="https://github.com/test/repo/actions/runs/3",
            created_at="2023-01-01T10:00:00Z",
            updated_at="2023-01-01T10:10:00Z",
            head_sha="abc123",
            duration_seconds=600,
        )

    def test_manager_initialization(self):
        """Test IntelligentPollingManager initialization."""
        manager = IntelligentPollingManager()

        assert isinstance(manager.strategy, PollingStrategy)
        assert len(manager.workflow_histories) == 0
        assert len(manager.active_workflows) == 0
        assert len(manager.workflow_phases) == 0

    def test_analyze_workflow_phase_queued(self):
        """Test phase analysis for queued workflow."""
        phase = self.manager.analyze_workflow_phase(self.queued_workflow)
        assert phase == WorkflowPhase.QUEUED

    def test_analyze_workflow_phase_completed(self):
        """Test phase analysis for completed workflow."""
        phase = self.manager.analyze_workflow_phase(self.completed_workflow)
        assert phase == WorkflowPhase.COMPLETED

    def test_analyze_workflow_phase_active_no_history(self):
        """Test phase analysis for active workflow without history."""
        phase = self.manager.analyze_workflow_phase(self.active_workflow)
        assert phase == WorkflowPhase.ACTIVE

    def test_analyze_workflow_phase_with_history(self):
        """Test phase analysis using historical data."""
        # Add historical data
        history = WorkflowHistory("test-workflow")
        history.typical_duration_seconds = 600  # 10 minutes typical duration
        self.manager.workflow_histories["test-workflow"] = history

        # Test workflow that started very recently (should be STARTING)
        # Use a time that's clearly within the 10% threshold (< 60 seconds for 600s duration)
        with patch("github_intelligent_polling.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 10, 5, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromisoformat = datetime.fromisoformat

            workflow = WorkflowRun(
                id=4,
                name="test-workflow",
                status="in_progress",
                conclusion=None,
                html_url="https://github.com/test/repo/actions/runs/4",
                created_at="2023-01-01T10:04:30Z",  # 30 seconds ago (5% of 600s)
                updated_at="2023-01-01T10:05:00Z",
                head_sha="abc123",
                duration_seconds=None,
            )

            phase = self.manager.analyze_workflow_phase(workflow)
            assert phase == WorkflowPhase.STARTING

        # Test workflow that started long ago (should be COMPLETING)
        # Use a time that's clearly within the completion threshold (> 80% of 600s = > 480s)
        with patch("github_intelligent_polling.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 10, 5, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromisoformat = datetime.fromisoformat

            workflow.created_at = (
                "2023-01-01T09:56:00Z"  # 9 minutes ago (540s = 90% of 600s)
            )
            phase = self.manager.analyze_workflow_phase(workflow)
            assert phase == WorkflowPhase.COMPLETING

    def test_update_workflow_history(self):
        """Test updating workflow history."""
        self.manager.update_workflow_history(self.completed_workflow)

        assert "test-workflow" in self.manager.workflow_histories
        history = self.manager.workflow_histories["test-workflow"]
        assert history.last_seen_status == "completed"
        assert history.last_seen_conclusion == "success"
        assert 600 in history.duration_samples
        assert history.typical_duration_seconds == 600

    def test_get_next_poll_interval_queued(self):
        """Test polling interval for queued workflow."""
        interval = self.manager.get_next_poll_interval(self.queued_workflow)
        assert interval == self.strategy.queued_interval

    def test_get_next_poll_interval_active(self):
        """Test polling interval for active workflow."""
        interval = self.manager.get_next_poll_interval(self.active_workflow)
        assert interval == self.strategy.active_interval

    def test_apply_backoff(self):
        """Test applying exponential backoff."""
        workflow_id = 1

        # Initial backoff should be 1.0
        assert self.manager.backoff_multipliers.get(workflow_id, 1.0) == 1.0

        # Apply backoff
        self.manager.apply_backoff(workflow_id)
        assert self.manager.backoff_multipliers[workflow_id] == 1.5

        # Apply again
        self.manager.apply_backoff(workflow_id)
        assert self.manager.backoff_multipliers[workflow_id] == 2.25

    def test_reset_backoff(self):
        """Test resetting backoff."""
        workflow_id = 1

        # Apply some backoff
        self.manager.apply_backoff(workflow_id)
        self.manager.apply_backoff(workflow_id)
        assert self.manager.backoff_multipliers[workflow_id] > 1.0

        # Reset backoff
        self.manager.reset_backoff(workflow_id)
        assert self.manager.backoff_multipliers[workflow_id] == 1.0

    @patch("github_intelligent_polling.datetime")
    def test_should_poll_workflow_time_based(self, mock_datetime):
        """Test time-based polling decisions."""
        # Set up mock time
        base_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = base_time

        # First poll should always return True
        assert self.manager.should_poll_workflow(self.active_workflow) is True

        # Record poll time
        self.manager.record_poll_time(self.active_workflow.id)

        # Immediately after polling, should return False
        assert self.manager.should_poll_workflow(self.active_workflow) is False

        # After enough time has passed, should return True
        mock_datetime.now.return_value = base_time + timedelta(seconds=20)
        assert self.manager.should_poll_workflow(self.active_workflow) is True

    def test_should_poll_workflow_completed(self):
        """Test polling decisions for completed workflows."""
        # First time seeing completed workflow should poll
        assert self.manager.should_poll_workflow(self.completed_workflow) is True

        # After updating history, should not poll again
        self.manager.update_workflow_history(self.completed_workflow)
        assert self.manager.should_poll_workflow(self.completed_workflow) is False

    def test_get_workflows_to_poll(self):
        """Test getting workflows that should be polled."""
        workflows = [
            self.queued_workflow,
            self.active_workflow,
            self.completed_workflow,
        ]

        # All workflows should be polled initially
        to_poll = self.manager.get_workflows_to_poll(workflows)
        assert len(to_poll) == 3

        # After updating completed workflow, it shouldn't be polled again
        self.manager.update_workflow_history(self.completed_workflow)
        to_poll = self.manager.get_workflows_to_poll(workflows)
        assert len(to_poll) == 2
        assert self.completed_workflow not in to_poll

    def test_get_workflows_to_poll_priority(self):
        """Test workflow polling priority."""
        # Create many workflows to test priority
        workflows = []
        for i in range(15):  # More than max_concurrent_workflows
            workflow = WorkflowRun(
                id=i,
                name=f"workflow-{i}",
                status="in_progress",
                conclusion=None,
                html_url=f"https://github.com/test/repo/actions/runs/{i}",
                created_at="2023-01-01T10:00:00Z",
                updated_at="2023-01-01T10:05:00Z",
                head_sha="abc123",
                duration_seconds=None,
            )
            workflows.append(workflow)

        to_poll = self.manager.get_workflows_to_poll(workflows)

        # Should be limited to max_concurrent_workflows
        assert len(to_poll) <= self.strategy.max_concurrent_workflows

    def test_cleanup_completed_workflows(self):
        """Test cleanup of completed workflows."""
        # Add some workflows to tracking
        self.manager.active_workflows[1] = self.queued_workflow
        self.manager.active_workflows[3] = self.completed_workflow
        self.manager.workflow_phases[1] = WorkflowPhase.QUEUED
        self.manager.workflow_phases[3] = WorkflowPhase.COMPLETED

        # Cleanup should remove completed workflows
        self.manager.cleanup_completed_workflows()

        assert 1 in self.manager.active_workflows  # Queued workflow remains
        assert 3 not in self.manager.active_workflows  # Completed workflow removed
        assert 1 in self.manager.workflow_phases
        assert 3 not in self.manager.workflow_phases

    def test_get_polling_statistics(self):
        """Test getting polling statistics."""
        # Add some workflows to tracking
        self.manager.active_workflows[1] = self.queued_workflow
        self.manager.active_workflows[2] = self.active_workflow
        self.manager.workflow_phases[1] = WorkflowPhase.QUEUED
        self.manager.workflow_phases[2] = WorkflowPhase.ACTIVE
        self.manager.backoff_multipliers[1] = 1.5
        self.manager.backoff_multipliers[2] = 2.0

        stats = self.manager.get_polling_statistics()

        assert stats["active_workflows"] == 2
        assert stats["phase_distribution"]["queued"] == 1
        assert stats["phase_distribution"]["active"] == 1
        assert stats["average_backoff"] == 1.75  # (1.5 + 2.0) / 2

    def test_estimate_completion_time(self):
        """Test completion time estimation."""
        # Add historical data
        history = WorkflowHistory("test-workflow")
        history.typical_duration_seconds = 600  # 10 minutes typical duration
        self.manager.workflow_histories["test-workflow"] = history

        # Test workflow that started 2 minutes ago
        with patch("github_intelligent_polling.datetime") as mock_datetime:
            mock_now = datetime(2023, 1, 1, 10, 5, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromisoformat = datetime.fromisoformat

            workflow = WorkflowRun(
                id=4,
                name="test-workflow",
                status="in_progress",
                conclusion=None,
                html_url="https://github.com/test/repo/actions/runs/4",
                created_at="2023-01-01T10:03:00Z",  # 2 minutes ago
                updated_at="2023-01-01T10:05:00Z",
                head_sha="abc123",
                duration_seconds=None,
            )

            estimated = self.manager.estimate_completion_time(workflow)
            assert estimated == 480  # 600 - 120 = 480 seconds remaining

        # Test completed workflow
        estimated = self.manager.estimate_completion_time(self.completed_workflow)
        assert estimated == 0

        # Test workflow without history
        workflow.name = "unknown-workflow"
        estimated = self.manager.estimate_completion_time(workflow)
        assert estimated is None


class TestFactoryFunction:
    """Test factory function."""

    def test_create_intelligent_polling_manager_default(self):
        """Test creating manager with default strategy."""
        manager = create_intelligent_polling_manager()

        assert isinstance(manager, IntelligentPollingManager)
        assert isinstance(manager.strategy, PollingStrategy)

    def test_create_intelligent_polling_manager_custom(self):
        """Test creating manager with custom strategy."""
        custom_strategy = PollingStrategy(active_interval=5)
        manager = create_intelligent_polling_manager(custom_strategy)

        assert isinstance(manager, IntelligentPollingManager)
        assert manager.strategy.active_interval == 5


if __name__ == "__main__":
    pytest.main([__file__])
