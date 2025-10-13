#!/usr/bin/env python3
"""
Tests for Make Command Integration

This module tests the integration of GitHub Action monitoring with make commands,
including new pipeline monitoring targets and enhanced quality gates.
"""

import os
import subprocess
import unittest

import pytest


@pytest.mark.skipif(
    os.name == "nt",
    reason="Windows make/subprocess issues - TODO: fix Windows compatibility",
)
class TestMakeTargetExistence(unittest.TestCase):
    """Test that all expected make targets exist and are properly defined."""

    def setUp(self):
        """Set up test environment."""
        self.makefile_path = "Makefile"

    def test_makefile_exists(self):
        """Test that Makefile exists."""
        self.assertTrue(os.path.exists(self.makefile_path), "Makefile should exist")

    def test_pipeline_monitoring_targets_exist(self):
        """Test that all pipeline monitoring make targets are defined."""
        expected_targets = [
            "monitor-pipeline",
            "monitor-after-push",
            "check-pipeline-status",
            "wait-for-pipeline",
            "wait-for-pipeline-extended",
        ]

        # Read Makefile content
        with open(self.makefile_path, "r") as f:
            makefile_content = f.read()

        for target in expected_targets:
            with self.subTest(target=target):
                self.assertIn(
                    f"{target}:",
                    makefile_content,
                    f"Make target '{target}' should be defined in Makefile",
                )

    def test_enhanced_quality_gate_targets_exist(self):
        """Test that enhanced quality gate targets are defined."""
        expected_targets = [
            "test-complete-with-pipeline",
            "test-complete-wait-pipeline",
            "test-complete-bypass-pipeline",
            "quality-gate-full",
            "ci-full",
            "pre-push-full",
        ]

        # Read Makefile content
        with open(self.makefile_path, "r") as f:
            makefile_content = f.read()

        for target in expected_targets:
            with self.subTest(target=target):
                self.assertIn(
                    f"{target}:",
                    makefile_content,
                    f"Enhanced target '{target}' should be defined in Makefile",
                )

    def test_help_target_includes_pipeline_commands(self):
        """Test that help target includes pipeline monitoring commands."""
        result = subprocess.run(["make", "help"], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Make help should execute successfully")

        expected_help_sections = [
            "Pipeline Monitoring:",
            "monitor-pipeline",
            "monitor-after-push",
            "check-pipeline-status",
            "wait-for-pipeline",
        ]

        for section in expected_help_sections:
            with self.subTest(section=section):
                self.assertIn(
                    section, result.stdout, f"Help should include '{section}'"
                )


class TestMakeTargetExecution(unittest.TestCase):
    """Test execution of make targets with mocked dependencies."""

    def setUp(self):
        """Set up test environment with mocks."""
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_monitor_pipeline_target(self):
        """Test monitor-pipeline make target execution."""
        # Test dry run to see what command would be executed
        result = subprocess.run(
            ["make", "-n", "monitor-pipeline"], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "github_pipeline_monitor.py",
            result.stdout,
            "Should call pipeline monitor script",
        )
        self.assertIn("--status-only", result.stdout, "Should use status-only flag")
        self.assertIn("--repo", result.stdout, "Should specify repository")

    def test_monitor_after_push_target(self):
        """Test monitor-after-push make target execution."""
        # Test dry run
        result = subprocess.run(
            ["make", "-n", "monitor-after-push"], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "github_pipeline_monitor.py",
            result.stdout,
            "Should call pipeline monitor script",
        )
        self.assertIn("--after-push", result.stdout, "Should use after-push flag")
        self.assertIn(
            "--branch pre-release", result.stdout, "Should specify pre-release branch"
        )

    def test_check_pipeline_status_target(self):
        """Test check-pipeline-status make target execution."""
        # Test dry run
        result = subprocess.run(
            ["make", "-n", "check-pipeline-status"], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "github_pipeline_monitor.py",
            result.stdout,
            "Should call pipeline monitor script",
        )
        self.assertIn("--status-only", result.stdout, "Should use status-only flag")
        self.assertIn("--format minimal", result.stdout, "Should use minimal format")

    def test_wait_for_pipeline_target(self):
        """Test wait-for-pipeline make target execution."""
        # Test dry run
        result = subprocess.run(
            ["make", "-n", "wait-for-pipeline"], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "github_pipeline_monitor.py",
            result.stdout,
            "Should call pipeline monitor script",
        )
        self.assertIn("--repo", result.stdout, "Should specify repository")
        # Should not have --status-only (waits for completion)
        self.assertNotIn(
            "--status-only",
            result.stdout,
            "Should not use status-only flag for waiting",
        )


@pytest.mark.skipif(
    os.name == "nt",
    reason="Windows make/subprocess issues - TODO: fix Windows compatibility",
)
class TestEnhancedQualityGates(unittest.TestCase):
    """Test enhanced quality gate targets with pipeline integration."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_quality_gate_full_without_pipeline_check(self):
        """Test quality-gate-full target without pipeline checking enabled."""
        # Ensure pipeline checking is disabled
        os.environ.pop("ENABLE_PIPELINE_CHECK", None)

        # Test dry run
        result = subprocess.run(
            ["make", "-n", "quality-gate-full"], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "run-complete-test-suite.sh", result.stdout, "Should call test suite runner"
        )
        # Should include the conditional logic but not execute pipeline checking
        self.assertIn(
            "Pipeline checking disabled",
            result.stdout,
            "Should indicate pipeline checking is disabled",
        )
        self.assertIn(
            "--verbose",
            result.stdout,
            "Should call test suite with verbose flag when disabled",
        )

    def test_quality_gate_full_with_pipeline_check(self):
        """Test quality-gate-full target with pipeline checking enabled."""
        # Enable pipeline checking
        os.environ["ENABLE_PIPELINE_CHECK"] = "true"

        # Test dry run
        result = subprocess.run(
            ["make", "-n", "quality-gate-full"], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "run-complete-test-suite.sh", result.stdout, "Should call test suite runner"
        )
        self.assertIn(
            "--check-pipeline",
            result.stdout,
            "Should include pipeline checking when enabled",
        )

    def test_ci_full_without_pipeline_check(self):
        """Test ci-full target without pipeline checking."""
        # Ensure pipeline checking is disabled
        os.environ.pop("ENABLE_PIPELINE_CHECK", None)

        # Test dry run
        result = subprocess.run(
            ["make", "-n", "ci-full"], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "Remote pipeline checking disabled",
            result.stdout,
            "Should indicate pipeline checking is disabled",
        )

    def test_ci_full_with_pipeline_check(self):
        """Test ci-full target with pipeline checking enabled."""
        # Enable pipeline checking
        os.environ["ENABLE_PIPELINE_CHECK"] = "true"

        # Test dry run
        result = subprocess.run(
            ["make", "-n", "ci-full"], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "github_pipeline_monitor.py",
            result.stdout,
            "Should call pipeline monitor when enabled",
        )
        self.assertIn("--status-only", result.stdout, "Should check pipeline status")

    def test_pre_push_full_with_pipeline_check(self):
        """Test pre-push-full target with pipeline checking."""
        # Enable pipeline checking
        os.environ["ENABLE_PIPELINE_CHECK"] = "true"

        # Test dry run
        result = subprocess.run(
            ["make", "-n", "pre-push-full"], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "github_pipeline_monitor.py", result.stdout, "Should call pipeline monitor"
        )
        self.assertIn(
            "--status-only", result.stdout, "Should check current pipeline status"
        )


class TestPipelineIntegratedTargets(unittest.TestCase):
    """Test targets that integrate pipeline checking with test suite."""

    def test_test_complete_with_pipeline_target(self):
        """Test test-complete-with-pipeline target."""
        # Test dry run
        result = subprocess.run(
            ["make", "-n", "test-complete-with-pipeline"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "run-complete-test-suite.sh", result.stdout, "Should call test suite runner"
        )
        self.assertIn(
            "--check-pipeline", result.stdout, "Should include pipeline checking"
        )

    def test_test_complete_wait_pipeline_target(self):
        """Test test-complete-wait-pipeline target."""
        # Test dry run
        result = subprocess.run(
            ["make", "-n", "test-complete-wait-pipeline"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "run-complete-test-suite.sh", result.stdout, "Should call test suite runner"
        )
        self.assertIn(
            "--check-pipeline", result.stdout, "Should include pipeline checking"
        )
        self.assertIn(
            "--pipeline-wait", result.stdout, "Should include pipeline wait option"
        )

    def test_test_complete_bypass_pipeline_target(self):
        """Test test-complete-bypass-pipeline target (emergency mode)."""
        # Test dry run
        result = subprocess.run(
            ["make", "-n", "test-complete-bypass-pipeline"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        self.assertIn(
            "run-complete-test-suite.sh", result.stdout, "Should call test suite runner"
        )
        self.assertIn(
            "--check-pipeline", result.stdout, "Should include pipeline checking"
        )
        self.assertIn(
            "--pipeline-bypass", result.stdout, "Should include pipeline bypass option"
        )


@pytest.mark.skipif(
    os.name == "nt",
    reason="Windows make/subprocess issues - TODO: fix Windows compatibility",
)
class TestMakeTargetErrorHandling(unittest.TestCase):
    """Test error handling in make targets."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_pipeline_failure_blocks_ci_full(self):
        """Test that pipeline failures block ci-full target."""
        # Enable pipeline checking
        os.environ["ENABLE_PIPELINE_CHECK"] = "true"

        # Test dry run to see the conditional logic
        result = subprocess.run(
            ["make", "-n", "ci-full"], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, "Make -n should show command structure")
        self.assertIn(
            "github_pipeline_monitor.py",
            result.stdout,
            "Should include pipeline monitor call",
        )
        self.assertIn(
            "|| \\",
            result.stdout,
            "Should include error handling logic with line continuation",
        )
        self.assertIn(
            "exit 1", result.stdout, "Should exit with error code on pipeline failure"
        )
        self.assertIn(
            "Remote pipelines failed", result.stdout, "Should include failure message"
        )

    def test_repository_detection_in_make_targets(self):
        """Test that make targets properly detect repository information."""
        # Test dry run to see repository detection logic
        result = subprocess.run(
            ["make", "-n", "monitor-pipeline"], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, "Make -n should execute successfully")
        # The Makefile resolves the repository at build time, so we should see the resolved repo
        self.assertIn(
            "--repo", result.stdout, "Should pass repository to pipeline monitor"
        )
        # Should see the actual repository name (resolved by make)
        self.assertIn(
            "stabbotco1/mypylogger",
            result.stdout,
            "Should include resolved repository name",
        )


@pytest.mark.skipif(
    os.name == "nt",
    reason="Windows make/subprocess issues - TODO: fix Windows compatibility",
)
class TestMakeTargetBackwardCompatibility(unittest.TestCase):
    """Test that new make targets don't break existing functionality."""

    def test_existing_targets_still_work(self):
        """Test that existing make targets are not broken by new additions."""
        existing_targets = [
            "help",
            "test-fast",
            "test-coverage",
            "lint",
            "format",
            "build",
            "clean",
        ]

        for target in existing_targets:
            with self.subTest(target=target):
                # Test dry run to ensure target exists and is valid
                result = subprocess.run(
                    ["make", "-n", target], capture_output=True, text=True
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    f"Existing target '{target}' should still work",
                )

    def test_default_behavior_unchanged(self):
        """Test that default make behavior is unchanged."""
        # Test that make without arguments shows help
        result = subprocess.run(["make"], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Default make should show help")
        self.assertIn(
            "mypylogger Development Commands",
            result.stdout,
            "Should show help by default",
        )

    def test_environment_variable_optional(self):
        """Test that ENABLE_PIPELINE_CHECK is optional and defaults work."""
        # Ensure environment variable is not set
        os.environ.pop("ENABLE_PIPELINE_CHECK", None)

        # Test that enhanced targets work without the environment variable
        enhanced_targets = ["quality-gate-full", "ci-full", "pre-push-full"]

        for target in enhanced_targets:
            with self.subTest(target=target):
                result = subprocess.run(
                    ["make", "-n", target], capture_output=True, text=True
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    f"Enhanced target '{target}' should work without env var",
                )
                self.assertIn(
                    "disabled",
                    result.stdout,
                    f"Should indicate pipeline checking is disabled for '{target}'",
                )


class TestMakeTargetDocumentation(unittest.TestCase):
    """Test that make targets are properly documented."""

    def test_help_target_completeness(self):
        """Test that help target includes all new functionality."""
        result = subprocess.run(["make", "help"], capture_output=True, text=True)

        self.assertEqual(result.returncode, 0, "Make help should execute successfully")

        # Check for pipeline monitoring section
        self.assertIn(
            "Pipeline Monitoring:",
            result.stdout,
            "Help should include Pipeline Monitoring section",
        )

        # Check for environment variables section
        self.assertIn(
            "Environment Variables:",
            result.stdout,
            "Help should include Environment Variables section",
        )

        # Check for ENABLE_PIPELINE_CHECK documentation
        self.assertIn(
            "ENABLE_PIPELINE_CHECK",
            result.stdout,
            "Help should document ENABLE_PIPELINE_CHECK variable",
        )

    def test_target_descriptions_accurate(self):
        """Test that target descriptions in help are accurate."""
        result = subprocess.run(["make", "help"], capture_output=True, text=True)

        expected_descriptions = [
            ("monitor-pipeline", "Monitor current commit's pipeline status"),
            ("monitor-after-push", "Monitor pipeline after push to pre-release"),
            ("check-pipeline-status", "Quick pipeline status check"),
            ("wait-for-pipeline", "Wait for pipeline completion with timeout"),
        ]

        for target, description in expected_descriptions:
            with self.subTest(target=target):
                # Find the line with the target
                lines = result.stdout.split("\n")
                target_line = next((line for line in lines if target in line), None)

                self.assertIsNotNone(
                    target_line, f"Target '{target}' should be in help"
                )
                assert target_line is not None  # Type narrowing for MyPy
                self.assertIn(
                    description,
                    target_line,
                    f"Target '{target}' should have correct description",
                )


@pytest.mark.skipif(
    os.name == "nt",
    reason="Windows make/subprocess issues - TODO: fix Windows compatibility",
)
class TestMakeTargetIntegrationScenarios(unittest.TestCase):
    """Test realistic integration scenarios."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_development_workflow_scenario(self):
        """Test a complete development workflow using make targets."""
        workflow_targets = [
            "format",  # Format code
            "lint",  # Check linting
            "test-fast",  # Run fast tests
            "monitor-pipeline",  # Check pipeline status
        ]

        for target in workflow_targets:
            with self.subTest(target=target):
                # Test dry run to ensure all targets in workflow exist
                result = subprocess.run(
                    ["make", "-n", target], capture_output=True, text=True
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    f"Workflow target '{target}' should be available",
                )

    def test_ci_workflow_scenario(self):
        """Test CI workflow with pipeline integration."""
        # Enable pipeline checking for CI scenario
        os.environ["ENABLE_PIPELINE_CHECK"] = "true"

        ci_targets = [
            "quality-gate-full",  # Enhanced quality gate
            "ci-full",  # Enhanced CI with pipeline verification
        ]

        for target in ci_targets:
            with self.subTest(target=target):
                result = subprocess.run(
                    ["make", "-n", target], capture_output=True, text=True
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    f"CI target '{target}' should work with pipeline checking",
                )
                # For quality-gate-full, pipeline monitoring is in the test suite runner
                if target == "quality-gate-full":
                    self.assertIn(
                        "--check-pipeline",
                        result.stdout,
                        f"CI target '{target}' should include pipeline checking in test suite",
                    )
                else:
                    self.assertIn(
                        "github_pipeline_monitor.py",
                        result.stdout,
                        f"CI target '{target}' should include pipeline monitoring",
                    )

    def test_emergency_bypass_scenario(self):
        """Test emergency bypass scenario for pipeline issues."""
        # Test emergency bypass target
        result = subprocess.run(
            ["make", "-n", "test-complete-bypass-pipeline"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, "Emergency bypass should be available")
        self.assertIn(
            "--pipeline-bypass",
            result.stdout,
            "Should include bypass option for emergencies",
        )
        self.assertIn(
            "emergency mode",
            result.stdout,
            "Should indicate emergency mode in description",
        )


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
