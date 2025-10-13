"""
Performance benchmark tests for mypylogger.

These tests validate that the library meets performance requirements:
- Latency: <1ms per log entry (95th percentile)
- Throughput: >10,000 logs/second
- Memory: <50MB baseline memory usage
"""

import os
import time
from statistics import median
from typing import List, Tuple

import psutil
import pytest

from mypylogger import get_logger


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark test suite."""

    def setup_method(self):
        """Set up clean logger for each test."""
        # Reset singleton for clean testing
        from mypylogger.core import SingletonLogger

        SingletonLogger._instance = None
        SingletonLogger._logger = None

    @pytest.mark.performance
    def test_logging_latency_requirement(self, temp_log_dir):
        """Test that individual log entries meet latency requirement (<1ms)."""
        # Set up logger with temp directory
        os.environ["APP_NAME"] = "performance_test"
        logger = get_logger()

        # Warm up the logger (first few calls may be slower due to initialization)
        for _ in range(10):
            logger.info("Warmup message")

        # Measure latency for multiple log entries
        latencies = []
        num_samples = 100

        for i in range(num_samples):
            start_time = time.perf_counter()
            logger.info(f"Performance test message {i}")
            end_time = time.perf_counter()

            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

        # Calculate statistics
        avg_latency = sum(latencies) / len(latencies)
        median_latency = median(latencies)
        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
        max_latency = max(latencies)

        # Print performance metrics for visibility
        print("\nLatency Performance Metrics:")
        print(f"  Average: {avg_latency:.3f}ms")
        print(f"  Median:  {median_latency:.3f}ms")
        print(f"  95th %:  {p95_latency:.3f}ms")
        print(f"  Maximum: {max_latency:.3f}ms")

        # Requirement: 95th percentile < 1ms
        assert (
            p95_latency < 1.0
        ), f"95th percentile latency {p95_latency:.3f}ms exceeds 1ms requirement"

        # Additional checks for good performance
        assert (
            avg_latency < 0.5
        ), f"Average latency {avg_latency:.3f}ms should be well under 1ms"

    @pytest.mark.performance
    def test_logging_throughput_requirement(self, temp_log_dir):
        """Test that logger can handle >10,000 logs/second throughput."""
        # Set up logger with temp directory
        os.environ["APP_NAME"] = "throughput_test"
        logger = get_logger()

        # Warm up
        for _ in range(100):
            logger.info("Warmup message")

        # Measure throughput
        num_messages = 15000  # Test with more than requirement
        start_time = time.perf_counter()

        for i in range(num_messages):
            logger.info(f"Throughput test message {i}")

        end_time = time.perf_counter()
        duration = end_time - start_time
        throughput = num_messages / duration

        print("\nThroughput Performance Metrics:")
        print(f"  Messages: {num_messages}")
        print(f"  Duration: {duration:.3f}s")
        print(f"  Throughput: {throughput:.0f} logs/second")

        # Requirement: >10,000 logs/second (local), >8,000 logs/second (CI), >6,000 logs/second (Windows CI)
        # CI environments have constrained resources, Windows CI is even slower
        is_ci = os.getenv("CI", "false").lower() == "true"
        is_windows = os.name == "nt"

        if is_ci and is_windows:
            min_throughput = 6000  # Windows CI is slowest
        elif is_ci:
            min_throughput = 8000  # Linux/macOS CI
        else:
            min_throughput = 10000  # Local development

        assert (
            throughput > min_throughput
        ), f"Throughput {throughput:.0f} logs/sec is below {min_throughput} requirement ({'CI' if is_ci else 'local'} environment)"

    @pytest.mark.performance
    def test_memory_usage_requirement(self, temp_log_dir):
        """Test that logger memory usage stays within acceptable limits (<50MB)."""
        # Set up logger with temp directory
        os.environ["APP_NAME"] = "memory_test"

        # Get baseline memory usage
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create logger and log messages
        logger = get_logger()

        # Log a significant number of messages to test memory usage
        for i in range(5000):
            logger.info(
                f"Memory test message {i} with some additional data to make it realistic"
            )

            # Check memory every 1000 messages
            if i % 1000 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - baseline_memory

                # Ensure we don't exceed 50MB increase from baseline
                assert (
                    memory_increase < 50
                ), f"Memory usage increased by {memory_increase:.1f}MB, exceeding 50MB limit"

        # Final memory check
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_increase = final_memory - baseline_memory

        print("\nMemory Usage Metrics:")
        print(f"  Baseline: {baseline_memory:.1f}MB")
        print(f"  Final:    {final_memory:.1f}MB")
        print(f"  Increase: {total_increase:.1f}MB")

        # Requirement: <50MB baseline increase
        assert (
            total_increase < 50
        ), f"Memory usage increased by {total_increase:.1f}MB, exceeding 50MB limit"

    @pytest.mark.performance
    def test_concurrent_logging_performance(self, temp_log_dir):
        """Test performance under concurrent logging scenarios."""
        import queue
        import threading

        os.environ["APP_NAME"] = "concurrent_test"
        logger = get_logger()

        # Test concurrent logging from multiple threads
        num_threads = 4
        messages_per_thread = 1000
        results_queue: queue.Queue[Tuple[int, float, float]] = queue.Queue()

        def log_worker(thread_id, num_messages):
            """Worker function for concurrent logging."""
            start_time = time.perf_counter()

            for i in range(num_messages):
                logger.info(f"Thread {thread_id} message {i}")

            end_time = time.perf_counter()
            duration = end_time - start_time
            throughput = num_messages / duration
            results_queue.put((thread_id, throughput, duration))

        # Start all threads
        threads = []
        overall_start = time.perf_counter()

        for thread_id in range(num_threads):
            thread = threading.Thread(
                target=log_worker, args=(thread_id, messages_per_thread)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        overall_end = time.perf_counter()
        overall_duration = overall_end - overall_start
        total_messages = num_threads * messages_per_thread
        overall_throughput = total_messages / overall_duration

        # Collect results
        thread_results: List[Tuple[int, float, float]] = []
        while not results_queue.empty():
            thread_results.append(results_queue.get())

        print("\nConcurrent Logging Performance:")
        print(f"  Threads: {num_threads}")
        print(f"  Messages per thread: {messages_per_thread}")
        print(f"  Total messages: {total_messages}")
        print(f"  Overall duration: {overall_duration:.3f}s")
        print(f"  Overall throughput: {overall_throughput:.0f} logs/second")

        for thread_id, throughput, duration in thread_results:
            print(f"  Thread {thread_id}: {throughput:.0f} logs/sec ({duration:.3f}s)")

        # Requirement: Should maintain good performance under concurrency
        assert (
            overall_throughput > 5000
        ), f"Concurrent throughput {overall_throughput:.0f} is too low"

        # Ensure no thread performed extremely poorly
        min_thread_throughput = min(result[1] for result in thread_results)
        assert (
            min_thread_throughput > 1000
        ), f"Slowest thread only achieved {min_thread_throughput:.0f} logs/sec"

    @pytest.mark.performance
    def test_performance_regression_detection(self, temp_log_dir):
        """Test to detect performance regressions over time."""
        os.environ["APP_NAME"] = "regression_test"
        logger = get_logger()

        # This test establishes baseline performance metrics
        # In a real CI/CD environment, these would be compared against historical data

        # Measure key performance indicators
        num_warmup = 100
        num_test_messages = 1000

        # Warmup
        for _ in range(num_warmup):
            logger.info("Warmup message")

        # Measure latency
        start_time = time.perf_counter()
        for i in range(num_test_messages):
            logger.info(f"Regression test message {i}")
        end_time = time.perf_counter()

        duration = end_time - start_time
        avg_latency_ms = (duration / num_test_messages) * 1000
        throughput = num_test_messages / duration

        # Store metrics (in real implementation, this would go to a metrics store)
        performance_metrics = {
            "avg_latency_ms": avg_latency_ms,
            "throughput_logs_per_sec": throughput,
            "test_messages": num_test_messages,
            "duration_seconds": duration,
        }

        print("\nPerformance Regression Baseline:")
        for key, value in performance_metrics.items():
            if "latency" in key:
                print(f"  {key}: {value:.3f}")
            elif "throughput" in key:
                print(f"  {key}: {value:.0f}")
            else:
                print(f"  {key}: {value}")

        # Basic sanity checks (these would be more sophisticated in practice)
        assert (
            avg_latency_ms < 0.5
        ), f"Average latency {avg_latency_ms:.3f}ms is concerning"
        assert (
            throughput > 5000
        ), f"Throughput {throughput:.0f} logs/sec is below expected baseline"

        # In a real implementation, you would:
        # 1. Store these metrics in a time-series database
        # 2. Compare against historical trends
        # 3. Alert if performance degrades beyond acceptable thresholds
        # 4. Generate performance trend reports
