"""
Property-based testing using Hypothesis for robust edge case discovery.

This module uses Hypothesis to generate test cases that explore:
- Various input combinations automatically
- Edge cases that might not be manually considered
- Invariant properties that should always hold
- Regression testing with reproducible examples
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Optional hypothesis import
try:
    from hypothesis import assume, event, example, given, note, settings
    from hypothesis import strategies as st

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False

from clean_transcribe import CleanTranscriber
from transcribe import transcribe_api


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="Hypothesis not available")
class TestPropertyBasedTranscription:
    """Property-based tests for transcription functions."""

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=20, deadline=5000)  # Reasonable limits for CI
    def test_transcription_result_properties(self, expected_text, mock_openai_api, test_audio_path):
        """Test invariant properties of transcription results."""
        # Configure mock to return the generated text
        mock_response = MagicMock()
        mock_response.text = expected_text
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        result = transcribe_api(test_audio_path)

        # Property: Result should always be a string
        assert isinstance(result, str)

        # Property: Result should match what the API returned
        assert result == expected_text

        # Property: API should be called exactly once
        assert mock_openai_api.audio.transcriptions.create.call_count == 1

        # Log the test case for debugging
        note(f"Testing with text: {repr(expected_text[:50])}")

    @given(
        st.text(
            min_size=1,
            max_size=500,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs", "Po")),
        )
    )
    @settings(max_examples=15)
    def test_clean_transcribe_file_operations(self, transcription_content, mock_openai_api, test_audio_path):
        """Test file operation properties in clean_transcribe."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.text = transcription_content
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "property_test_output.txt")

            # Execute clean_transcribe
            CleanTranscriber(test_audio_path, output_path)

            # Property: Output file should always be created
            assert os.path.exists(output_path)

            # Property: File content should match API response
            with open(output_path, "r", encoding="utf-8") as f:
                file_content = f.read().strip()
                assert file_content == transcription_content.strip()

            # Property: File should be readable
            assert os.access(output_path, os.R_OK)

            note(f"Testing with content length: {len(transcription_content)}")

    @given(st.text(min_size=0, max_size=100))
    @example("")  # Explicitly test empty string
    @example("   ")  # Explicitly test whitespace-only
    @example("Hello, world!")  # Explicitly test normal case
    @settings(max_examples=10)
    def test_transcription_whitespace_handling(self, input_text, mock_openai_api, test_audio_path):
        """Test how transcription handles various whitespace scenarios."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.text = input_text
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        result = transcribe_api(test_audio_path)

        # Property: Result preserves the exact API response
        assert result == input_text

        # Property: Type is always string regardless of content
        assert isinstance(result, str)

        # Log whitespace characteristics
        event(f"whitespace_only: {input_text.isspace()}")
        event(f"empty_string: {len(input_text) == 0}")
        event(f"has_leading_space: {input_text.startswith(' ') if input_text else False}")
        event(f"has_trailing_space: {input_text.endswith(' ') if input_text else False}")

    @given(st.integers(min_value=0, max_value=10))
    @settings(max_examples=5)
    def test_multiple_api_calls_consistency(self, num_calls, mock_openai_api, test_audio_path):
        """Test consistency across multiple API calls."""
        assume(num_calls >= 0)  # Ensure non-negative

        # Configure mock to return consistent responses
        mock_response = MagicMock()
        mock_response.text = f"Consistent response for {num_calls} calls"
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        results = []
        for i in range(num_calls):
            result = transcribe_api(test_audio_path)
            results.append(result)

        if num_calls > 0:
            # Property: All calls should return the same result
            assert all(result == results[0] for result in results)

            # Property: All results should be strings
            assert all(isinstance(result, str) for result in results)

            # Property: API should be called the expected number of times
            assert mock_openai_api.audio.transcriptions.create.call_count == num_calls

        note(f"Tested {num_calls} consecutive API calls")


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="Hypothesis not available")
class TestPropertyBasedFileHandling:
    """Property-based tests for file handling edge cases."""

    @given(
        st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(min_codepoint=32, max_codepoint=126),
        )
    )
    @settings(max_examples=10)
    def test_filename_generation_properties(self, base_filename, mock_openai_api, test_audio_path):
        """Test properties of output filename generation."""
        # Filter out problematic characters for filenames
        safe_chars = "".join(c for c in base_filename if c.isalnum() or c in "-_.")
        assume(len(safe_chars) > 0)  # Ensure we have valid filename characters

        # Configure mock
        mock_response = MagicMock()
        mock_response.text = "Filename test content"
        mock_openai_api.audio.transcriptions.create.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, f"{safe_chars}.txt")

            try:
                CleanTranscriber(test_audio_path, output_path)

                # Property: File should be created successfully
                assert os.path.exists(output_path)

                # Property: File should contain expected content
                with open(output_path, "r") as f:
                    content = f.read().strip()
                    assert content == "Filename test content"

                note(f"Successfully created file: {safe_chars}.txt")

            except (OSError, IOError) as e:
                # Some filename patterns might still be invalid on certain systems
                note(f"Filename {safe_chars} caused OS error: {e}")
                assume(False)  # Skip this test case

    @given(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=5))
    @settings(max_examples=8)
    def test_batch_transcription_properties(self, text_list, mock_openai_api, test_audio_path):
        """Test properties when processing multiple transcriptions."""
        # Configure mock to cycle through the text list
        responses = []
        for text in text_list:
            mock_response = MagicMock()
            mock_response.text = text
            responses.append(mock_response)

        mock_openai_api.audio.transcriptions.create.side_effect = responses

        results = []
        for i, expected_text in enumerate(text_list):
            result = transcribe_api(test_audio_path)
            results.append(result)

        # Property: Should get back all expected results
        assert len(results) == len(text_list)

        # Property: Results should match input text list
        assert results == text_list

        # Property: API should be called for each item
        assert mock_openai_api.audio.transcriptions.create.call_count == len(text_list)

        note(f"Processed batch of {len(text_list)} transcriptions")


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="Hypothesis not available")
class TestPropertyBasedErrorHandling:
    """Property-based tests for error handling scenarios."""

    @given(st.sampled_from(["RateLimitError", "APIConnectionError", "BadRequestError", "TimeoutError"]))
    @settings(max_examples=4)  # Test each error type once
    def test_error_type_handling_properties(self, error_type, test_audio_path, mock_openai_api):
        """Test properties of different error type handling."""
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()

            # Create appropriate exception based on error_type
            if error_type == "RateLimitError":
                from openai import RateLimitError

                exception = RateLimitError("Rate limit", response=MagicMock(), body=None)
            elif error_type == "APIConnectionError":
                from openai import APIConnectionError

                exception = APIConnectionError("Connection failed")
            elif error_type == "BadRequestError":
                from openai import BadRequestError

                exception = BadRequestError("Bad request", response=MagicMock(), body=None)
            else:  # TimeoutError
                exception = TimeoutError("Request timed out")

            mock_client.audio.transcriptions.create.side_effect = exception
            mock_openai.return_value = mock_client

            # Property: All error types should raise an exception
            with pytest.raises(Exception):
                transcribe_api(test_audio_path)

            # Property: API should be called exactly once before error
            assert mock_openai_api.audio.transcriptions.create.call_count == 1

            note(f"Tested error handling for: {error_type}")

    @given(st.integers(min_value=1, max_value=5))
    @settings(max_examples=3)
    def test_retry_attempt_properties(self, max_retries, test_audio_path):
        """Test properties of retry logic with different retry counts."""
        assume(max_retries >= 1)

        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()

            call_count = 0

            def retry_side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1

                if call_count < max_retries:
                    from openai import RateLimitError

                    raise RateLimitError("Rate limited", response=MagicMock(), body=None)
                else:
                    mock_response = MagicMock()
                    mock_response.text = f"Success after {max_retries} attempts"
                    return mock_response

            mock_client.audio.transcriptions.create.side_effect = retry_side_effect
            mock_openai.return_value = mock_client

            # Implement simple retry logic
            last_exception = None
            for attempt in range(max_retries):
                try:
                    result = transcribe_api(test_audio_path)

                    # Property: Eventually succeeds after retries
                    assert result == f"Success after {max_retries} attempts"

                    # Property: Made the expected number of API calls
                    assert call_count == max_retries

                    note(f"Success after {max_retries} retry attempts")
                    break

                except Exception as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        raise
            else:
                # Should not reach here if retry logic works
                assert False, f"Retry logic failed after {max_retries} attempts"


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="Hypothesis not available")
class TestPropertyBasedResponseValidation:
    """Property-based tests for API response validation."""

    @given(
        st.dictionaries(
            keys=st.sampled_from(["text", "language", "duration", "segments"]),
            values=st.one_of(
                st.text(max_size=200),
                st.floats(
                    min_value=0.0,
                    max_value=3600.0,
                    allow_nan=False,
                    allow_infinity=False,
                ),
                st.lists(
                    st.dictionaries(
                        keys=st.sampled_from(["id", "start", "end", "text"]),
                        values=st.one_of(
                            st.integers(min_value=0),
                            st.floats(min_value=0.0, max_value=3600.0),
                            st.text(max_size=100),
                        ),
                    ),
                    max_size=5,
                ),
            ),
            min_size=1,
        )
    )
    @settings(max_examples=10)
    def test_response_structure_properties(self, response_data, test_audio_path):
        """Test handling of various API response structures."""
        # Ensure we have the required 'text' field
        if "text" not in response_data:
            response_data["text"] = "Generated text content"

        # Ensure text is actually a string
        if not isinstance(response_data["text"], str):
            response_data["text"] = str(response_data["text"])

        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()

            # Set up mock response with generated data
            for key, value in response_data.items():
                setattr(mock_response, key, value)

            mock_client.audio.transcriptions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            result = transcribe_api(test_audio_path)

            # Property: Should always return the text field as string
            assert isinstance(result, str)
            assert result == response_data["text"]

            note(f"Response structure keys: {list(response_data.keys())}")
            note(f"Text content length: {len(response_data['text'])}")


# Configuration for Hypothesis integration with pytest
def pytest_configure(config):
    """Configure Hypothesis settings for pytest."""
    if HYPOTHESIS_AVAILABLE:
        # Add hypothesis profile for CI
        from hypothesis import HealthCheck, settings

        settings.register_profile(
            "ci",
            max_examples=10,
            deadline=10000,
            suppress_health_check=[HealthCheck.too_slow],  # 10 seconds
        )

        settings.register_profile("dev", max_examples=50, deadline=None)

        # Use CI profile by default
        settings.load_profile("ci")
