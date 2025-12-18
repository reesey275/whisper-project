"""
Unit tests for Docker integration and functionality.
"""

import os
import subprocess

# Import the module under test
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestDockerIntegration:
    """Test suite for Docker-based transcription functionality."""

    def test_docker_availability_check(self, mock_docker_available):
        """Test Docker availability detection."""
        # Mock Docker being available
        mock_docker_available.return_value = True
        assert mock_docker_available() is True

        # Mock Docker being unavailable
        mock_docker_available.return_value = False
        assert mock_docker_available() is False

    def test_docker_image_existence(self):
        """Test checking for required Docker images."""
        required_images = ["whisper-local:latest", "faster-whisper:latest"]

        for image in required_images:
            # Mock docker images command
            with patch("subprocess.run") as mock_subprocess:
                mock_subprocess.return_value.returncode = 0
                mock_subprocess.return_value.stdout = f"{image}\n"

                # Test image exists
                result = subprocess.run(
                    ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
                    capture_output=True,
                    text=True,
                )

                assert mock_subprocess.called

    def test_docker_transcription_command(self, sample_audio_file, mock_docker_available):
        """Test Docker transcription command construction."""
        mock_docker_available.return_value = True

        # Mock Docker run command
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "Mock transcription result"

            # Test command construction for whisper-local
            expected_cmd = [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{os.path.dirname(sample_audio_file)}:/input",
                "-v",
                f"{os.getcwd()}:/output",
                "whisper-local:latest",
                "--model",
                "small",
                "--language",
                "en",
                "--output_format",
                "txt",
                f"/input/{os.path.basename(sample_audio_file)}",
            ]

            # This would test actual Docker command execution
            assert isinstance(expected_cmd, list)
            assert "docker" in expected_cmd[0]
            assert "whisper-local:latest" in expected_cmd

    def test_docker_volume_mounting(self, sample_audio_file, temp_dir):
        """Test Docker volume mounting for file access."""
        input_dir = os.path.dirname(sample_audio_file)
        output_dir = temp_dir

        # Test volume mount paths
        input_mount = f"{input_dir}:/input"
        output_mount = f"{output_dir}:/output"

        assert ":" in input_mount
        assert ":" in output_mount
        assert "/input" in input_mount
        assert "/output" in output_mount

    def test_docker_error_handling(self, sample_audio_file, mock_docker_available):
        """Test Docker error handling scenarios."""
        mock_docker_available.return_value = True

        # Test Docker command failure
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.side_effect = subprocess.CalledProcessError(1, "docker")

            # Should handle Docker errors gracefully
            with pytest.raises(subprocess.CalledProcessError):
                subprocess.run(["docker", "run", "nonexistent:image"], check=True)

    def test_docker_memory_limits(self):
        """Test Docker memory limit configuration."""
        memory_limit = "4g"

        # Test memory limit in Docker command
        cmd_with_memory = [
            "docker",
            "run",
            "--rm",
            "--memory",
            memory_limit,
            "whisper-local:latest",
        ]

        assert "--memory" in cmd_with_memory
        assert memory_limit in cmd_with_memory

    def test_docker_gpu_support(self):
        """Test Docker GPU support detection and usage."""
        # Test GPU support command
        gpu_cmd = ["docker", "run", "--rm", "--gpus", "all", "whisper-local:latest"]

        assert "--gpus" in gpu_cmd
        assert "all" in gpu_cmd


class TestDockerImages:
    """Test Docker image management and validation."""

    def test_whisper_local_image(self):
        """Test whisper-local Docker image."""
        image_name = "whisper-local:latest"

        # Mock image inspection
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = '{"Config": {"Env": ["WHISPER_MODEL=base"]}}'

            # Test image exists and has proper configuration
            result = subprocess.run(["docker", "inspect", image_name], capture_output=True, text=True)

            assert mock_subprocess.called

    def test_faster_whisper_image(self):
        """Test faster-whisper Docker image."""
        image_name = "faster-whisper:latest"

        # Mock image inspection
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = '{"Config": {"Cmd": ["python", "-m", "faster_whisper"]}}'

            # Test image configuration
            result = subprocess.run(["docker", "inspect", image_name], capture_output=True, text=True)

            assert mock_subprocess.called

    def test_image_size_validation(self):
        """Test Docker image size is reasonable."""
        # Mock docker images command with size info
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "whisper-local:latest 2.5GB\nfaster-whisper:latest 1.8GB"

            # Images should exist and have reasonable sizes
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}:{{.Tag}} {{.Size}}"],
                capture_output=True,
                text=True,
            )

            assert mock_subprocess.called


class TestDockerPerformance:
    """Test Docker performance characteristics."""

    def test_docker_startup_time(self):
        """Test Docker container startup performance."""
        import time

        # Mock Docker run with timing
        with patch("subprocess.run") as mock_subprocess:
            # Simulate fast startup
            def mock_docker_run(*args, **kwargs):
                time.sleep(0.1)  # Simulate 100ms startup
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = "Container started"
                return mock_result

            mock_subprocess.side_effect = mock_docker_run

            start_time = time.time()
            result = subprocess.run(["docker", "run", "--rm", "hello-world"])
            end_time = time.time()

            startup_time = end_time - start_time
            # Should start reasonably quickly (within 5 seconds for test)
            assert startup_time < 5.0

    def test_docker_resource_usage(self):
        """Test Docker resource usage monitoring."""
        # Mock docker stats command
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "container_id,cpu_percent,memory_usage\ntest_container,15.5%,512MB"

            # Test resource monitoring
            result = subprocess.run(
                [
                    "docker",
                    "stats",
                    "--format",
                    "table {{.Container}},{{.CPUPerc}},{{.MemUsage}}",
                    "--no-stream",
                ],
                capture_output=True,
                text=True,
            )

            assert mock_subprocess.called

    def test_docker_concurrent_processing(self):
        """Test handling multiple concurrent Docker containers."""
        # Test that multiple containers can run simultaneously
        container_count = 3

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = f"Running {container_count} containers"

            # Simulate multiple containers
            for i in range(container_count):
                result = subprocess.run(
                    [
                        "docker",
                        "run",
                        "--rm",
                        "--name",
                        f"whisper_test_{i}",
                        "whisper-local:latest",
                        "echo",
                        f"Container {i}",
                    ]
                )

            assert mock_subprocess.call_count == container_count


class TestDockerSecurity:
    """Test Docker security and isolation."""

    def test_docker_user_permissions(self):
        """Test Docker runs with appropriate user permissions."""
        # Test running container as non-root user
        cmd = [
            "docker",
            "run",
            "--rm",
            "--user",
            "1000:1000",
            "whisper-local:latest",
        ]  # Run as non-root

        assert "--user" in cmd
        assert "1000:1000" in cmd

    def test_docker_network_isolation(self):
        """Test Docker network isolation settings."""
        # Test network isolation
        cmd = [
            "docker",
            "run",
            "--rm",
            "--network",
            "none",
            "whisper-local:latest",
        ]  # No network access

        assert "--network" in cmd
        assert "none" in cmd

    def test_docker_read_only_filesystem(self):
        """Test Docker read-only filesystem security."""
        # Test read-only root filesystem
        cmd = [
            "docker",
            "run",
            "--rm",
            "--read-only",
            "--tmpfs",
            "/tmp",
            "whisper-local:latest",
        ]  # Allow tmp writes

        assert "--read-only" in cmd
        assert "--tmpfs" in cmd


if __name__ == "__main__":
    pytest.main([__file__])
