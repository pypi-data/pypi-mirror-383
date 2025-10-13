"""
Test suite for badge infrastructure setup and Shields.io migration.

This test suite verifies:
- Badge URLs are properly formatted for Shields.io
- Badge configuration documentation is complete
- Badge validation script works correctly
- Badge performance meets requirements
- Fallback behavior is properly implemented
"""

import os
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse


class TestBadgeInfrastructure(unittest.TestCase):
    """Test badge infrastructure setup and Shields.io migration."""

    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        self.readme_path = self.project_root / "README.md"
        self.badge_config_path = self.project_root / "docs" / "BADGE_CONFIGURATION.md"
        self.validate_script_path = self.project_root / "scripts" / "validate_badges.py"
        self.performance_script_path = (
            self.project_root / "scripts" / "test_badge_performance.py"
        )

    def test_readme_exists(self):
        """Test that README.md exists."""
        self.assertTrue(self.readme_path.exists(), "README.md file not found")

    def test_badge_configuration_documentation_exists(self):
        """Test that badge configuration documentation exists."""
        self.assertTrue(
            self.badge_config_path.exists(),
            "Badge configuration documentation not found",
        )

    def test_badge_validation_script_exists(self):
        """Test that badge validation script exists and is executable."""
        self.assertTrue(
            self.validate_script_path.exists(), "Badge validation script not found"
        )
        self.assertTrue(
            os.access(self.validate_script_path, os.X_OK),
            "Badge validation script is not executable",
        )

    def test_badge_performance_script_exists(self):
        """Test that badge performance test script exists and is executable."""
        self.assertTrue(
            self.performance_script_path.exists(),
            "Badge performance test script not found",
        )
        self.assertTrue(
            os.access(self.performance_script_path, os.X_OK),
            "Badge performance test script is not executable",
        )

    def test_shields_io_badge_format(self):
        """Test that all badges use Shields.io format."""
        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract all badge URLs
        badge_pattern = r"\[\!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)"
        matches = re.findall(badge_pattern, content)

        self.assertGreater(len(matches), 0, "No badges found in README.md")

        shields_io_badges = 0
        for alt_text, badge_url, link_url in matches:
            if "img.shields.io" in badge_url:
                shields_io_badges += 1

        # All badges should use Shields.io
        self.assertEqual(
            shields_io_badges,
            len(matches),
            f"Not all badges use Shields.io format. "
            f"Found {shields_io_badges} Shields.io badges out of {len(matches)} total",
        )

    def test_badge_tier_organization(self):
        """Test that badges are organized into proper tiers."""
        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for tier comments
        tier1_comment = "<!-- Core Status (Tier 1) -->"
        tier2_comment = "<!-- Quality & Compatibility (Tier 2) -->"
        tier3_comment = "<!-- Performance & Community (Tier 3) -->"

        self.assertIn(tier1_comment, content, "Tier 1 comment not found")
        self.assertIn(tier2_comment, content, "Tier 2 comment not found")
        self.assertIn(tier3_comment, content, "Tier 3 comment not found")

        # Verify tier order
        tier1_pos = content.find(tier1_comment)
        tier2_pos = content.find(tier2_comment)
        tier3_pos = content.find(tier3_comment)

        self.assertLess(tier1_pos, tier2_pos, "Tier 1 should come before Tier 2")
        self.assertLess(tier2_pos, tier3_pos, "Tier 2 should come before Tier 3")

    def test_required_tier1_badges(self):
        """Test that all required Tier 1 badges are present."""
        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Required Tier 1 badges
        required_badges = ["Build Status", "Coverage", "Security", "License"]

        for badge_name in required_badges:
            # Look for badge alt text
            self.assertRegex(
                content,
                rf"\[\!\[.*{badge_name}.*\]",
                f"Required Tier 1 badge '{badge_name}' not found",
            )

    def test_required_tier2_badges(self):
        """Test that all required Tier 2 badges are present."""
        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Required Tier 2 badges
        required_badges = ["PyPI Version", "Python Versions", "Maintenance"]

        for badge_name in required_badges:
            # Look for badge alt text or URL patterns
            badge_found = (
                re.search(rf"\[\!\[.*{badge_name}.*\]", content)
                or re.search(r"pypi/v/mypylogger", content)
                or re.search(r"pypi/pyversions/mypylogger", content)
                or re.search(r"maintenance/yes", content)
            )
            self.assertTrue(
                badge_found, f"Required Tier 2 badge '{badge_name}' not found"
            )

    def test_performance_badges_present(self):
        """Test that OS-specific performance badges are present with valid format."""
        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Performance badges should include Ubuntu and macOS
        self.assertIn("Ubuntu", content, "Ubuntu performance badge not found")
        self.assertIn("macOS", content, "macOS performance badge not found")

        # Verify latency format: should match pattern like "0.034ms" or "0.017ms"
        # Pattern: one or more digits, decimal point, 2-3 digits, "ms"
        latency_pattern = r"\d+\.\d{2,3}ms"
        latency_matches = re.findall(latency_pattern, content)
        self.assertGreaterEqual(
            len(latency_matches),
            2,
            f"Expected at least 2 latency metrics in valid format (X.XXXms), found {len(latency_matches)}",
        )

        # Verify throughput format: should match pattern like "32K/sec" or "60K/sec"
        # Pattern: digits followed by "K/sec"
        throughput_pattern = r"\d+K/sec"
        throughput_matches = re.findall(throughput_pattern, content)
        self.assertGreaterEqual(
            len(throughput_matches),
            2,
            f"Expected at least 2 throughput metrics in valid format (XXK/sec), found {len(throughput_matches)}",
        )

    def test_badge_accessibility_features(self):
        """Test that badges have proper accessibility features."""
        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract all badges
        badge_pattern = r"\[\!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)"
        matches = re.findall(badge_pattern, content)

        for alt_text, badge_url, link_url in matches:
            # Alt text should not be empty
            self.assertNotEqual(
                alt_text.strip(), "", f"Badge has empty alt text: {badge_url}"
            )

            # Alt text should be meaningful (not just generic terms)
            generic_terms = ["image", "badge", "icon", "logo"]
            self.assertNotIn(
                alt_text.lower().strip(),
                generic_terms,
                f"Badge has generic alt text: '{alt_text}'",
            )

            # Alt text should be reasonably descriptive
            self.assertGreaterEqual(
                len(alt_text.strip()), 3, f"Badge alt text too short: '{alt_text}'"
            )

    def test_badge_configuration_documentation_completeness(self):
        """Test that badge configuration documentation is complete."""
        with open(self.badge_config_path, "r", encoding="utf-8") as f:
            config_content = f.read()

        # Check for required sections
        required_sections = [
            "Badge Organization",
            "Tier 1: Core Status",
            "Tier 2: Quality & Compatibility",
            "Tier 3: Performance & Community",
            "Badge URL Templates",
            "Accessibility Features",
            "Badge Validation",
            "Maintenance Procedures",
        ]

        for section in required_sections:
            self.assertIn(
                section,
                config_content,
                f"Required documentation section '{section}' not found",
            )

        # Check for URL templates
        self.assertIn(
            "https://img.shields.io/",
            config_content,
            "Shields.io URL templates not documented",
        )

        # Check for parameter documentation
        self.assertIn(
            "{owner}", config_content, "URL template parameters not documented"
        )
        self.assertIn("{repo}", config_content, "Repository parameter not documented")

    def test_makefile_badge_commands(self):
        """Test that Makefile includes badge validation commands."""
        makefile_path = self.project_root / "Makefile"

        with open(makefile_path, "r", encoding="utf-8") as f:
            makefile_content = f.read()

        # Check for badge-related commands
        required_commands = [
            "verify-badges:",
            "validate-badges-verbose:",
            "test-badge-performance:",
        ]

        for command in required_commands:
            self.assertIn(
                command, makefile_content, f"Makefile command '{command}' not found"
            )

    def test_badge_validation_script_functionality(self):
        """Test that badge validation script has proper functionality."""
        # Read the validation script
        with open(self.validate_script_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        # Check for required functions/classes
        required_components = [
            "class Badge",
            "class BadgeValidator",
            "def extract_badges_from_readme",
            "def validate_badge_url",
            "def validate_alt_text",
            "def validate_all_badges",
        ]

        for component in required_components:
            self.assertIn(
                component,
                script_content,
                f"Badge validation script missing: {component}",
            )

        # Check for proper imports
        self.assertIn(
            "import requests",
            script_content,
            "Badge validation script missing requests import",
        )
        self.assertIn(
            "import argparse",
            script_content,
            "Badge validation script missing argparse import",
        )

    def test_badge_performance_script_functionality(self):
        """Test that badge performance script has proper functionality."""
        # Read the performance script
        with open(self.performance_script_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        # Check for required functions/classes
        required_components = [
            "class PerformanceResult",
            "class BadgePerformanceTester",
            "def test_single_badge_performance",
            "def test_concurrent_badge_loading",
            "def test_fallback_behavior",
            "def run_performance_test",
        ]

        for component in required_components:
            self.assertIn(
                component,
                script_content,
                f"Badge performance script missing: {component}",
            )

    def test_badge_url_patterns(self):
        """Test that badge URLs follow expected patterns."""
        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract badge URLs
        badge_pattern = r"\[\!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)"
        matches = re.findall(badge_pattern, content)

        for alt_text, badge_url, link_url in matches:
            # All badge URLs should use HTTPS with proper domain validation
            parsed_badge = urlparse(badge_url)
            self.assertEqual(
                parsed_badge.scheme,
                "https",
                f"Badge URL not using HTTPS: {badge_url}",
            )
            self.assertTrue(
                parsed_badge.netloc,
                f"Badge URL must have valid domain: {badge_url}",
            )

            # Link URLs should also use HTTPS with proper domain validation
            parsed_link = urlparse(link_url)
            self.assertEqual(
                parsed_link.scheme,
                "https",
                f"Badge link URL not using HTTPS: {link_url}",
            )
            self.assertTrue(
                parsed_link.netloc,
                f"Badge link URL must have valid domain: {link_url}",
            )

            # Shields.io badges should have proper format
            if "img.shields.io" in badge_url:
                # Should contain repository reference for GitHub-based badges
                # (excluding maintenance and static badges)
                if (
                    "github" in badge_url
                    and "maintenance" not in badge_url
                    and "badge/" not in badge_url
                ):
                    self.assertIn(
                        "stabbotco1/mypylogger",
                        badge_url,
                        f"GitHub badge missing repository reference: {badge_url}",
                    )

    def test_badge_count_within_limits(self):
        """Test that badge count is within recommended limits."""
        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract all badges
        badge_pattern = r"\[\!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)"
        matches = re.findall(badge_pattern, content)

        badge_count = len(matches)

        # Should have between 8-11 badges as per design specification
        self.assertGreaterEqual(
            badge_count, 8, f"Too few badges ({badge_count}). Minimum recommended: 8"
        )
        self.assertLessEqual(
            badge_count, 11, f"Too many badges ({badge_count}). Maximum recommended: 11"
        )


if __name__ == "__main__":
    unittest.main()
