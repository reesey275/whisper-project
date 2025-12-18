"""
Test edge cases and error scenarios for Whisper transcription.

This module tests various edge cases including:
- Empty and very short audio files
- Corrupted or invalid audio files
- API error scenarios and recovery
- File system edge cases
- Network timeout scenarios
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from clean_transcribe import CleanTranscriber
from transcribe import transcribe_api


class TestFileEdgeCases:
    """Test edge cases related to file handling."""

    def test_empty_audio_file(self, edge_case_files, mock_openai_api, realistic_transcription_responses):
        """Test transcription of completely empty audio file."""
        # Configure mock to return empty transcription
        mock_response = MagicMock()
        mock_response.text = realistic_transcription_responses["empty_audio"]["text"]
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        result = transcribe_api(edge_case_files["empty_audio"])

        # Should handle empty audio gracefully
        assert result == ""
        mock_openai_api.audio.transcriptions.create.assert_called_once()

    def test_very_short_audio_file(self, edge_case_files, mock_openai_api, realistic_transcription_responses):
        """Test transcription of very short audio file (< 0.1 seconds)."""
        # Configure mock for short audio
        mock_response = MagicMock()
        mock_response.text = realistic_transcription_responses["short_audio"]["text"]
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        result = transcribe_api(edge_case_files["very_short"])

        # Should handle very short audio
        assert isinstance(result, str)
        assert len(result) > 0
        mock_openai_api.audio.transcriptions.create.assert_called_once()

    def test_non_existent_file(self, edge_case_files):
        """Test handling of non-existent audio file."""
        with pytest.raises(FileNotFoundError):
            transcribe_api(edge_case_files["non_existent"])

    def test_corrupted_audio_file(self, edge_case_files, mock_openai_api_with_errors):
        """Test handling of corrupted/invalid audio file."""
        # The corrupted file should trigger an API error when processed
        with pytest.raises(Exception):  # Should raise BadRequestError or similar
            transcribe_api(edge_case_files["corrupted"])

    def test_invalid_file_path_types(self):
        """Test handling of invalid file path types."""
        invalid_paths = [None, 123, [], {}]

        for invalid_path in invalid_paths:
            with pytest.raises((TypeError, ValueError, AttributeError)):
                transcribe_api(invalid_path)

    def test_empty_string_path(self):
        """Test handling of empty string as file path."""
        with pytest.raises((FileNotFoundError, ValueError)):
            transcribe_api("")

    def test_directory_instead_of_file(self, temp_dir):
        """Test handling when a directory path is provided instead of file."""
        with pytest.raises((IsADirectoryError, PermissionError, OSError)):
            transcribe_api(temp_dir)


class TestAPIErrorScenarios:
    """Test various API error scenarios and recovery mechanisms."""

    def test_rate_limit_error_handling(self, mock_openai_api_with_errors, test_audio_path):
        """Test handling of OpenAI API rate limit errors."""
        # The mock_openai_api_with_errors fixture simulates rate limit on first call
        with pytest.raises(Exception):  # Should raise RateLimitError
            transcribe_api(test_audio_path)

    def test_api_connection_error_handling(self, mock_openai_api_with_errors, test_audio_path):
        """Test handling of API connection errors."""
        # First call will fail with rate limit, need to trigger second call
        try:
            transcribe_api(test_audio_path)
        except:
            pass  # First call expected to fail

        # Second call should trigger connection error
        with pytest.raises(Exception):  # Should raise APIConnectionError
            transcribe_api(test_audio_path)

    def test_invalid_file_format_error(self, mock_openai_api_with_errors, test_audio_path):
        """Test handling of invalid file format errors from API."""
        # Need to trigger the third call which raises BadRequestError
        for _ in range(2):
            try:
                transcribe_api(test_audio_path)
            except:
                pass

        # Third call should trigger invalid format error
        with pytest.raises(Exception):  # Should raise BadRequestError
            transcribe_api(test_audio_path)

    def test_api_recovery_after_errors(self, mock_openai_api_with_errors, test_audio_path):
        """Test that API calls can recover after initial errors."""
        # First three calls will fail, fourth should succeed
        for _ in range(3):
            try:
                transcribe_api(test_audio_path)
            except:
                pass  # Expected failures

        # Fourth call should succeed
        result = transcribe_api(test_audio_path)
        assert result == "Recovery transcription after errors."

    @pytest.mark.slow
    def test_timeout_handling(self, test_audio_path):
        """Test handling of API timeout scenarios."""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()

            # Simulate timeout
            import time

            def timeout_side_effect(*args, **kwargs):
                time.sleep(0.1)  # Short delay for testing
                raise TimeoutError("Request timed out")

            mock_client.audio.transcriptions.create.side_effect = timeout_side_effect
            mock_openai.return_value = mock_client

            with pytest.raises(TimeoutError):
                transcribe_api(test_audio_path)


class TestTranscriptionQualityEdgeCases:
    """Test edge cases related to transcription quality and content."""

    def test_noisy_audio_transcription(self, mock_openai_api, realistic_transcription_responses, test_audio_path):
        """Test transcription of noisy audio with low confidence."""
        # Configure mock for noisy audio response
        mock_response = MagicMock()
        response_data = realistic_transcription_responses["noisy_audio"]
        mock_response.text = response_data["text"]
        mock_response.language = response_data["language"]
        mock_response.segments = response_data["segments"]
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        result = transcribe_api(test_audio_path)

        # Should still return transcription even for noisy audio
        assert isinstance(result, str)
        assert len(result) > 0
        # Check that the result contains expected challenging transcription
        assert "background noise" in result
        assert "challenging" in result

    def test_multilingual_audio_transcription(self, mock_openai_api, realistic_transcription_responses, test_audio_path):
        """Test transcription of multilingual audio content."""
        # Configure mock for multilingual response
        mock_response = MagicMock()
        response_data = realistic_transcription_responses["multilingual"]
        mock_response.text = response_data["text"]
        mock_response.language = response_data["language"]
        mock_response.segments = response_data["segments"]
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        result = transcribe_api(test_audio_path)

        # Should handle multilingual content
        assert isinstance(result, str)
        assert "Hello" in result
        assert "bonjour" in result
        assert "hola" in result
        assert "こんにちは" in result

    def test_long_audio_with_segments(self, mock_openai_api, realistic_transcription_responses, test_audio_path):
        """Test transcription of long audio with multiple segments."""
        # Configure mock for long audio with segments
        mock_response = MagicMock()
        response_data = realistic_transcription_responses["long_audio"]
        mock_response.text = response_data["text"]
        mock_response.language = response_data["language"]
        mock_response.segments = response_data["segments"]
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        result = transcribe_api(test_audio_path)

        # Should handle long audio with multiple segments
        assert isinstance(result, str)
        assert len(result) > 50  # Should be substantial text
        assert "longer audio sample" in result
        assert "multiple sentences" in result
        assert "speech patterns" in result


class TestCleanTranscribeEdgeCases:
    """Test edge cases specific to the clean_transcribe function."""

    def test_clean_transcribe_with_empty_result(self, mock_openai_api, temp_dir, test_audio_path):
        """Test clean_transcribe when transcription returns empty result."""
        # Configure mock to return empty transcription
        mock_response = MagicMock()
        mock_response.text = ""
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        output_path = os.path.join(temp_dir, "empty_output.txt")
        CleanTranscriber(test_audio_path, output_path)

        # Should create output file even with empty content
        assert os.path.exists(output_path)
        with open(output_path, "r") as f:
            content = f.read().strip()
            assert content == ""

    def test_clean_transcribe_with_invalid_output_path(self, mock_openai_api, test_audio_path):
        """Test clean_transcribe with invalid output directory."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.text = "Test transcription"
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        invalid_output_path = "/nonexistent/directory/output.txt"

        with pytest.raises((FileNotFoundError, OSError, PermissionError)):
            CleanTranscriber(test_audio_path, invalid_output_path)

    def test_clean_transcribe_output_file_permissions(self, mock_openai_api, test_audio_path, temp_dir):
        """Test clean_transcribe with various output file permission scenarios."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.text = "Test transcription for permissions"
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        output_path = os.path.join(temp_dir, "permissions_test.txt")

        # Test normal case first
        CleanTranscriber(test_audio_path, output_path)
        assert os.path.exists(output_path)

        # Verify content was written correctly
        with open(output_path, "r") as f:
            content = f.read().strip()
            assert content == "Test transcription for permissions"


class TestParameterValidation:
    """Test parameter validation and type checking."""

    def test_transcribe_audio_parameter_types(self):
        """Test transcribe_audio with various invalid parameter types."""
        invalid_inputs = [
            None,
            123,
            [],
            {},
            True,
            False,
        ]

        for invalid_input in invalid_inputs:
            with pytest.raises((TypeError, ValueError, AttributeError)):
                transcribe_api(invalid_input)

    def test_clean_transcribe_parameter_validation(self, test_audio_path):
        """Test clean_transcribe parameter validation."""
        # Test invalid input file
        with pytest.raises((TypeError, ValueError, AttributeError)):
            CleanTranscriber(None, "output.txt")

        # Test invalid output file
        with pytest.raises((TypeError, ValueError, AttributeError)):
            CleanTranscriber(test_audio_path, None)

    def test_path_object_handling(self, mock_openai_api, test_audio_path):
        """Test that functions properly handle Path objects vs strings."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.text = "Path object test"
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        # Test with Path object
        path_obj = Path(test_audio_path)
        result = transcribe_api(path_obj)

        assert result == "Path object test"
        mock_openai_api.audio.transcriptions.create.assert_called_once()
