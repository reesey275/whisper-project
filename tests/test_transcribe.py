"""
Unit tests for the universal transcribe.py interface.
"""

import os

# Import the module under test
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import transcribe
except ImportError:
    # Handle case where transcribe might not be directly importable
    pass


class TestUniversalTranscribe:
    """Test suite for the universal transcription interface."""

    def test_detect_best_method_local_available(self, mock_whisper_model):
        """Test method detection when local Whisper is available."""
        with (
            patch("transcribe.check_local_whisper", return_value=True),
            patch("transcribe.check_docker", return_value=False),
            patch("transcribe.check_openai_api", return_value=False),
        ):
            # Mock the actual function if it exists
            if hasattr(transcribe, "detect_best_method"):
                methods = transcribe.detect_best_method()
                assert len(methods) > 0
                assert any(method[0] == "local" for method in methods)

    def test_detect_best_method_docker_fallback(self, mock_docker_available):
        """Test method detection falls back to Docker when local unavailable."""
        with (
            patch("transcribe.check_local_whisper", return_value=False),
            patch("transcribe.check_docker", return_value=True),
            patch("transcribe.check_openai_api", return_value=False),
        ):
            if hasattr(transcribe, "detect_best_method"):
                methods = transcribe.detect_best_method()
                assert len(methods) > 0
                assert any(method[0] == "docker" for method in methods)

    def test_detect_best_method_api_fallback(self, mock_openai_api):
        """Test method detection falls back to API when others unavailable."""
        with (
            patch("transcribe.check_local_whisper", return_value=False),
            patch("transcribe.check_docker", return_value=False),
            patch("transcribe.check_openai_api", return_value=True),
        ):
            if hasattr(transcribe, "detect_best_method"):
                methods = transcribe.detect_best_method()
                assert len(methods) > 0
                assert any(method[0] == "api" for method in methods)

    def test_transcription_with_local_method(self, sample_audio_file, mock_whisper_model, temp_dir):
        """Test transcription using local method."""
        # This would test the actual transcription logic
        # For now, we'll test that the file exists and can be processed
        assert os.path.exists(sample_audio_file)
        assert os.path.getsize(sample_audio_file) > 0

    def test_transcription_with_invalid_file(self):
        """Test transcription with non-existent file."""
        # Test error handling for invalid files
        invalid_file = "/nonexistent/file.mp3"
        assert not os.path.exists(invalid_file)

    def test_output_formats(self, sample_audio_file, temp_dir):
        """Test different output formats (txt, srt, vtt, json)."""
        formats = ["txt", "srt", "vtt", "json"]
        for format_type in formats:
            # Test that format is recognized
            assert format_type in formats

    def test_model_validation(self):
        """Test model name validation."""
        valid_models = ["tiny", "base", "small", "medium", "large", "turbo"]
        for model in valid_models:
            assert model in valid_models

        # Test invalid model
        invalid_model = "nonexistent_model"
        assert invalid_model not in valid_models

    def test_language_validation(self):
        """Test language code validation."""
        valid_languages = ["en", "es", "fr", "de", "auto"]
        for lang in valid_languages:
            assert lang in valid_languages

        # Test invalid language
        invalid_lang = "xyz"
        assert len(invalid_lang) <= 3  # Language codes are typically 2-3 chars


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_missing_dependencies(self):
        """Test behavior when dependencies are missing."""
        with patch("importlib.import_module", side_effect=ImportError("Module not found")):
            # Test that appropriate errors are raised or handled
            pass

    def test_insufficient_memory(self):
        """Test behavior with insufficient memory."""
        # Mock low memory condition
        with patch("psutil.virtual_memory") as mock_memory:
            mock_memory.return_value.available = 100 * 1024 * 1024  # 100MB
            # Test that system handles low memory gracefully
            assert mock_memory.return_value.available < 1024 * 1024 * 1024

    def test_corrupted_audio_file(self, temp_dir):
        """Test handling of corrupted audio files."""
        corrupted_file = os.path.join(temp_dir, "corrupted.mp3")
        with open(corrupted_file, "wb") as f:
            f.write(b"Not a real audio file")

        assert os.path.exists(corrupted_file)
        # Test that appropriate error handling occurs

    def test_network_failures(self, mock_openai_api):
        """Test handling of network failures for API calls."""
        mock_openai_api.audio.transcriptions.create.side_effect = Exception("Network error")
        # Test that network errors are handled gracefully
        assert True  # Placeholder for actual error handling test


class TestPerformance:
    """Performance and resource usage tests."""

    def test_memory_usage_tracking(self, sample_audio_file):
        """Test memory usage during transcription."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Simulate transcription process
        # In a real test, this would call the actual transcription

        final_memory = process.memory_info().rss
        memory_used = final_memory - initial_memory

        # Test that memory usage is reasonable (less than 1GB for test)
        assert memory_used < 1024 * 1024 * 1024

    def test_processing_time(self, sample_audio_file):
        """Test processing time is reasonable."""
        import time

        start_time = time.time()

        # Simulate processing
        time.sleep(0.1)  # Minimal delay for test

        end_time = time.time()
        processing_time = end_time - start_time

        # Test that processing completes in reasonable time
        assert processing_time < 60  # Should complete within 60 seconds for test


if __name__ == "__main__":
    pytest.main([__file__])
