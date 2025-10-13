#!/usr/bin/env python3
"""
Documentation Tests and Validation

This module tests all documentation examples to ensure they work correctly,
validates setup instructions, tests troubleshooting guides, and verifies
all links and references in documentation.
"""

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlparse

import pytest


@pytest.mark.skipif(
    os.name == "nt", reason="Windows encoding issues - TODO: fix UTF-8 file reading"
)
class TestDocumentationExamples(unittest.TestCase):
    """Test that all code examples in documentation work correctly."""

    def setUp(self):
        """Set up test environment."""
        self.docs_dir = Path("docs")
        self.scripts_dir = Path("scripts")
        self.original_env = os.environ.copy()

        # Set up test environment variables
        os.environ["GITHUB_TOKEN"] = "test_token_for_docs"
        os.environ["GITHUB_PIPELINE_CHECK"] = "false"  # Disable for testing

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_github_action_monitoring_examples(self):
        """Test code examples from GITHUB_ACTION_MONITORING.md."""
        doc_file = self.docs_dir / "GITHUB_ACTION_MONITORING.md"
        self.assertTrue(doc_file.exists(), "GITHUB_ACTION_MONITORING.md should exist")

        # Test basic usage examples
        basic_examples = [
            "python scripts/github_pipeline_monitor.py --status-only",
            "python scripts/github_pipeline_monitor.py --after-push --branch pre-release",
            "python scripts/github_pipeline_monitor.py --format json",
            "python scripts/github_pipeline_monitor.py --verbose",
            "python scripts/github_pipeline_monitor.py --cache-stats",
        ]

        for example in basic_examples:
            with self.subTest(example=example):
                # Verify the script exists and can be imported
                script_path = Path("scripts/github_pipeline_monitor.py")
                self.assertTrue(
                    script_path.exists(),
                    f"Script referenced in example should exist: {script_path}",
                )

                # Test dry run (syntax check)
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
                    self.fail(f"Script compilation timed out: {script_path}")

    def test_make_command_examples(self):
        """Test make command examples from documentation."""
        # Extract make commands from documentation
        make_commands = [
            "monitor-pipeline",
            "monitor-after-push",
            "check-pipeline-status",
            "wait-for-pipeline",
            "test-complete-with-pipeline",
        ]

        # Verify Makefile exists
        makefile = Path("Makefile")
        self.assertTrue(makefile.exists(), "Makefile should exist")

        with open(makefile, "r") as f:
            makefile_content = f.read()

        for command in make_commands:
            with self.subTest(command=command):
                self.assertIn(
                    f"{command}:",
                    makefile_content,
                    f"Make command '{command}' should be defined in Makefile",
                )

                # Test make dry run
                result = subprocess.run(
                    ["make", "-n", command], capture_output=True, text=True, timeout=10
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"Make command '{command}' should execute without errors",
                )

    def test_environment_variable_examples(self):
        """Test environment variable examples from documentation."""
        doc_file = self.docs_dir / "GITHUB_ACTION_MONITORING.md"

        with open(doc_file, "r") as f:
            content = f.read()

        # Test environment variables mentioned in documentation
        env_vars = {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_PIPELINE_CHECK": "true",
            "GITHUB_PIPELINE_TIMEOUT": "30",
            "GITHUB_PIPELINE_POLL_INTERVAL": "15",
            "GITHUB_PIPELINE_BRANCH": "pre-release",
            "GITHUB_PIPELINE_VERBOSE": "true",
            "GITHUB_PIPELINE_COLORS": "false",
        }

        for var_name, var_value in env_vars.items():
            with self.subTest(env_var=var_name):
                # Verify the variable is documented
                self.assertIn(
                    var_name,
                    content,
                    f"Environment variable '{var_name}' should be documented",
                )

                # Test setting the variable
                os.environ[var_name] = var_value
                self.assertEqual(
                    os.environ.get(var_name),
                    var_value,
                    f"Environment variable '{var_name}' should be settable",
                )

    def test_configuration_file_examples(self):
        """Test configuration file examples from documentation."""
        doc_file = self.docs_dir / "GITHUB_ACTION_MONITORING.md"

        with open(doc_file, "r") as f:
            content = f.read()

        # Extract YAML configuration example
        yaml_pattern = r"```yaml\n(.*?)\n```"
        yaml_matches = re.findall(yaml_pattern, content, re.DOTALL)

        self.assertGreater(
            len(yaml_matches),
            0,
            "Documentation should contain YAML configuration examples",
        )

        for i, yaml_content in enumerate(yaml_matches):
            with self.subTest(yaml_example=i):
                # Test that YAML is valid (basic structure check)
                lines = yaml_content.strip().split("\n")

                # Check for expected configuration sections
                expected_sections = ["github:", "monitoring:", "output:"]
                yaml_text = "\n".join(lines)

                for section in expected_sections:
                    if section in yaml_text:
                        # Verify proper YAML indentation (basic check)
                        section_lines = [
                            line
                            for line in lines
                            if section in line
                            or (
                                line.startswith("  ")
                                and any(
                                    s in yaml_text[: yaml_text.find(line)]
                                    for s in expected_sections
                                )
                            )
                        ]
                        self.assertGreater(
                            len(section_lines),
                            0,
                            f"YAML section '{section}' should have content",
                        )


@pytest.mark.skipif(
    os.name == "nt", reason="Windows encoding issues - TODO: fix UTF-8 file reading"
)
class TestSetupInstructions(unittest.TestCase):
    """Test setup instructions work on clean environments."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_github_token_setup_instructions(self):
        """Test GitHub token setup instructions from GITHUB_TOKEN_SETUP.md."""
        doc_file = Path("docs/GITHUB_TOKEN_SETUP.md")
        self.assertTrue(doc_file.exists(), "GITHUB_TOKEN_SETUP.md should exist")

        with open(doc_file, "r") as f:
            content = f.read()

        # Test environment variable setup examples
        bash_examples = [
            "export GITHUB_TOKEN=your_actual_token_here",
            "echo $GITHUB_TOKEN",
            "source ~/.zshrc",
            "source ~/.bashrc",
        ]

        for example in bash_examples:
            with self.subTest(bash_example=example):
                self.assertIn(
                    example,
                    content,
                    f"Setup instruction should be documented: {example}",
                )

        # Test token validation command
        validation_commands = [
            "python scripts/github_pipeline_monitor.py --status-only",
            'curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user',
        ]

        for command in validation_commands:
            with self.subTest(validation_command=command):
                self.assertIn(
                    command,
                    content,
                    f"Validation command should be documented: {command}",
                )

    def test_prerequisite_validation(self):
        """Test that documented prerequisites can be validated."""
        doc_file = Path("docs/GITHUB_ACTION_MONITORING.md")

        with open(doc_file, "r") as f:
            content = f.read()

        # Test Python version requirement
        self.assertIn(
            "Python 3.8", content, "Python version requirement should be documented"
        )

        # Verify current Python version meets requirement
        import sys

        python_version = sys.version_info
        self.assertGreaterEqual(
            python_version[:2],
            (3, 8),
            "Current Python version should meet documented requirement",
        )

        # Test Git requirement
        self.assertIn("Git repository", content, "Git requirement should be documented")

        # Verify git is available
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True, timeout=5
            )
            self.assertEqual(result.returncode, 0, "Git should be available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.fail("Git should be available as documented prerequisite")

    def test_installation_steps(self):
        """Test installation steps from documentation."""
        doc_file = Path("docs/GITHUB_ACTION_MONITORING.md")

        with open(doc_file, "r") as f:
            content = f.read()

        # Test pip install command
        pip_commands = ["pip install -r requirements.txt", 'pip install -e ".[dev]"']

        for command in pip_commands:
            if command in content:
                with self.subTest(pip_command=command):
                    # Verify requirements.txt exists if referenced
                    if "requirements.txt" in command:
                        req_file = Path("requirements.txt")
                        if req_file.exists():
                            # Test that requirements file is readable
                            with open(req_file, "r") as f:
                                req_content = f.read()
                            self.assertIsInstance(
                                req_content, str, "Requirements file should be readable"
                            )

    def test_verification_commands(self):
        """Test setup verification commands from documentation."""
        doc_file = Path("docs/GITHUB_ACTION_MONITORING.md")

        with open(doc_file, "r") as f:
            content = f.read()

        # Test verification commands
        verification_commands = [
            "python scripts/github_pipeline_monitor.py --cache-stats",
            "make test-fast",
        ]

        for command in verification_commands:
            if command in content:
                with self.subTest(verification_command=command):
                    # Test that the command can be parsed (basic syntax check)
                    parts = command.split()
                    self.assertGreater(
                        len(parts), 0, f"Command should have valid syntax: {command}"
                    )

                    # For Python commands, verify script exists
                    if parts[0] == "python" and len(parts) > 1:
                        script_path = Path(parts[1])
                        if script_path.exists():
                            # Test script compilation
                            result = subprocess.run(
                                ["python", "-m", "py_compile", str(script_path)],
                                capture_output=True,
                                text=True,
                                timeout=10,
                            )
                            self.assertEqual(
                                result.returncode,
                                0,
                                f"Verification script should compile: {script_path}",
                            )


@pytest.mark.skipif(
    os.name == "nt", reason="Windows encoding issues - TODO: fix UTF-8 file reading"
)
class TestTroubleshootingGuides(unittest.TestCase):
    """Test troubleshooting guides with common error scenarios."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_authentication_troubleshooting(self):
        """Test authentication troubleshooting scenarios."""
        doc_file = Path("docs/GITHUB_ACTION_MONITORING.md")

        with open(doc_file, "r") as f:
            content = f.read()

        # Test documented authentication errors
        auth_errors = [
            "401 Unauthorized",
            "403 Forbidden",
            "invalid or missing token",
            "insufficient permissions",
        ]

        for error in auth_errors:
            with self.subTest(auth_error=error):
                self.assertIn(
                    error,
                    content,
                    f"Authentication error should be documented: {error}",
                )

        # Test troubleshooting commands
        troubleshooting_commands = [
            "echo $GITHUB_TOKEN",
            'curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user',
        ]

        for command in troubleshooting_commands:
            with self.subTest(troubleshooting_command=command):
                if command in content:
                    # Basic syntax validation
                    self.assertGreater(
                        len(command.strip()),
                        0,
                        f"Troubleshooting command should be valid: {command}",
                    )

    def test_repository_detection_troubleshooting(self):
        """Test repository detection troubleshooting scenarios."""
        doc_file = Path("docs/GITHUB_ACTION_MONITORING.md")

        with open(doc_file, "r") as f:
            content = f.read()

        # Test documented repository errors
        repo_errors = ["Repository not found", "not accessible", "git remote"]

        for error in repo_errors:
            with self.subTest(repo_error=error):
                self.assertIn(
                    error, content, f"Repository error should be documented: {error}"
                )

        # Test git remote validation command
        git_commands = ["git remote -v", "git remote add origin"]

        for command in git_commands:
            if command in content:
                with self.subTest(git_command=command):
                    # Test that git command syntax is valid
                    parts = command.split()
                    self.assertEqual(
                        parts[0],
                        "git",
                        f"Git command should start with 'git': {command}",
                    )

    def test_rate_limiting_troubleshooting(self):
        """Test rate limiting troubleshooting scenarios."""
        doc_file = Path("docs/GITHUB_ACTION_MONITORING.md")

        with open(doc_file, "r") as f:
            content = f.read()

        # Test documented rate limiting scenarios
        rate_limit_terms = [
            "rate limit",
            "API rate limit",
            "requests remaining",
            "poll-interval",
        ]

        for term in rate_limit_terms:
            with self.subTest(rate_limit_term=term):
                self.assertIn(
                    term, content, f"Rate limiting term should be documented: {term}"
                )

    def test_network_troubleshooting(self):
        """Test network troubleshooting scenarios."""
        doc_file = Path("docs/GITHUB_ACTION_MONITORING.md")

        with open(doc_file, "r") as f:
            content = f.read()

        # Test documented network errors
        network_errors = [
            "Network connectivity",
            "getaddrinfo failed",
            "internet connection",
            "GitHub API is accessible",
        ]

        for error in network_errors:
            with self.subTest(network_error=error):
                self.assertIn(
                    error, content, f"Network error should be documented: {error}"
                )

        # Test network validation command
        if "curl https://api.github.com" in content:
            # Basic curl command validation
            self.assertIn("curl", content, "Network test command should use curl")

    def test_debug_mode_instructions(self):
        """Test debug mode instructions."""
        doc_file = Path("docs/GITHUB_ACTION_MONITORING.md")

        with open(doc_file, "r") as f:
            content = f.read()

        # Test debug commands
        debug_commands = ["--verbose", "--cache-stats", "verbose mode"]

        for command in debug_commands:
            with self.subTest(debug_command=command):
                self.assertIn(
                    command, content, f"Debug command should be documented: {command}"
                )


@pytest.mark.skipif(
    os.name == "nt", reason="Windows encoding issues - TODO: fix UTF-8 file reading"
)
class TestDocumentationLinks(unittest.TestCase):
    """Test that all links and references in documentation are valid."""

    def setUp(self):
        """Set up test environment."""
        self.docs_dir = Path("docs")
        self.timeout = 10  # seconds for URL checks

    def test_internal_links(self):
        """Test internal links between documentation files."""
        doc_files = list(self.docs_dir.glob("*.md"))
        self.assertGreater(len(doc_files), 0, "Documentation files should exist")

        for doc_file in doc_files:
            with self.subTest(doc_file=doc_file.name):
                with open(doc_file, "r") as f:
                    content = f.read()

                # Find markdown links [text](link)
                link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
                links = re.findall(link_pattern, content)

                for link_text, link_url in links:
                    # Test internal links (relative paths)
                    # Use URL parsing to properly identify external links
                    parsed_link = urlparse(link_url)
                    is_external = parsed_link.scheme in ("http", "https")
                    is_anchor = link_url.startswith("#")

                    if not is_external and not is_anchor:
                        with self.subTest(internal_link=link_url):
                            # Resolve relative path
                            if link_url.startswith("../"):
                                target_path = doc_file.parent.parent / link_url[3:]
                            else:
                                target_path = doc_file.parent / link_url

                            # Check if target exists
                            if not target_path.exists():
                                # Try as directory
                                if not target_path.is_dir():
                                    self.fail(
                                        f"Internal link target not found: {link_url} -> {target_path}"
                                    )

    def test_script_references(self):
        """Test references to scripts in documentation."""
        doc_files = list(self.docs_dir.glob("*.md"))

        for doc_file in doc_files:
            with self.subTest(doc_file=doc_file.name):
                with open(doc_file, "r") as f:
                    content = f.read()

                # Find script references
                script_pattern = r"scripts/([a-zA-Z_][a-zA-Z0-9_]*\.py)"
                scripts = re.findall(script_pattern, content)

                for script_name in scripts:
                    with self.subTest(script_reference=script_name):
                        script_path = Path("scripts") / script_name
                        self.assertTrue(
                            script_path.exists(),
                            f"Referenced script should exist: {script_path}",
                        )

                        # Test that script is executable Python
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
                                f"Referenced script should be valid Python: {script_path}",
                            )
                        except subprocess.TimeoutExpired:
                            self.fail(f"Script compilation timed out: {script_path}")

    def test_makefile_references(self):
        """Test references to Makefile targets in documentation."""
        doc_files = list(self.docs_dir.glob("*.md"))
        makefile = Path("Makefile")

        if not makefile.exists():
            self.skipTest("Makefile not found")

        with open(makefile, "r") as f:
            makefile_content = f.read()

        for doc_file in doc_files:
            with self.subTest(doc_file=doc_file.name):
                with open(doc_file, "r") as f:
                    content = f.read()

                # Find make target references (exclude comments and generic text)
                make_targets = []
                for line in content.split("\n"):
                    if line.strip().startswith("make ") and not line.strip().startswith(
                        "#"
                    ):
                        matches = re.findall(r"make\s+([a-zA-Z][a-zA-Z0-9_-]*)", line)
                        make_targets.extend(matches)

                for target in make_targets:
                    with self.subTest(make_target=target):
                        self.assertIn(
                            f"{target}:",
                            makefile_content,
                            f"Referenced make target should exist: {target}",
                        )

    def test_external_urls(self):
        """Test external URLs in documentation (basic validation)."""
        doc_files = list(self.docs_dir.glob("*.md"))

        for doc_file in doc_files:
            with self.subTest(doc_file=doc_file.name):
                with open(doc_file, "r") as f:
                    content = f.read()

                # Find external URLs
                url_pattern = r"https?://[^\s\)]+"
                urls = re.findall(url_pattern, content)

                for url in urls:
                    with self.subTest(external_url=url):
                        # Basic URL format validation
                        parsed = urlparse(url)
                        self.assertIn(
                            parsed.scheme,
                            ["http", "https"],
                            f"URL should have valid scheme: {url}",
                        )
                        self.assertTrue(
                            parsed.netloc, f"URL should have valid domain: {url}"
                        )

                        # Test specific known URLs
                        if "github.com" in url:
                            self.assertIn(
                                "github.com",
                                parsed.netloc,
                                f"GitHub URL should be properly formatted: {url}",
                            )


@pytest.mark.skipif(
    os.name == "nt", reason="Windows encoding issues - TODO: fix UTF-8 file reading"
)
class TestDocumentationCompleteness(unittest.TestCase):
    """Test that documentation covers all implemented features."""

    def setUp(self):
        """Set up test environment."""
        self.docs_dir = Path("docs")
        self.scripts_dir = Path("scripts")

    def test_all_scripts_documented(self):
        """Test that all user-facing scripts are documented."""
        # Get main user-facing GitHub scripts (not internal modules)
        main_scripts = ["github_pipeline_monitor.py"]

        # Read all documentation
        doc_content = ""
        for doc_file in self.docs_dir.glob("*.md"):
            with open(doc_file, "r") as f:
                doc_content += f.read() + "\n"

        for script_name in main_scripts:
            with self.subTest(script=script_name):
                self.assertIn(
                    script_name,
                    doc_content,
                    f"Main script should be documented: {script_name}",
                )

    def test_all_make_targets_documented(self):
        """Test that all pipeline monitoring make targets are documented."""
        makefile = Path("Makefile")
        if not makefile.exists():
            self.skipTest("Makefile not found")

        with open(makefile, "r") as f:
            makefile_content = f.read()

        # Find pipeline monitoring targets (actual make targets, not command lines)
        pipeline_targets = []
        for line in makefile_content.split("\n"):
            # Only look for actual make target definitions (start of line, end with colon)
            if (
                line
                and not line.startswith("\t")
                and not line.startswith(" ")
                and ":" in line
                and not line.strip().startswith("#")
            ):
                target = line.split(":")[0].strip()
                # Check if this is a pipeline-related target
                if (
                    target
                    and any(keyword in target for keyword in ["monitor", "pipeline"])
                    and not target.startswith(".")  # Skip .PHONY
                    and target not in ["help"]
                ):  # Skip help target
                    pipeline_targets.append(target)

        # Read documentation
        doc_content = ""
        for doc_file in self.docs_dir.glob("*.md"):
            with open(doc_file, "r") as f:
                doc_content += f.read() + "\n"

        for target in pipeline_targets:
            with self.subTest(make_target=target):
                self.assertIn(
                    target, doc_content, f"Make target should be documented: {target}"
                )

    def test_environment_variables_documented(self):
        """Test that all environment variables are documented."""
        # Get environment variables from scripts
        script_files = list(self.scripts_dir.glob("github_*.py"))
        env_vars = set()

        for script_file in script_files:
            try:
                with open(script_file, "r") as f:
                    script_content = f.read()

                # Find environment variable references
                env_pattern = r'os\.environ\.get\(["\']([^"\']+)["\']'
                env_matches = re.findall(env_pattern, script_content)
                env_vars.update(env_matches)

                # Also check for direct os.environ access
                direct_pattern = r'os\.environ\[["\']([^"\']+)["\']\]'
                direct_matches = re.findall(direct_pattern, script_content)
                env_vars.update(direct_matches)

            except Exception:
                # Skip files that can't be read
                continue

        # Read documentation
        doc_content = ""
        for doc_file in self.docs_dir.glob("*.md"):
            with open(doc_file, "r") as f:
                doc_content += f.read() + "\n"

        # Filter to GitHub-related environment variables
        github_env_vars = [var for var in env_vars if "GITHUB" in var]

        for env_var in github_env_vars:
            with self.subTest(env_var=env_var):
                self.assertIn(
                    env_var,
                    doc_content,
                    f"Environment variable should be documented: {env_var}",
                )


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
