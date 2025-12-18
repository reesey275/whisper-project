"""
Advanced performance tests using pytest-benchmark.

This module provides comprehensive performance testing for:
- Transcription speed across different audio lengths
- Memory usage patterns
- API response time measurements
- Throughput testing with concurrent requests
- Performance regression detection
"""

import os
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from clean_transcribe import CleanTranscriber
from transcribe import transcribe_api


@pytest.mark.benchmark
class TestTranscriptionPerformance:
    """Benchmark transcription performance across various scenarios."""

    def test_benchmark_short_audio_transcription(
        self,
        benchmark,
        mock_openai_api,
        test_audio_path,
        realistic_transcription_responses,
    ):
        """Benchmark transcription performance for short audio files."""
        # Configure mock with realistic short audio response
        mock_response = MagicMock()
        response_data = realistic_transcription_responses["short_audio"]
        mock_response.text = response_data["text"]
        mock_response.language = response_data["language"]
        mock_response.segments = response_data["segments"]
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        # Benchmark the transcription
        result = benchmark(transcribe_api, test_audio_path)

        # Verify result quality
        assert isinstance(result, str)
        assert len(result) > 0
        assert result == response_data["text"]

    def test_benchmark_medium_audio_transcription(
        self,
        benchmark,
        mock_openai_api,
        test_audio_path,
        realistic_transcription_responses,
    ):
        """Benchmark transcription performance for medium-length audio files."""
        # Configure mock with realistic medium-length response
        mock_response = MagicMock()
        response_data = realistic_transcription_responses["long_audio"]
        mock_response.text = response_data["text"]
        mock_response.language = response_data["language"]
        mock_response.segments = response_data["segments"]
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        # Add artificial delay to simulate longer processing
        def delayed_transcription(*args, **kwargs):
            time.sleep(0.01)  # 10ms delay to simulate processing
            return mock_response

        mock_openai_api.audio.transcriptions.create.side_effect = delayed_transcription

        # Benchmark the transcription
        result = benchmark(transcribe_api, test_audio_path)

        # Verify result quality
        assert isinstance(result, str)
        assert len(result) > 50
        assert "longer audio sample" in result

    def test_benchmark_clean_transcribe_end_to_end(
        self,
        benchmark,
        mock_openai_api,
        test_audio_path,
        temp_dir,
        realistic_transcription_responses,
    ):
        """Benchmark complete clean_transcribe workflow including file I/O."""
        # Configure mock
        mock_response = MagicMock()
        response_data = realistic_transcription_responses["short_audio"]
        mock_response.text = response_data["text"]
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        output_path = os.path.join(temp_dir, "benchmark_output.txt")

        # Benchmark the complete workflow
        transcriber = CleanTranscriber()
        benchmark(transcriber.transcribe, test_audio_path, output_path)

        # Verify output was created correctly
        assert os.path.exists(output_path)
        with open(output_path, "r") as f:
            content = f.read().strip()
            assert content == response_data["text"]

    @pytest.mark.slow
    def test_benchmark_with_api_latency_simulation(self, benchmark, mock_openai_api, test_audio_path):
        """Benchmark transcription with realistic API latency simulation."""
        # Configure mock with realistic API latency
        mock_response = MagicMock()
        mock_response.text = "Transcription with realistic latency simulation"

        def simulate_api_latency(*args, **kwargs):
            # Simulate realistic OpenAI API latency (100-500ms)
            time.sleep(0.2)  # 200ms average latency
            return mock_response

        mock_openai_api.audio.transcriptions.create.side_effect = simulate_api_latency

        # Benchmark with latency
        result = benchmark(transcribe_api, test_audio_path)

        assert result == "Transcription with realistic latency simulation"

    def test_benchmark_multiple_consecutive_calls(self, benchmark, mock_openai_api, test_audio_path):
        """Benchmark performance of multiple consecutive transcription calls."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.text = "Consecutive call transcription"
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        def multiple_transcriptions():
            """Perform multiple transcriptions to test throughput."""
            results = []
            for _ in range(5):  # Test with 5 consecutive calls
                result = transcribe_api(test_audio_path)
                results.append(result)
            return results

        # Benchmark multiple calls
        results = benchmark(multiple_transcriptions)

        # Verify all calls succeeded
        assert len(results) == 5
        assert all(result == "Consecutive call transcription" for result in results)

        # Verify API was called expected number of times
        assert mock_openai_api.audio.transcriptions.create.call_count == 5


@pytest.mark.benchmark
class TestMemoryUsagePatterns:
    """Test memory usage patterns and potential memory leaks."""

    def test_memory_usage_single_transcription(self, benchmark, mock_openai_api, test_audio_path):
        """Monitor memory usage for single transcription."""
        import tracemalloc

        # Configure mock
        mock_response = MagicMock()
        mock_response.text = "Memory usage test transcription"
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        def transcription_with_memory_tracking():
            tracemalloc.start()

            result = transcribe_api(test_audio_path)

            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Return result and memory info for analysis
            return {"result": result, "current_memory": current, "peak_memory": peak}

        # Benchmark with memory tracking
        data = benchmark(transcription_with_memory_tracking)

        # Verify transcription succeeded
        assert data["result"] == "Memory usage test transcription"

        # Memory usage should be reasonable (less than 100MB for simple case)
        assert data["peak_memory"] < 100 * 1024 * 1024  # 100MB limit

    @pytest.mark.slow
    def test_memory_stability_multiple_transcriptions(self, mock_openai_api, test_audio_path):
        """Test memory stability across multiple transcriptions."""
        import gc
        import tracemalloc

        # Configure mock
        mock_response = MagicMock()
        mock_response.text = "Memory stability test"
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        memory_measurements = []

        for i in range(10):  # Test 10 iterations
            tracemalloc.start()
            gc.collect()  # Force garbage collection

            # Perform transcription
            result = transcribe_api(test_audio_path)
            assert result == "Memory stability test"

            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            memory_measurements.append({"iteration": i, "current": current, "peak": peak})

        # Analyze memory pattern - should not continuously increase
        first_peak = memory_measurements[0]["peak"]
        last_peak = memory_measurements[-1]["peak"]

        # Memory shouldn't grow by more than 50% over 10 iterations
        memory_growth_ratio = last_peak / first_peak
        assert memory_growth_ratio < 1.5, f"Memory growth too high: {memory_growth_ratio}"


@pytest.mark.benchmark
class TestPerformanceRegression:
    """Test for performance regressions and establish baselines."""

    def test_baseline_transcription_speed(self, benchmark, mock_openai_api, test_audio_path):
        """Establish baseline performance for transcription speed."""
        # Configure mock with minimal processing
        mock_response = MagicMock()
        mock_response.text = "Baseline performance test"
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        # Set performance expectations
        benchmark.extra_info["expected_max_time"] = 1.0  # 1 second max
        benchmark.extra_info["expected_min_ops_per_sec"] = 1.0  # At least 1 op/sec

        # Benchmark with custom timing
        result = benchmark.pedantic(transcribe_api, args=(test_audio_path,), iterations=5, rounds=3)

        assert result == "Baseline performance test"

    def test_file_io_performance_baseline(self, benchmark, mock_openai_api, test_audio_path, temp_dir):
        """Establish baseline for file I/O performance in clean_transcribe."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.text = "File I/O performance baseline test with longer content to measure file write performance"
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        output_path = os.path.join(temp_dir, "io_baseline.txt")

        # Set I/O performance expectations
        benchmark.extra_info["operation_type"] = "file_io_transcription"
        benchmark.extra_info["expected_max_time"] = 2.0  # 2 seconds max for file I/O

        # Benchmark file I/O operations
        transcriber = CleanTranscriber()
        benchmark.pedantic(
            transcriber.transcribe,
            args=(test_audio_path, output_path),
            iterations=3,
            rounds=2,
        )

        # Verify output
        assert os.path.exists(output_path)
        with open(output_path, "r") as f:
            content = f.read().strip()
            assert "File I/O performance baseline test" in content

    def test_error_handling_performance_impact(self, benchmark, mock_openai_api_with_errors, test_audio_path):
        """Measure performance impact of error handling."""
        # This will test the error scenarios from mock_openai_api_with_errors

        def transcription_with_error_recovery():
            """Test transcription that encounters errors but eventually succeeds."""
            # First three calls will fail, fourth should succeed
            for attempt in range(4):
                try:
                    result = transcribe_api(test_audio_path)
                    if result:  # Successful transcription
                        return result
                except Exception:
                    if attempt == 3:  # Last attempt, re-raise
                        raise
                    continue
            return None

        # Benchmark error handling
        benchmark.extra_info["includes_error_recovery"] = True
        result = benchmark(transcription_with_error_recovery)

        assert result == "Recovery transcription after errors."


@pytest.mark.benchmark
@pytest.mark.slow
class TestConcurrencyPerformance:
    """Test performance under concurrent load scenarios."""

    def test_concurrent_transcription_simulation(self, mock_openai_api, test_audio_path):
        """Simulate concurrent transcription requests."""
        import concurrent.futures
        import threading

        # Configure mock with thread-safe counting
        call_count = threading.local()
        call_count.value = 0

        def thread_safe_mock(*args, **kwargs):
            if not hasattr(call_count, "value"):
                call_count.value = 0
            call_count.value += 1

            mock_response = MagicMock()
            mock_response.text = f"Concurrent transcription #{call_count.value}"
            return mock_response

        mock_openai_api.audio.transcriptions.create.side_effect = thread_safe_mock

        # Test concurrent execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit multiple transcription tasks
            futures = [executor.submit(transcribe_api, test_audio_path) for _ in range(5)]

            # Collect results
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Verify all transcriptions completed
        assert len(results) == 5
        assert all(isinstance(result, str) for result in results)
        assert all("Concurrent transcription #" in result for result in results)

        # Verify API was called for each request
        assert mock_openai_api.audio.transcriptions.create.call_count == 5


# Performance test configuration and utilities
def pytest_configure(config):
    """Configure pytest-benchmark settings."""
    # Add custom markers
    config.addinivalue_line("markers", "benchmark: mark test as a performance benchmark")
    config.addinivalue_line("markers", "slow: mark test as slow-running")


def pytest_benchmark_update_json(config, benchmarks, output_json):
    """Add custom metadata to benchmark results."""
    output_json["test_environment"] = {
        "python_version": sys.version,
        "platform": sys.platform,
        "test_audio_used": "mock_responses",
        "openai_api_mocked": True,
    }
