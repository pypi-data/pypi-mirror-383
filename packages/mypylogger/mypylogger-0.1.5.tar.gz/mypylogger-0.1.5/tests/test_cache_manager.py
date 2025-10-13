#!/usr/bin/env python3
"""
Tests for GitHub Cache Manager

This module tests the response caching and rate limiting functionality
for GitHub API requests.
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from unittest.mock import patch

import pytest

# Import the modules to test
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
from github_cache_manager import (  # noqa: E402
    CacheConfig,
    CacheEntry,
    CacheEntryType,
    GitHubCacheManager,
    RateLimitInfo,
    create_cache_manager,
)


class TestRateLimitInfo:
    """Test RateLimitInfo functionality."""

    def test_rate_limit_info_initialization(self):
        """Test RateLimitInfo initialization."""
        rate_limit = RateLimitInfo(
            limit=5000,
            remaining=4500,
            reset_time=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            used=500,
        )

        assert rate_limit.limit == 5000
        assert rate_limit.remaining == 4500
        assert rate_limit.used == 500
        assert rate_limit.reset_time.hour == 12

    def test_rate_limit_from_headers(self):
        """Test creating RateLimitInfo from HTTP headers."""
        headers = {
            "X-RateLimit-Limit": "5000",
            "X-RateLimit-Remaining": "4500",
            "X-RateLimit-Reset": "1672574400",  # 2023-01-01 12:00:00 UTC
        }

        rate_limit = RateLimitInfo.from_headers(headers)

        assert rate_limit.limit == 5000
        assert rate_limit.remaining == 4500
        assert rate_limit.used == 500

    @patch("github_cache_manager.datetime")
    def test_time_until_reset(self, mock_datetime):
        """Test time until reset calculation."""
        mock_now = datetime(2023, 1, 1, 11, 30, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        rate_limit = RateLimitInfo(
            limit=5000,
            remaining=4500,
            reset_time=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        time_until_reset = rate_limit.time_until_reset()
        assert time_until_reset == timedelta(minutes=30)

    def test_is_exhausted(self):
        """Test rate limit exhaustion detection."""
        rate_limit = RateLimitInfo(
            limit=5000, remaining=5, reset_time=datetime.now(timezone.utc)
        )

        assert rate_limit.is_exhausted() is True
        assert rate_limit.is_exhausted(threshold=3) is False

        rate_limit.remaining = 15
        assert rate_limit.is_exhausted() is False

    @patch("github_cache_manager.datetime")
    def test_requests_per_minute_available(self, mock_datetime):
        """Test requests per minute calculation."""
        mock_now = datetime(2023, 1, 1, 11, 30, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        rate_limit = RateLimitInfo(
            limit=5000,
            remaining=1000,
            reset_time=datetime(
                2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc
            ),  # 30 minutes from now
        )

        requests_per_minute = rate_limit.requests_per_minute_available()
        expected = 1000 / 30  # 1000 requests over 30 minutes
        assert abs(requests_per_minute - expected) < 0.1


class TestCacheEntry:
    """Test CacheEntry functionality."""

    def test_cache_entry_initialization(self):
        """Test CacheEntry initialization."""
        created_at = datetime.now(timezone.utc)
        expires_at = created_at + timedelta(minutes=30)

        entry = CacheEntry(
            key="test-key",
            data={"test": "data"},
            entry_type=CacheEntryType.WORKFLOW_RUNS,
            created_at=created_at,
            expires_at=expires_at,
        )

        assert entry.key == "test-key"
        assert entry.data == {"test": "data"}
        assert entry.entry_type == CacheEntryType.WORKFLOW_RUNS
        assert entry.hit_count == 0

    @patch("github_cache_manager.datetime")
    def test_is_expired(self, mock_datetime):
        """Test cache entry expiration detection."""
        created_at = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        expires_at = datetime(2023, 1, 1, 10, 30, 0, tzinfo=timezone.utc)

        entry = CacheEntry(
            key="test-key",
            data={},
            entry_type=CacheEntryType.WORKFLOW_RUNS,
            created_at=created_at,
            expires_at=expires_at,
        )

        # Before expiration
        mock_datetime.now.return_value = datetime(
            2023, 1, 1, 10, 15, 0, tzinfo=timezone.utc
        )
        assert entry.is_expired() is False

        # After expiration
        mock_datetime.now.return_value = datetime(
            2023, 1, 1, 10, 35, 0, tzinfo=timezone.utc
        )
        assert entry.is_expired() is True

    @patch("github_cache_manager.datetime")
    def test_is_stale(self, mock_datetime):
        """Test cache entry staleness detection."""
        created_at = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        expires_at = datetime(2023, 1, 1, 10, 30, 0, tzinfo=timezone.utc)

        entry = CacheEntry(
            key="test-key",
            data={},
            entry_type=CacheEntryType.WORKFLOW_RUNS,
            created_at=created_at,
            expires_at=expires_at,
        )

        # Fresh entry
        mock_datetime.now.return_value = datetime(
            2023, 1, 1, 10, 15, 0, tzinfo=timezone.utc
        )
        assert entry.is_stale() is False

        # Stale but not expired (within 5 minutes of expiration)
        mock_datetime.now.return_value = datetime(
            2023, 1, 1, 10, 27, 0, tzinfo=timezone.utc
        )
        assert entry.is_stale() is True
        assert entry.is_expired() is False

    def test_record_hit(self):
        """Test recording cache hits."""
        entry = CacheEntry(
            key="test-key",
            data={},
            entry_type=CacheEntryType.WORKFLOW_RUNS,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )

        assert entry.hit_count == 0

        entry.record_hit()
        assert entry.hit_count == 1

        entry.record_hit()
        assert entry.hit_count == 2


class TestCacheConfig:
    """Test CacheConfig functionality."""

    def test_cache_config_defaults(self):
        """Test CacheConfig default values."""
        config = CacheConfig()

        assert config.workflow_runs_ttl == 30
        assert config.repository_info_ttl == 3600
        assert config.rate_limit_info_ttl == 60
        assert config.user_info_ttl == 1800
        assert config.max_entries == 1000
        assert config.max_memory_mb == 50
        assert config.allow_stale_responses is True
        assert config.stale_threshold_minutes == 5
        assert config.rate_limit_threshold == 10
        assert config.rate_limit_backoff_seconds == 60

    def test_get_ttl_for_type(self):
        """Test getting TTL for different cache entry types."""
        config = CacheConfig()

        assert config.get_ttl_for_type(CacheEntryType.WORKFLOW_RUNS) == 30
        assert config.get_ttl_for_type(CacheEntryType.REPOSITORY_INFO) == 3600
        assert config.get_ttl_for_type(CacheEntryType.RATE_LIMIT_INFO) == 60
        assert config.get_ttl_for_type(CacheEntryType.USER_INFO) == 1800

    def test_custom_cache_config(self):
        """Test custom CacheConfig values."""
        config = CacheConfig(
            workflow_runs_ttl=60, max_entries=500, allow_stale_responses=False
        )

        assert config.workflow_runs_ttl == 60
        assert config.max_entries == 500
        assert config.allow_stale_responses is False
        # Other values should remain default
        assert config.repository_info_ttl == 3600


class TestGitHubCacheManager:
    """Test GitHubCacheManager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = CacheConfig(max_entries=10)  # Small cache for testing
        self.manager = GitHubCacheManager(self.config)

    def test_manager_initialization(self):
        """Test GitHubCacheManager initialization."""
        manager = GitHubCacheManager()

        assert isinstance(manager.config, CacheConfig)
        assert len(manager.cache) == 0
        assert manager.rate_limit_info is None
        assert len(manager.request_queue) == 0

    def test_generate_cache_key_simple(self):
        """Test cache key generation for simple endpoints."""
        key = self.manager._generate_cache_key("/repos/owner/repo")
        assert key == "repos/owner/repo"

    def test_generate_cache_key_with_params(self):
        """Test cache key generation with parameters."""
        params = {"head_sha": "abc123", "per_page": 100}
        key = self.manager._generate_cache_key("/repos/owner/repo/actions/runs", params)

        # Parameters should be sorted for consistent keys
        assert "head_sha=abc123" in key
        assert "per_page=100" in key
        assert key.startswith("repos/owner/repo/actions/runs")

    def test_generate_cache_key_long_key_hashing(self):
        """Test that long cache keys are hashed."""
        long_endpoint = "/very/long/endpoint/" + "x" * 200
        key = self.manager._generate_cache_key(long_endpoint)

        # Should be a hash (64 characters for SHA256)
        assert len(key) == 64
        assert all(c in "0123456789abcdef" for c in key)

    def test_determine_entry_type(self):
        """Test determining cache entry type from endpoint."""
        assert (
            self.manager._determine_entry_type("/repos/owner/repo/actions/runs")
            == CacheEntryType.WORKFLOW_RUNS
        )
        assert (
            self.manager._determine_entry_type("/repos/owner/repo")
            == CacheEntryType.REPOSITORY_INFO
        )
        assert (
            self.manager._determine_entry_type("/rate_limit")
            == CacheEntryType.RATE_LIMIT_INFO
        )
        assert self.manager._determine_entry_type("/user") == CacheEntryType.USER_INFO
        assert (
            self.manager._determine_entry_type("/unknown/endpoint")
            == CacheEntryType.WORKFLOW_RUNS
        )

    def test_cache_and_retrieve_response(self):
        """Test caching and retrieving responses."""
        endpoint = "/repos/owner/repo/actions/runs"
        params = {"head_sha": "abc123"}
        response_data: Dict[str, Any] = {"workflow_runs": []}

        # Initially no cached response
        cached = self.manager.get_cached_response(endpoint, params)
        assert cached is None

        # Cache the response
        self.manager.cache_response(endpoint, params, response_data)

        # Should now return cached response
        cached = self.manager.get_cached_response(endpoint, params)
        assert cached == response_data

    @patch("github_cache_manager.datetime")
    def test_cache_expiration(self, mock_datetime):
        """Test cache entry expiration."""
        base_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = base_time

        endpoint = "/repos/owner/repo/actions/runs"
        response_data: Dict[str, Any] = {"workflow_runs": []}

        # Cache the response
        self.manager.cache_response(endpoint, None, response_data)

        # Should be available immediately
        cached = self.manager.get_cached_response(endpoint)
        assert cached == response_data

        # Move time forward past TTL
        mock_datetime.now.return_value = base_time + timedelta(
            seconds=35
        )  # TTL is 30 seconds

        # Should be expired and return None
        cached = self.manager.get_cached_response(endpoint)
        assert cached is None

    @patch("github_cache_manager.datetime")
    def test_stale_response_handling(self, mock_datetime):
        """Test handling of stale responses."""
        base_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = base_time

        endpoint = "/repos/owner/repo/actions/runs"
        response_data: Dict[str, Any] = {"workflow_runs": []}

        # Cache the response
        self.manager.cache_response(endpoint, None, response_data)

        # Move time forward to make entry stale but not expired
        mock_datetime.now.return_value = base_time + timedelta(
            seconds=27
        )  # Stale but not expired

        # Should return stale response when allowed
        cached = self.manager.get_cached_response(endpoint, allow_stale=True)
        assert cached == response_data

        # Should not return stale response when not allowed
        cached = self.manager.get_cached_response(endpoint, allow_stale=False)
        assert cached is None

    def test_update_rate_limit_info(self):
        """Test updating rate limit information."""
        headers = {
            "X-RateLimit-Limit": "5000",
            "X-RateLimit-Remaining": "4500",
            "X-RateLimit-Reset": "1672574400",
        }

        self.manager.update_rate_limit_info(headers)

        assert self.manager.rate_limit_info is not None
        assert self.manager.rate_limit_info.limit == 5000
        assert self.manager.rate_limit_info.remaining == 4500
        assert self.manager.rate_limit_info.used == 500

    def test_should_throttle_request(self):
        """Test request throttling decisions."""
        # No rate limit info - should not throttle
        assert self.manager.should_throttle_request() is False

        # Set rate limit info with plenty of requests remaining
        self.manager.rate_limit_info = RateLimitInfo(
            limit=5000,
            remaining=100,
            reset_time=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        assert self.manager.should_throttle_request() is False

        # Set rate limit info with few requests remaining
        self.manager.rate_limit_info.remaining = 5
        assert self.manager.should_throttle_request() is True

    @patch("github_cache_manager.datetime")
    def test_get_throttle_delay(self, mock_datetime):
        """Test throttle delay calculation."""
        mock_now = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        # No rate limit info - no delay
        assert self.manager.get_throttle_delay() == 0.0

        # Rate limit exhausted - should wait until reset
        self.manager.rate_limit_info = RateLimitInfo(
            limit=5000,
            remaining=0,
            reset_time=datetime(
                2023, 1, 1, 10, 5, 0, tzinfo=timezone.utc
            ),  # 5 minutes from now
        )

        delay = self.manager.get_throttle_delay()
        assert delay == 60.0  # Should be capped at backoff_seconds

        # Some requests remaining - should calculate spread delay
        self.manager.rate_limit_info.remaining = 60
        delay = self.manager.get_throttle_delay()
        assert delay >= 0.0  # Should be some small delay to spread requests

    def test_record_request(self):
        """Test recording API requests."""
        assert len(self.manager.request_queue) == 0

        self.manager.record_request("/repos/owner/repo/actions/runs")

        assert len(self.manager.request_queue) == 1
        assert self.manager.last_request_time is not None

        endpoint, timestamp = self.manager.request_queue[0]
        assert endpoint == "/repos/owner/repo/actions/runs"
        assert isinstance(timestamp, datetime)

    def test_invalidate_cache_by_pattern(self):
        """Test cache invalidation by endpoint pattern."""
        # Cache some responses
        self.manager.cache_response(
            "/repos/owner/repo/actions/runs", {"head_sha": "abc123"}, {}
        )
        self.manager.cache_response(
            "/repos/owner/repo/actions/runs", {"head_sha": "def456"}, {}
        )
        self.manager.cache_response("/repos/owner/repo", None, {})

        assert len(self.manager.cache) == 3

        # Invalidate by pattern
        invalidated = self.manager.invalidate_cache(endpoint_pattern="actions/runs")

        assert invalidated == 2
        assert len(self.manager.cache) == 1  # Only repo info should remain

    def test_invalidate_cache_by_type(self):
        """Test cache invalidation by entry type."""
        # Cache responses of different types
        self.manager.cache_response("/repos/owner/repo/actions/runs", None, {})
        self.manager.cache_response("/repos/owner/repo", None, {})
        self.manager.cache_response("/user", None, {})

        assert len(self.manager.cache) == 3

        # Invalidate workflow runs only
        invalidated = self.manager.invalidate_cache(
            entry_type=CacheEntryType.WORKFLOW_RUNS
        )

        assert invalidated == 1  # Only the actions/runs endpoint should be invalidated
        assert len(self.manager.cache) == 2  # repo and user endpoints should remain

    def test_invalidate_all_cache(self):
        """Test invalidating all cache entries."""
        # Cache some responses
        self.manager.cache_response("/repos/owner/repo/actions/runs", None, {})
        self.manager.cache_response("/repos/owner/repo", None, {})

        assert len(self.manager.cache) == 2

        # Invalidate all
        invalidated = self.manager.invalidate_cache()

        assert invalidated == 2
        assert len(self.manager.cache) == 0

    def test_enforce_cache_limits(self):
        """Test cache size limit enforcement."""
        # Fill cache beyond limit
        for i in range(15):  # More than max_entries (10)
            self.manager.cache_response(f"/endpoint/{i}", None, {"data": i})

        # Should be limited to max_entries
        assert len(self.manager.cache) <= self.config.max_entries

    @patch("github_cache_manager.datetime")
    def test_cleanup_expired_entries(self, mock_datetime):
        """Test cleanup of expired cache entries."""
        base_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = base_time

        # Cache some responses
        self.manager.cache_response("/endpoint/1", None, {"data": 1})
        self.manager.cache_response("/endpoint/2", None, {"data": 2})

        assert len(self.manager.cache) == 2

        # Move time forward to expire entries
        mock_datetime.now.return_value = base_time + timedelta(seconds=35)

        # Cleanup expired entries
        removed = self.manager.cleanup_expired_entries()

        assert removed == 2
        assert len(self.manager.cache) == 0

    def test_get_request_statistics(self):
        """Test getting request statistics."""
        # Add some cache entries and requests
        self.manager.cache_response("/endpoint/1", None, {"data": 1})
        self.manager.record_request("/endpoint/1")

        # Get a cached response to record a hit
        self.manager.get_cached_response("/endpoint/1")

        stats = self.manager.get_request_statistics()

        assert "cache" in stats
        assert "requests" in stats
        assert "rate_limit" in stats

        assert stats["cache"]["total_entries"] == 1
        assert stats["cache"]["total_hits"] == 1
        assert stats["requests"]["total_requests_1hour"] == 1


class TestFactoryFunction:
    """Test factory function."""

    def test_create_cache_manager_default(self):
        """Test creating cache manager with default config."""
        manager = create_cache_manager()

        assert isinstance(manager, GitHubCacheManager)
        assert isinstance(manager.config, CacheConfig)

    def test_create_cache_manager_custom(self):
        """Test creating cache manager with custom config."""
        custom_config = CacheConfig(workflow_runs_ttl=60)
        manager = create_cache_manager(custom_config)

        assert isinstance(manager, GitHubCacheManager)
        assert manager.config.workflow_runs_ttl == 60


if __name__ == "__main__":
    pytest.main([__file__])
