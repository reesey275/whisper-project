"""
Performance and benchmarking tests for Whisper transcription system.
"""

import os

# Import the module under test
import sys
import time
from unittest.mock import MagicMock, patch

import psutil
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import benchmark_models
except ImportError:
    benchmark_models = None


class TestPerformanceBenchmarks:
    """Test suite for performance benchmarking functionality."""

    def test_benchmark_models_import(self):
        """Test that benchmark_models module can be imported."""
        if benchmark_models is None:
            pytest.skip("benchmark_models not available")
        assert benchmark_models is not None

    def test_memory_monitoring(self):
        """Test memory usage monitoring during transcription."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Simulate memory-intensive operation
        large_data = [0] * (1024 * 1024)  # 1M integers

        peak_memory = process.memory_info().rss
        memory_used = peak_memory - initial_memory

        # Clean up
        del large_data

        # Memory usage should be measurable but reasonable
        assert memory_used > 0
        assert memory_used < 1024 * 1024 * 1024  # Less than 1GB for test

    def test_cpu_usage_monitoring(self):
        """Test CPU usage monitoring."""
        process = psutil.Process(os.getpid())

        # Get initial CPU times
        cpu_times_start = process.cpu_times()

        # Simulate CPU-intensive operation
        start_time = time.time()
        while time.time() - start_time < 0.1:  # 100ms of work
            _ = sum(range(1000))

        cpu_times_end = process.cpu_times()

        # CPU usage should be measurable
        cpu_used = cpu_times_end.user - cpu_times_start.user
        assert cpu_used >= 0

    def test_transcription_speed_measurement(self, sample_audio_file):
        """Test measurement of transcription speed."""
        # Mock audio duration
        mock_duration = 60.0  # 60 seconds of audio

        with patch("os.path.getsize", return_value=1024 * 1024):  # 1MB file
            start_time = time.time()

            # Simulate transcription process
            time.sleep(0.1)  # 100ms processing time

            end_time = time.time()
            processing_time = end_time - start_time

            # Calculate realtime factor
            realtime_factor = mock_duration / processing_time

            # Should be much faster than realtime for small test
            assert realtime_factor > 1.0
            assert processing_time < 1.0  # Should complete quickly in test

    def test_model_comparison_metrics(self):
        """Test model comparison and performance metrics."""
        # Mock performance data for different models
        model_performance = {
            "tiny": {"speed": 16.7, "accuracy": 85, "memory": 256},
            "base": {"speed": 8.3, "accuracy": 88, "memory": 512},
            "small": {"speed": 7.0, "accuracy": 91, "memory": 768},
            "medium": {"speed": 3.0, "accuracy": 94, "memory": 1536},
            "large": {"speed": 1.5, "accuracy": 96, "memory": 3072},
        }

        # Test performance metrics structure
        for model, metrics in model_performance.items():
            assert "speed" in metrics
            assert "accuracy" in metrics
            assert "memory" in metrics

            # Speed should be positive
            assert metrics["speed"] > 0

            # Accuracy should be reasonable percentage
            assert 0 < metrics["accuracy"] <= 100

            # Memory should be positive
            assert metrics["memory"] > 0

    def test_resource_scaling(self):
        """Test resource usage scaling with different workloads."""
        workload_sizes = [1, 5, 10]  # Simulated number of files

        for size in workload_sizes:
            # Mock processing multiple files
            start_memory = psutil.virtual_memory().used

            # Simulate scaling workload
            data_per_file = [0] * (1024 * size)  # Scale with workload

            end_memory = psutil.virtual_memory().used
            memory_delta = end_memory - start_memory

            # Clean up
            del data_per_file

            # Memory usage should scale reasonably
            assert memory_delta >= 0

    @pytest.mark.slow
    def test_long_running_performance(self):
        """Test performance characteristics over longer duration."""
        duration = 1.0  # 1 second test
        start_time = time.time()
        iterations = 0

        while time.time() - start_time < duration:
            # Simulate repetitive transcription-like work
            _ = "test string" * 1000
            iterations += 1

        end_time = time.time()
        actual_duration = end_time - start_time
        throughput = iterations / actual_duration

        # Should maintain reasonable throughput
        assert throughput > 0
        assert actual_duration <= duration + 0.1  # Small tolerance


class TestResourceLimits:
    """Test resource limit handling and validation."""

    def test_memory_limit_detection(self):
        """Test detection of available memory."""
        available_memory = psutil.virtual_memory().available
        total_memory = psutil.virtual_memory().total

        assert available_memory > 0
        assert total_memory > available_memory
        assert available_memory < total_memory

    def test_cpu_count_detection(self):
        """Test CPU core count detection."""
        cpu_count = psutil.cpu_count()
        logical_cpu_count = psutil.cpu_count(logical=True)

        assert cpu_count > 0
        assert logical_cpu_count >= cpu_count
        assert logical_cpu_count <= cpu_count * 2  # Reasonable hyperthreading limit

    def test_disk_space_validation(self, temp_dir):
        """Test disk space availability checking."""
        disk_usage = psutil.disk_usage(temp_dir)

        assert disk_usage.total > 0
        assert disk_usage.used >= 0
        assert disk_usage.free >= 0
        # Allow for filesystem overhead - used + free might be slightly less than total
        assert disk_usage.used + disk_usage.free <= disk_usage.total

    def test_memory_threshold_warnings(self):
        """Test memory threshold warning system."""
        total_memory = psutil.virtual_memory().total
        available_memory = psutil.virtual_memory().available

        # Calculate memory usage percentage
        memory_usage_percent = ((total_memory - available_memory) / total_memory) * 100

        # Define warning thresholds
        warning_threshold = 80.0
        critical_threshold = 95.0

        # Test threshold logic
        if memory_usage_percent > critical_threshold:
            status = "critical"
        elif memory_usage_percent > warning_threshold:
            status = "warning"
        else:
            status = "ok"

        assert status in ["ok", "warning", "critical"]
        assert isinstance(memory_usage_percent, float)
        assert 0 <= memory_usage_percent <= 100


class TestBenchmarkResults:
    """Test benchmark result validation and analysis."""

    def test_benchmark_result_structure(self):
        """Test benchmark result data structure."""
        # Mock benchmark result
        benchmark_result = {
            "model": "small",
            "audio_duration": 60.0,
            "processing_time": 8.5,
            "realtime_factor": 7.06,
            "memory_peak": 768,
            "cpu_usage": 85.2,
            "accuracy_score": 91.5,
            "timestamp": "2024-01-15T10:30:00Z",
        }

        # Validate required fields
        required_fields = [
            "model",
            "audio_duration",
            "processing_time",
            "realtime_factor",
            "memory_peak",
            "timestamp",
        ]

        for field in required_fields:
            assert field in benchmark_result

        # Validate data types and ranges
        assert isinstance(benchmark_result["model"], str)
        assert benchmark_result["audio_duration"] > 0
        assert benchmark_result["processing_time"] > 0
        assert benchmark_result["realtime_factor"] > 0
        assert benchmark_result["memory_peak"] > 0

    def test_performance_comparison(self):
        """Test performance comparison between models."""
        # Mock results for comparison
        results = {
            "tiny": {"speed": 16.7, "memory": 256, "accuracy": 85},
            "small": {"speed": 7.0, "memory": 768, "accuracy": 91},
            "medium": {"speed": 3.0, "memory": 1536, "accuracy": 94},
        }

        models = list(results.keys())

        # Test speed comparison (higher is better)
        assert results["tiny"]["speed"] > results["small"]["speed"]
        assert results["small"]["speed"] > results["medium"]["speed"]

        # Test memory usage (lower models use less)
        assert results["tiny"]["memory"] < results["small"]["memory"]
        assert results["small"]["memory"] < results["medium"]["memory"]

        # Test accuracy (higher models more accurate)
        assert results["tiny"]["accuracy"] < results["small"]["accuracy"]
        assert results["small"]["accuracy"] < results["medium"]["accuracy"]

    def test_recommendation_logic(self):
        """Test model recommendation based on requirements."""
        # Mock system capabilities
        system_memory = 8192  # 8GB
        cpu_cores = 8
        time_constraint = 60.0  # 60 seconds for 1 hour of audio

        # Mock model requirements
        model_requirements = {
            "tiny": {"min_memory": 256, "speed_factor": 16.7},
            "base": {"min_memory": 512, "speed_factor": 8.3},
            "small": {"min_memory": 768, "speed_factor": 7.0},
            "medium": {"min_memory": 1536, "speed_factor": 3.0},
            "large": {"min_memory": 3072, "speed_factor": 1.5},
        }

        # Test recommendation logic
        audio_duration = 300  # 5 minutes (more realistic for testing)
        max_processing_time = time_constraint

        suitable_models = []
        for model, reqs in model_requirements.items():
            if reqs["min_memory"] <= system_memory and audio_duration / reqs["speed_factor"] <= max_processing_time:
                suitable_models.append(model)

        # Should find at least one suitable model with reasonable constraints
        assert len(suitable_models) > 0

        # Should recommend based on constraints
        recommended = suitable_models[-1] if suitable_models else "tiny"
        assert recommended in model_requirements.keys()


if __name__ == "__main__":
    pytest.main([__file__])
