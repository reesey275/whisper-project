"""
Unit tests for clean_transcribe.py CleanTranscriber class.
"""

import os
import shutil
import subprocess

# Import the module under test
import sys
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import clean_transcribe
    from clean_transcribe import CleanTranscriber
except ImportError:
    CleanTranscriber = None


class TestCleanTranscriber:
    """Test suite for CleanTranscriber class."""

    @pytest.fixture
    def transcriber(self):
        """Create a CleanTranscriber instance for testing."""
        if CleanTranscriber is None:
            pytest.skip("CleanTranscriber not available")
        return CleanTranscriber()

    def test_init_default_directories(self):
        """Test initialization with default directory structure."""
        if CleanTranscriber is None:
            pytest.skip("CleanTranscriber not available")

        transcriber = CleanTranscriber()
        assert hasattr(transcriber, "base_dir")
        assert hasattr(transcriber, "production_dir")
        assert hasattr(transcriber, "development_dir")
        assert hasattr(transcriber, "archive_dir")

        # Should create proper directory structure
        assert transcriber.base_dir.name == "output"
        assert transcriber.production_dir.name == "production"
        assert transcriber.development_dir.name == "development"
        assert transcriber.archive_dir.name == "archive"

    def test_directory_creation(self):
        """Test that required directories are created."""
        if CleanTranscriber is None:
            pytest.skip("CleanTranscriber not available")

        transcriber = CleanTranscriber()
        # Directories should exist after initialization
        assert transcriber.production_dir.exists()
        assert transcriber.development_dir.exists()
        assert transcriber.archive_dir.exists()

    def test_get_clean_output_path(self, transcriber, sample_audio_file):
        """Test that clean output paths are generated correctly."""
        if transcriber is None:
            pytest.skip("CleanTranscriber not available")

        # Test production mode
        output_dir, filename_base = transcriber.get_clean_output_path(sample_audio_file, mode="production", model="small")

        assert output_dir == transcriber.production_dir
        assert "small" in filename_base
        # Should include timestamp in production
        today = datetime.now().strftime("%Y%m%d")
        assert today in filename_base

        # Test development mode
        output_dir, filename_base = transcriber.get_clean_output_path(sample_audio_file, mode="development", model="base")

        assert output_dir == transcriber.development_dir
        assert "base" in filename_base

    def test_transcribe_method_signature(self, transcriber, sample_audio_file):
        """Test transcription method with proper parameters."""
        if transcriber is None:
            pytest.skip("CleanTranscriber not available")

        # Mock subprocess to avoid actual transcription
        with patch("clean_transcribe.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "Mock output"

            # Test that transcribe method accepts expected parameters
            with patch("clean_transcribe.Path.glob", return_value=[]):
                result = transcriber.transcribe(sample_audio_file, model="small", language="en", mode="development")

                # Should return result dictionary
                assert isinstance(result, dict)
                assert "success" in result

    def test_production_vs_development_mode(self, transcriber, sample_audio_file):
        """Test differences between production and development modes."""
        if transcriber is None:
            pytest.skip("CleanTranscriber not available")

        # Test production mode path
        prod_dir, prod_filename = transcriber.get_clean_output_path(sample_audio_file, mode="production", model="small")
        assert prod_dir == transcriber.production_dir

        # Test development mode path
        dev_dir, dev_filename = transcriber.get_clean_output_path(sample_audio_file, mode="development", model="small")
        assert dev_dir == transcriber.development_dir

        # Production should have timestamps, development simpler names
        assert len(prod_filename) > len(dev_filename)

    def test_list_transcriptions_method(self, transcriber):
        """Test list_transcriptions functionality."""
        if transcriber is None:
            pytest.skip("CleanTranscriber not available")

        # Test with empty directory
        result = transcriber.list_transcriptions(mode="production")
        assert isinstance(result, list)

        result = transcriber.list_transcriptions(mode="development")
        assert isinstance(result, list)

    def test_file_naming_convention(self, transcriber, sample_audio_file):
        """Test file naming follows consistent conventions."""
        if transcriber is None:
            pytest.skip("CleanTranscriber not available")

        # Test filename generation directly
        output_dir, filename_base = transcriber.get_clean_output_path(sample_audio_file, mode="production", model="small")

        # Should include original filename
        original_name = os.path.splitext(os.path.basename(sample_audio_file))[0]
        assert original_name in filename_base

        # Should include model name
        assert "small" in filename_base

        # Should have timestamp in production mode
        today = datetime.now().strftime("%Y%m%d")
        assert today in filename_base

    def test_error_handling_graceful(self, transcriber, sample_audio_file):
        """Test graceful error handling."""
        if transcriber is None:
            pytest.skip("CleanTranscriber not available")

        # Test with non-existent file
        nonexistent_file = "/path/to/nonexistent/file.mp3"

        # Mock subprocess to simulate error
        with patch("clean_transcribe.subprocess.run") as mock_subprocess:
            mock_subprocess.side_effect = subprocess.CalledProcessError(1, "cmd")

            result = transcriber.transcribe(nonexistent_file)
            assert isinstance(result, dict)
            assert "success" in result

    def test_audio_file_validation(self, transcriber, sample_audio_file):
        """Test validation of audio file inputs."""
        if transcriber is None:
            pytest.skip("CleanTranscriber not available")

        # Test that sample audio file exists and has content
        assert os.path.exists(sample_audio_file)
        assert os.path.getsize(sample_audio_file) > 0

        # Test path handling
        from pathlib import Path

        audio_path = Path(sample_audio_file)
        assert audio_path.exists()
        assert audio_path.is_file()


class TestCleanTranscriberIntegration:
    """Integration tests for CleanTranscriber with actual transcription methods."""

    @pytest.fixture
    def transcriber(self):
        """Create a CleanTranscriber instance for integration testing."""
        if CleanTranscriber is None:
            pytest.skip("CleanTranscriber not available")
        return CleanTranscriber()

    def test_integration_with_subprocess(self, transcriber, sample_audio_file):
        """Test integration with subprocess transcription."""
        if transcriber is None:
            pytest.skip("CleanTranscriber not available")

        # Mock successful subprocess call
        with patch("clean_transcribe.subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = "Mock successful transcription"

            with (
                patch("clean_transcribe.Path.glob") as mock_glob,
                patch("clean_transcribe.shutil.move") as mock_move,
            ):
                # Mock finding output files - return empty list to skip file operations
                mock_glob.return_value = []

                result = transcriber.transcribe(sample_audio_file, model="small")
                assert isinstance(result, dict)
                assert "success" in result

    def test_integration_error_handling(self, transcriber, sample_audio_file):
        """Test integration error handling."""
        if transcriber is None:
            pytest.skip("CleanTranscriber not available")

        # Mock subprocess failure
        with patch("clean_transcribe.subprocess.run") as mock_subprocess:
            mock_subprocess.side_effect = subprocess.CalledProcessError(1, "transcribe")
            mock_subprocess.stderr = "Mock error output"

            result = transcriber.transcribe(sample_audio_file)
            assert isinstance(result, dict)
            assert "success" in result


class TestOutputManagement:
    """Test output file management and organization."""

    def test_output_directory_structure(self):
        """Test automatic creation of output directories."""
        if CleanTranscriber is None:
            pytest.skip("CleanTranscriber not available")

        transcriber = CleanTranscriber()

        # All required directories should exist
        assert transcriber.base_dir.exists()
        assert transcriber.production_dir.exists()
        assert transcriber.development_dir.exists()
        assert transcriber.archive_dir.exists()

    def test_filename_generation(self, sample_audio_file):
        """Test filename generation for different modes."""
        if CleanTranscriber is None:
            pytest.skip("CleanTranscriber not available")

        transcriber = CleanTranscriber()

        # Test production filename (with timestamp)
        prod_dir, prod_filename = transcriber.get_clean_output_path(sample_audio_file, mode="production", model="small")
        assert "small" in prod_filename
        assert "_" in prod_filename  # Should have timestamp separator

        # Test development filename (simpler)
        dev_dir, dev_filename = transcriber.get_clean_output_path(sample_audio_file, mode="development", model="base")
        assert "base" in dev_filename
        # Development mode should be simpler
        assert dev_filename.count("_") <= prod_filename.count("_")

    def test_path_handling(self, sample_audio_file):
        """Test proper handling of file paths."""
        if CleanTranscriber is None:
            pytest.skip("CleanTranscriber not available")

        transcriber = CleanTranscriber()

        # Should handle Path objects correctly
        from pathlib import Path

        audio_path = Path(sample_audio_file)

        output_dir, filename_base = transcriber.get_clean_output_path(str(audio_path), mode="production")

        assert output_dir.exists()
        assert audio_path.stem in filename_base


if __name__ == "__main__":
    pytest.main([__file__])
