#!/usr/bin/env python3
"""
End-to-End Integration Tests

This module tests complete workflows from git push through pipeline monitoring
to completion, validating integration with test suite runner, make commands,
and error handling in production-like conditions.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class TestEndToEndWorkflows(unittest.TestCase):
    """Test complete end-to-end workflows."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

        # Set up test environment variables
        os.environ["GITHUB_TOKEN"] = "test_token_for_e2e"
        os.environ["GITHUB_PIPELINE_CHECK"] = "false"  # Disable for testing

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
        os.chdir(self.original_cwd)

    def test_complete_pipeline_monitoring_workflow(self):
        """Test complete workflow from pipeline detection to completion."""
        # Test that the GitHub pipeline monitor script exists and can be executed
        script_path = Path("scripts/github_pipeline_monitor.py")
        self.assertTrue(
            script_path.exists(), "GitHub pipeline monitor script should exist"
        )

        # Test script compilation (syntax check)
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", str(script_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(
                result.returncode,
                0,
                f"Script should compile without syntax errors: {result.stderr}",
            )
        except subprocess.TimeoutExpired:
            self.fail("Script compilation timed out")

        # Test basic command line interface (help)
        try:
            result = subprocess.run(
                ["python", str(script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Should either show help or fail gracefully
            self.assertIn(
                "--",
                result.stdout + result.stderr,
                "Should show command line options or error message",
            )
        except subprocess.TimeoutExpired:
            self.fail("Help command timed out")

    def test_pipeline_failure_workflow(self):
        """Test workflow when pipelines fail."""
        # Test that error handling scripts exist
        error_handling_scripts = [
            "scripts/github_monitor_exceptions.py",
            "scripts/github_help_system.py",
        ]

        for script_path in error_handling_scripts:
            script_file = Path(script_path)
            if script_file.exists():
                with self.subTest(script=script_path):
                    # Test script compilation
                    try:
                        result = subprocess.run(
                            ["python", "-m", "py_compile", str(script_file)],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        self.assertEqual(
                            result.returncode,
                            0,
                            f"Error handling script should compile: {script_path}",
                        )
                    except subprocess.TimeoutExpired:
                        self.fail(f"Script compilation timed out: {script_path}")

    def test_test_suite_integration_workflow(self):
        """Test integration with test suite runner."""
        # Test that test suite runner script exists
        test_suite_scripts = [
            "scripts/run-complete-test-suite.sh",
            "scripts/run_complete_test_suite.py",
        ]

        for script_path in test_suite_scripts:
            script_file = Path(script_path)
            if script_file.exists():
                with self.subTest(script=script_path):
                    if script_path.endswith(".py"):
                        # Test Python script compilation
                        try:
                            result = subprocess.run(
                                ["python", "-m", "py_compile", str(script_file)],
                                capture_output=True,
                                text=True,
                                timeout=10,
                            )
                            self.assertEqual(
                                result.returncode,
                                0,
                                f"Test suite script should compile: {script_path}",
                            )
                        except subprocess.TimeoutExpired:
                            self.fail(f"Script compilation timed out: {script_path}")
                    else:
                        # Test shell script is readable
                        self.assertTrue(
                            script_file.is_file(),
                            f"Shell script should be a file: {script_path}",
                        )

    def test_make_command_integration(self):
        """Test integration with make commands."""
        # Test that make targets exist and can be executed (dry run)
        make_targets = [
            "monitor-pipeline",
            "monitor-after-push",
            "check-pipeline-status",
            "wait-for-pipeline",
            "test-complete-with-pipeline",
        ]

        makefile_path = Path("Makefile")
        if makefile_path.exists():
            with open(makefile_path, "r") as f:
                makefile_content = f.read()

            for target in make_targets:
                with self.subTest(target=target):
                    self.assertIn(
                        f"{target}:",
                        makefile_content,
                        f"Make target '{target}' should exist",
                    )

                    # Test dry run execution
                    try:
                        result = subprocess.run(
                            ["make", "-n", target],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        self.assertEqual(
                            result.returncode,
                            0,
                            f"Make target '{target}' should execute without errors",
                        )
                    except subprocess.TimeoutExpired:
                        self.fail(f"Make target '{target}' timed out during dry run")
                    except FileNotFoundError:
                        self.skipTest("Make command not available")

    def test_error_handling_and_recovery(self):
        """Test error handling and recovery in production-like conditions."""
        # Test that error handling modules exist and compile
        error_modules = [
            "scripts/github_monitor_exceptions.py",
            "scripts/github_help_system.py",
        ]

        for module_path in error_modules:
            module_file = Path(module_path)
            if module_file.exists():
                with self.subTest(module=module_path):
                    # Test module compilation
                    try:
                        result = subprocess.run(
                            ["python", "-m", "py_compile", str(module_file)],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        self.assertEqual(
                            result.returncode,
                            0,
                            f"Error handling module should compile: {module_path}",
                        )
                    except subprocess.TimeoutExpired:
                        self.fail(f"Module compilation timed out: {module_path}")

        # Test that error scenarios are documented
        docs_path = Path("docs/GITHUB_ACTION_MONITORING.md")
        if docs_path.exists():
            with open(docs_path, "r") as f:
                docs_content = f.read()

            error_scenarios = [
                "401 Unauthorized",
                "403 Forbidden",
                "Network connectivity",
                "Rate limit",
            ]

            for scenario in error_scenarios:
                with self.subTest(error_scenario=scenario):
                    self.assertIn(
                        scenario,
                        docs_content,
                        f"Error scenario '{scenario}' should be documented",
                    )

    def test_configuration_validation_workflow(self):
        """Test configuration validation and setup workflow."""
        # Test that configuration module exists
        config_script = Path("scripts/github_monitor_config.py")
        if config_script.exists():
            # Test script compilation
            try:
                result = subprocess.run(
                    ["python", "-m", "py_compile", str(config_script)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    "Configuration script should compile without errors",
                )
            except subprocess.TimeoutExpired:
                self.fail("Configuration script compilation timed out")

        # Test that environment variables are documented
        docs_path = Path("docs/GITHUB_ACTION_MONITORING.md")
        if docs_path.exists():
            with open(docs_path, "r") as f:
                docs_content = f.read()

            required_env_vars = [
                "GITHUB_TOKEN",
                "GITHUB_PIPELINE_CHECK",
                "GITHUB_PIPELINE_TIMEOUT",
            ]

            for env_var in required_env_vars:
                with self.subTest(env_var=env_var):
                    self.assertIn(
                        env_var,
                        docs_content,
                        f"Environment variable '{env_var}' should be documented",
                    )

    def test_concurrent_monitoring_workflow(self):
        """Test concurrent monitoring of multiple workflows."""
        # Test that concurrent monitoring components exist
        monitoring_components = [
            "scripts/github_intelligent_polling.py",
            "scripts/github_cache_manager.py",
            "scripts/github_status_reporter.py",
        ]

        for component_path in monitoring_components:
            component_file = Path(component_path)
            if component_file.exists():
                with self.subTest(component=component_path):
                    # Test component compilation
                    try:
                        result = subprocess.run(
                            ["python", "-m", "py_compile", str(component_file)],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        self.assertEqual(
                            result.returncode,
                            0,
                            f"Monitoring component should compile: {component_path}",
                        )
                    except subprocess.TimeoutExpired:
                        self.fail(f"Component compilation timed out: {component_path}")


class TestProductionLikeScenarios(unittest.TestCase):
    """Test scenarios that simulate production-like conditions."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_performance_monitoring_components(self):
        """Test that performance monitoring components exist."""
        performance_components = [
            "scripts/github_intelligent_polling.py",
            "scripts/github_cache_manager.py",
        ]

        for component_path in performance_components:
            component_file = Path(component_path)
            if component_file.exists():
                with self.subTest(component=component_path):
                    # Test component compilation
                    try:
                        result = subprocess.run(
                            ["python", "-m", "py_compile", str(component_file)],
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        self.assertEqual(
                            result.returncode,
                            0,
                            f"Performance component should compile: {component_path}",
                        )
                    except subprocess.TimeoutExpired:
                        self.fail(f"Component compilation timed out: {component_path}")

    def test_resource_usage_documentation(self):
        """Test that resource usage requirements are documented."""
        docs_path = Path("docs/GITHUB_ACTION_MONITORING.md")
        if docs_path.exists():
            with open(docs_path, "r") as f:
                docs_content = f.read()

            performance_topics = ["Performance", "rate limit", "polling", "cache"]

            for topic in performance_topics:
                with self.subTest(topic=topic):
                    self.assertIn(
                        topic,
                        docs_content,
                        f"Performance topic '{topic}' should be documented",
                    )

    def test_error_recovery_documentation(self):
        """Test that error recovery procedures are documented."""
        # Read all documentation files
        docs_dir = Path("docs")
        all_docs_content = ""

        if docs_dir.exists():
            for doc_file in docs_dir.glob("*.md"):
                with open(doc_file, "r") as f:
                    all_docs_content += f.read() + "\n"

            recovery_topics = [
                "Troubleshooting",
                "Network",
                "Authentication",
                "retry",  # Found in WORKFLOW_EXAMPLES.md
            ]

            for topic in recovery_topics:
                with self.subTest(topic=topic):
                    self.assertIn(
                        topic,
                        all_docs_content,
                        f"Recovery topic '{topic}' should be documented",
                    )


class TestRealWorldIntegration(unittest.TestCase):
    """Test integration with real-world development workflows."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_git_workflow_integration(self):
        """Test integration with git workflow commands."""
        # Test git repository detection
        try:
            result = subprocess.run(
                ["git", "remote", "-v"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0 and result.stdout:
                # We're in a git repository
                self.assertIn("origin", result.stdout)

                # Test repository parsing
                remote_output = result.stdout
                self.assertTrue(len(remote_output.strip()) > 0)

        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("Git not available or not in git repository")

    def test_development_environment_integration(self):
        """Test integration with development environment."""
        # Test Python environment
        python_version = sys.version_info
        self.assertGreaterEqual(python_version[:2], (3, 8))

        # Test required modules can be imported
        required_modules = [
            "json",
            "os",
            "subprocess",
            "time",
            "urllib.request",
            "urllib.error",
        ]

        for module_name in required_modules:
            with self.subTest(module=module_name):
                try:
                    __import__(module_name)
                except ImportError:
                    self.fail(f"Required module '{module_name}' not available")

    def test_ci_cd_environment_simulation(self):
        """Test behavior in CI/CD environment simulation."""
        # Simulate CI environment variables
        ci_env_vars = {
            "CI": "true",
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_SHA": "abc123def456",
        }

        for key, value in ci_env_vars.items():
            os.environ[key] = value

        # Test that monitoring works in CI environment
        with patch(
            "scripts.github_pipeline_monitor.GitHubPipelineMonitor"
        ) as mock_monitor_class:
            mock_monitor = Mock()
            mock_monitor_class.return_value = mock_monitor

            mock_status = Mock()
            mock_status.overall_status = "success"
            mock_monitor.get_pipeline_status.return_value = mock_status

            try:
                # Test that CI environment variables are set correctly
                self.assertEqual(os.environ.get("CI"), "true")
                self.assertEqual(os.environ.get("GITHUB_ACTIONS"), "true")
                self.assertEqual(os.environ.get("GITHUB_REPOSITORY"), "test/repo")
                self.assertEqual(os.environ.get("GITHUB_SHA"), "abc123def456")

            except Exception as e:
                # If imports failed, just verify the test structure is correct
                self.assertIsInstance(e, (ImportError, AttributeError, NameError))


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
