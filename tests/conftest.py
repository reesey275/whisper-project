"""
Test configuration and fixtures for test suite.

Professional test infrastructure with stabilized imports and comprehensive markers.
"""

import os
import shutil
import struct
import sys
import tempfile
import wave
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Professional import system - eliminate per-file sys.path hacks
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_configure(config):
    """Configure pytest markers for professional test categorization."""
    config.addinivalue_line("markers", "integration: hits docker/network/external services")
    config.addinivalue_line("markers", "slow: long-running tests (>1 second)")
    config.addinivalue_line(
        "markers",
        "xfail_doc: documenting current behavior - may fail during refactoring",
    )
    config.addinivalue_line("markers", "property: property-based tests with Hypothesis")
    config.addinivalue_line("markers", "benchmark: performance measurement tests")
    config.addinivalue_line("markers", "flaky: tests with non-deterministic behavior")


# Optional imports for enhanced testing
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Import OpenAI exceptions for mocking
try:
    from openai import APIConnectionError, BadRequestError, RateLimitError
except ImportError:
    # Fallback for testing when openai is not available
    class RateLimitError(Exception):
        def __init__(self, message, response=None, body=None):
            super().__init__(message)
            self.response = response
            self.body = body

    class APIConnectionError(Exception):
        pass

    class BadRequestError(Exception):
        def __init__(self, message, response=None, body=None):
            super().__init__(message)
            self.response = response
            self.body = body


# Test data directory
TEST_DATA_DIR = Path(__file__).parents[1] / "test_audio"
TEST_AUDIO_PATH = TEST_DATA_DIR / "test_sample.wav"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_audio_path():
    """Provide path to test audio file."""
    return str(TEST_AUDIO_PATH)


@pytest.fixture
def mock_whisper_model():
    """Mock Whisper model for testing without actual model loading."""
    # Mock the entire whisper module to avoid import issues
    with patch.dict("sys.modules", {"whisper": MagicMock()}):
        with patch("local.transcribe_local.whisper") as mock_whisper:
            mock_model = MagicMock()
            mock_model.transcribe.return_value = {
                "text": "This is a test transcription.",
                "segments": [
                    {
                        "id": 0,
                        "seek": 0,
                        "start": 0.0,
                        "end": 2.0,
                        "text": "This is a test transcription.",
                        "tokens": [1, 2, 3],
                        "temperature": 0.0,
                        "avg_logprob": -0.5,
                        "compression_ratio": 1.0,
                        "no_speech_prob": 0.1,
                    }
                ],
                "language": "en",
            }
            mock_whisper.load_model.return_value = mock_model
            yield mock_model


@pytest.fixture
def sample_audio_file(temp_dir):
    """Create a sample audio file for testing."""
    # Create a minimal WAV file (44 bytes header + 1 second of silence)
    audio_path = os.path.join(temp_dir, "test_audio.wav")

    # WAV header for 1 second of silence at 44.1kHz, 16-bit, mono
    wav_header = bytes(
        [
            0x52,
            0x49,
            0x46,
            0x46,  # "RIFF"
            0x2C,
            0x00,
            0x00,
            0x00,  # File size - 8
            0x57,
            0x41,
            0x56,
            0x45,  # "WAVE"
            0x66,
            0x6D,
            0x74,
            0x20,  # "fmt "
            0x10,
            0x00,
            0x00,
            0x00,  # Subchunk1Size (16)
            0x01,
            0x00,  # AudioFormat (PCM)
            0x01,
            0x00,  # NumChannels (1)
            0x44,
            0xAC,
            0x00,
            0x00,  # SampleRate (44100)
            0x88,
            0x58,
            0x01,
            0x00,  # ByteRate
            0x02,
            0x00,  # BlockAlign
            0x10,
            0x00,  # BitsPerSample (16)
            0x64,
            0x61,
            0x74,
            0x61,  # "data"
            0x00,
            0x00,
            0x00,
            0x00,  # Subchunk2Size (0 - silence)
        ]
    )

    with open(audio_path, "wb") as f:
        f.write(wav_header)

    return audio_path


@pytest.fixture
def mock_docker_available():
    """Mock Docker availability."""
    with patch("subprocess.run") as mock_subprocess:
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Docker version 20.10.0"
        yield mock_subprocess


@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API with realistic response structure."""
    # Mock OpenAI module before it gets imported to avoid circular imports
    mock_openai_module = MagicMock()
    mock_openai_class = MagicMock()
    mock_openai_module.OpenAI = mock_openai_class

    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    # Create realistic transcription response
    mock_response = MagicMock()
    mock_response.text = "This is a test transcription from OpenAI API."
    mock_response.language = "en"
    mock_response.duration = 5.0
    mock_response.segments = [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 5.0,
            "text": "This is a test transcription from OpenAI API.",
            "tokens": [1, 2, 3, 4, 5],
            "temperature": 0.0,
            "avg_logprob": -0.5,
            "compression_ratio": 1.5,
            "no_speech_prob": 0.1,
        }
    ]

    mock_client.audio.transcriptions.create.return_value = mock_response

    with patch.dict("sys.modules", {"openai": mock_openai_module}):
        yield mock_client


@pytest.fixture
def mock_openai_api_with_errors():
    """Mock OpenAI API that simulates various error conditions."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()

        def side_effect(*args, **kwargs):
            # Simulate different error types based on call count
            if not hasattr(side_effect, "call_count"):
                side_effect.call_count = 0
            side_effect.call_count += 1

            if side_effect.call_count == 1:
                # First call: Rate limit error
                raise RateLimitError("Rate limit exceeded", response=MagicMock(), body=None)
            elif side_effect.call_count == 2:
                # Second call: API connection error
                raise APIConnectionError("Connection failed")
            elif side_effect.call_count == 3:
                # Third call: Invalid file format error
                raise BadRequestError("Invalid file format", response=MagicMock(), body=None)
            else:
                # Subsequent calls: Success
                mock_response = MagicMock()
                mock_response.text = "Recovery transcription after errors."
                return mock_response

        mock_client.audio.transcriptions.create.side_effect = side_effect
        mock_openai.return_value = mock_client
        yield mock_client


@pytest.fixture
def realistic_transcription_responses():
    """Provide various realistic transcription response scenarios."""
    return {
        "short_audio": {
            "text": "Hello, this is a short audio sample.",
            "language": "en",
            "duration": 2.5,
            "segments": [
                {
                    "id": 0,
                    "seek": 0,
                    "start": 0.0,
                    "end": 2.5,
                    "text": "Hello, this is a short audio sample.",
                    "tokens": [15496, 11, 428, 318, 257, 1790, 6597, 6291, 13],
                    "temperature": 0.0,
                    "avg_logprob": -0.3,
                    "compression_ratio": 1.2,
                    "no_speech_prob": 0.05,
                }
            ],
        },
        "long_audio": {
            "text": "This is a longer audio sample with multiple sentences. It contains various words and phrases that might be challenging to transcribe accurately. The sample includes different speech patterns and vocabulary.",
            "language": "en",
            "duration": 15.7,
            "segments": [
                {
                    "id": 0,
                    "seek": 0,
                    "start": 0.0,
                    "end": 5.2,
                    "text": "This is a longer audio sample with multiple sentences.",
                    "tokens": [1212, 318, 257, 2392, 6597, 6291, 351, 3294, 13439, 13],
                    "temperature": 0.0,
                    "avg_logprob": -0.4,
                    "compression_ratio": 1.8,
                    "no_speech_prob": 0.02,
                },
                {
                    "id": 1,
                    "seek": 5200,
                    "start": 5.2,
                    "end": 10.8,
                    "text": "It contains various words and phrases that might be challenging to transcribe accurately.",
                    "tokens": [
                        1026,
                        4909,
                        2972,
                        2456,
                        290,
                        20144,
                        326,
                        1244,
                        307,
                        9389,
                        284,
                        26905,
                        7713,
                        13,
                    ],
                    "temperature": 0.0,
                    "avg_logprob": -0.5,
                    "compression_ratio": 2.1,
                    "no_speech_prob": 0.01,
                },
                {
                    "id": 2,
                    "seek": 10800,
                    "start": 10.8,
                    "end": 15.7,
                    "text": "The sample includes different speech patterns and vocabulary.",
                    "tokens": [464, 6291, 3407, 1180, 4046, 7572, 290, 25818, 13],
                    "temperature": 0.0,
                    "avg_logprob": -0.3,
                    "compression_ratio": 1.6,
                    "no_speech_prob": 0.03,
                },
            ],
        },
        "noisy_audio": {
            "text": "This audio has background noise that makes transcription challenging.",
            "language": "en",
            "duration": 4.2,
            "segments": [
                {
                    "id": 0,
                    "seek": 0,
                    "start": 0.0,
                    "end": 4.2,
                    "text": "This audio has background noise that makes transcription challenging.",
                    "tokens": [1212, 6597, 468, 4469, 7838, 326, 1838, 26905, 9389, 13],
                    "temperature": 0.2,
                    "avg_logprob": -0.8,
                    "compression_ratio": 1.4,
                    "no_speech_prob": 0.15,
                }
            ],
        },
        "multilingual": {
            "text": "Hello, bonjour, hola, こんにちは.",
            "language": "en",  # Detected as primary language
            "duration": 3.1,
            "segments": [
                {
                    "id": 0,
                    "seek": 0,
                    "start": 0.0,
                    "end": 3.1,
                    "text": "Hello, bonjour, hola, こんにちは.",
                    "tokens": [
                        15496,
                        11,
                        5351,
                        30963,
                        11,
                        289,
                        5708,
                        11,
                        220,
                        8525,
                        10520,
                        20412,
                        13,
                    ],
                    "temperature": 0.1,
                    "avg_logprob": -0.6,
                    "compression_ratio": 1.3,
                    "no_speech_prob": 0.08,
                }
            ],
        },
        "empty_audio": {"text": "", "language": "en", "duration": 0.0, "segments": []},
    }


@pytest.fixture
def performance_audio_samples():
    """Generate mock audio data for performance testing."""
    if not NUMPY_AVAILABLE:
        pytest.skip("NumPy not available for performance testing")

    def generate_sample(duration_seconds=5.0, sample_rate=16000):
        """Generate a simple sine wave audio sample for testing."""
        t = np.linspace(0, duration_seconds, int(sample_rate * duration_seconds), False)
        frequency = 440  # A4 note
        audio_data = np.sin(2 * np.pi * frequency * t)
        return audio_data.astype(np.float32)

    return {
        "short": generate_sample(1.0),  # 1 second
        "medium": generate_sample(10.0),  # 10 seconds
        "long": generate_sample(60.0),  # 1 minute
        "very_long": generate_sample(300.0),  # 5 minutes
    }


@pytest.fixture
def edge_case_files(temp_dir):
    """Create various edge case files for testing."""
    edge_cases = {}

    # Empty audio file
    empty_path = os.path.join(temp_dir, "empty.wav")
    with wave.open(empty_path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b"")
    edge_cases["empty_audio"] = empty_path

    # Very short audio (< 0.1 seconds)
    short_path = os.path.join(temp_dir, "very_short.wav")
    with wave.open(short_path, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        # 0.05 seconds of silence
        frames = struct.pack("<" + "h" * 800, *([0] * 800))
        wav_file.writeframes(frames)
    edge_cases["very_short"] = short_path

    # Corrupted file (invalid format)
    corrupted_path = os.path.join(temp_dir, "corrupted.wav")
    with open(corrupted_path, "wb") as f:
        f.write(b"This is not a valid audio file content")
    edge_cases["corrupted"] = corrupted_path

    # Non-existent file path
    edge_cases["non_existent"] = os.path.join(temp_dir, "does_not_exist.wav")

    return edge_cases


# Test constants
TEST_TRANSCRIPTION_TEXT = "This is a test transcription."
TEST_SEGMENTS = [
    {
        "id": 0,
        "seek": 0,
        "start": 0.0,
        "end": 2.0,
        "text": TEST_TRANSCRIPTION_TEXT,
        "tokens": [1, 2, 3],
        "temperature": 0.0,
        "avg_logprob": -0.5,
        "compression_ratio": 1.0,
        "no_speech_prob": 0.1,
    }
]

TEST_RESULT = {
    "text": TEST_TRANSCRIPTION_TEXT,
    "segments": TEST_SEGMENTS,
    "language": "en",
}
