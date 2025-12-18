# API Reference Documentation

Complete reference for all transcription interfaces, classes, and methods in the Whisper project.

## 📋 Table of Contents

- [Quick Reference](#-quick-reference)
- [Universal Interface (transcribe.py)](#-universal-interface-transcribepy)
- [Clean Interface (clean_transcribe.py)](#-clean-interface-clean_transcribepy)
- [Local Transcription (local_transcribe.py)](#-local-transcription-local_transcribepy)
- [Docker Transcription (docker_transcribe.py)](#-docker-transcription-docker_transcribepy)
- [API Transcription (api_transcribe.py)](#-api-transcription-api_transcribepy)
- [Return Values and Error Handling](#-return-values-and-error-handling)
- [Integration Examples](#-integration-examples)

## 🚀 Quick Reference

### Command Line Interfaces

| Script | Purpose | Best For |
|--------|---------|----------|
| `transcribe.py` | **Universal interface** with auto-detection | All users (recommended) |
| `clean_transcribe.py` | **Organized outputs** with clean file management | Production workflows |
| `local_transcribe.py` | Direct local Whisper usage | Development/testing |
| `docker_transcribe.py` | Docker-based transcription | Containerized environments |
| `api_transcribe.py` | OpenAI API transcription | Cloud-based processing |

### Common Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio_file` | `str` | Required | Path to audio/video file |
| `--model`, `-m` | `str` | `"small"` | Whisper model size |
| `--language`, `-l` | `str` | `"en"` | Language code |
| `--output-dir`, `-o` | `str` | `"output"` | Output directory |

## 🔄 Universal Interface (transcribe.py)

### Command Line Usage

```bash
python transcribe.py <audio_file> [options]
```

### Parameters

#### Required
- `audio_file` (str): Path to audio or video file

#### Optional
| Flag | Long Form | Type | Default | Description |
|------|-----------|------|---------|-------------|
| `-m` | `--model` | str | `"small"` | Model: tiny, base, small, medium, large |
| `-l` | `--language` | str | `"en"` | Language code (en, es, fr, de, auto) |
| `-o` | `--output-dir` | str | `"output"` | Output directory path |
| `-f` | `--format` | str | `"txt"` | Output format: txt, srt, vtt, json |
| `-v` | `--verbose` | flag | `False` | Enable verbose output |
| | `--method` | str | `"auto"` | Force method: local, docker, api |

### Method Auto-Detection Logic

```python
def detect_best_method():
    """
    Priority order:
    1. Local installation (if available)
    2. Docker (if containers available)
    3. API (if OPENAI_API_KEY set)
    """
    if local_whisper_available():
        return "local"
    elif docker_available():
        return "docker"
    elif api_key_available():
        return "api"
    else:
        raise EnvironmentError("No transcription method available")
```

### Examples

```bash
# Auto-detect best method
python transcribe.py interview.mp4

# Force specific method
python transcribe.py interview.mp4 --method docker

# Custom output and quality
python transcribe.py interview.mp4 --model medium --output-dir results

# Multiple formats
python transcribe.py interview.mp4 --format srt
python transcribe.py interview.mp4 --format vtt
```

### Return Values

#### Success
```python
{
    "success": True,
    "method_used": "local",
    "model": "small",
    "language": "en",
    "files_created": [
        "output/interview_small.txt",
        "output/interview_small.srt",
        "output/interview_small.vtt"
    ],
    "processing_time": 12.34,
    "audio_duration": 120.5
}
```

#### Error
```python
{
    "success": False,
    "error": "File not found: nonexistent.mp4",
    "method_attempted": "local",
    "troubleshooting": "Check file path and permissions"
}
```

## 🎯 Clean Interface (clean_transcribe.py)

### Command Line Usage

```bash
python clean_transcribe.py <audio_file> [options]
python clean_transcribe.py --list [--dev]
```

### CleanTranscriber Class

```python
class CleanTranscriber:
    """
    Clean, organized transcription interface with managed outputs.
    """

    def __init__(self, base_output_dir="output"):
        """
        Initialize transcriber with organized directory structure.

        Args:
            base_output_dir (str): Base directory for all outputs
        """

    def transcribe(self, audio_file, model="small", language="en",
                  mode="production"):
        """
        Transcribe audio with organized output management.

        Args:
            audio_file (str): Path to audio/video file
            model (str): Whisper model size
            language (str): Language code
            mode (str): "production" or "development"

        Returns:
            dict: Transcription results with file paths
        """

    def list_transcriptions(self, mode="production"):
        """
        List existing transcriptions with metadata.

        Args:
            mode (str): "production" or "development"

        Returns:
            list: Transcription file information
        """
```

### Usage Examples

#### Python Integration
```python
from clean_transcribe import CleanTranscriber

# Initialize transcriber
transcriber = CleanTranscriber()

# Production transcription
result = transcriber.transcribe(
    audio_file="meeting.mp4",
    model="medium",
    language="en",
    mode="production"
)

# Check results
if result['success']:
    for file_path in result['files']:
        print(f"Created: {file_path}")

# List existing transcriptions
transcriptions = transcriber.list_transcriptions(mode="production")
for item in transcriptions:
    print(f"File: {item['filename']}")
    print(f"Model: {item['model']}")
    print(f"Size: {item['size']} bytes")
```

### Directory Structure Management

#### Production Mode
- **Format**: `filename_model_YYYYMMDD_HHMMSS.ext`
- **Location**: `output/production/`
- **Purpose**: Timestamped files for archival

#### Development Mode
- **Format**: `filename_model.ext`
- **Location**: `output/development/`
- **Purpose**: Simple names for iteration

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio_file` | str | Required | Audio/video file path |
| `--model`, `-m` | str | `"small"` | Whisper model |
| `--language`, `-l` | str | `"en"` | Language code |
| `--dev` | flag | False | Development mode |
| `--list` | flag | False | List transcriptions |

## 🔧 Local Transcription (local_transcribe.py)

### Direct Whisper Usage

```bash
python local_transcribe.py <audio_file> [options]
```

### LocalTranscriber Class

```python
class LocalTranscriber:
    """Direct interface to locally installed Whisper."""

    def __init__(self):
        """Initialize with dependency checking."""

    def transcribe(self, audio_file, model="small", language="en",
                  output_dir="output"):
        """
        Transcribe using local Whisper installation.

        Args:
            audio_file (str): Input file path
            model (str): Model size (tiny, base, small, medium, large)
            language (str): Language code or "auto"
            output_dir (str): Output directory

        Returns:
            dict: Transcription results
        """

    def available_models(self):
        """Get list of available models."""

    def model_info(self, model_name):
        """Get model size and performance information."""
```

### Model Management

```python
# Check available models
transcriber = LocalTranscriber()
models = transcriber.available_models()
print(f"Available models: {models}")

# Get model information
info = transcriber.model_info("small")
print(f"Model size: {info['size']}")
print(f"Parameters: {info['parameters']}")
```

### Performance Optimization

```python
# Enable GPU acceleration (if available)
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Memory management for large files
transcriber.transcribe(
    audio_file="large_file.mp4",
    model="small",  # Use smaller model for large files
    language="en"   # Specify language to skip detection
)
```

## 🐳 Docker Transcription (docker_transcribe.py)

### Container-Based Processing

```bash
python docker_transcribe.py <audio_file> [options]
```

### DockerTranscriber Class

```python
class DockerTranscriber:
    """Docker-based transcription interface."""

    def __init__(self, image="whisper-local:latest"):
        """
        Initialize with Docker image.

        Args:
            image (str): Docker image name
        """

    def transcribe(self, audio_file, model="small", language="en",
                  output_dir="output"):
        """
        Transcribe using Docker container.

        Args:
            audio_file (str): Input file path
            model (str): Model size
            language (str): Language code
            output_dir (str): Output directory

        Returns:
            dict: Transcription results
        """

    def list_images(self):
        """List available Docker images."""

    def container_status(self):
        """Check container availability."""
```

### Docker Image Options

| Image | Purpose | Models | Size |
|-------|---------|--------|------|
| `whisper-local:latest` | Standard Whisper | All models | ~2GB |
| `faster-whisper:latest` | Optimized Whisper | All models | ~1.5GB |
| `whisper-gpu:latest` | GPU acceleration | All models | ~3GB |

### Volume Mapping

```python
# Automatic volume mapping
transcriber = DockerTranscriber()
result = transcriber.transcribe(
    audio_file="/host/path/audio.mp4",  # Host path
    output_dir="/host/path/output"      # Host output
)
# Container automatically maps: /host/path -> /app/data
```

### Advanced Docker Usage

```python
# Custom image
transcriber = DockerTranscriber(image="faster-whisper:latest")

# Check container status
status = transcriber.container_status()
if status['available']:
    print(f"Container ready: {status['image']}")

# List available images
images = transcriber.list_images()
for image in images:
    print(f"Image: {image['name']}, Size: {image['size']}")
```

## ☁️ API Transcription (api_transcribe.py)

### OpenAI API Integration

```bash
export OPENAI_API_KEY="your-api-key-here"
python api_transcribe.py <audio_file> [options]
```

### APITranscriber Class

```python
class APITranscriber:
    """OpenAI API transcription interface."""

    def __init__(self, api_key=None):
        """
        Initialize with API key.

        Args:
            api_key (str): OpenAI API key (or from environment)
        """

    def transcribe(self, audio_file, model="whisper-1", language="en",
                  output_dir="output"):
        """
        Transcribe using OpenAI API.

        Args:
            audio_file (str): Input file path
            model (str): API model name
            language (str): Language code
            output_dir (str): Output directory

        Returns:
            dict: Transcription results with API metadata
        """

    def get_usage(self):
        """Get API usage statistics."""

    def estimate_cost(self, audio_file):
        """Estimate transcription cost."""
```

### API Models

| Model | Purpose | Cost | Limits |
|-------|---------|------|--------|
| `whisper-1` | Standard API model | $0.006/minute | 25MB max file |

### Cost Management

```python
# Estimate cost before processing
transcriber = APITranscriber()
cost_estimate = transcriber.estimate_cost("long_audio.mp4")
print(f"Estimated cost: ${cost_estimate['total']:.2f}")

if cost_estimate['total'] < 5.00:  # Budget limit
    result = transcriber.transcribe("long_audio.mp4")
```

### File Size Handling

```python
# Automatic file splitting for large files
def transcribe_large_file(audio_file):
    """Handle files larger than API limits."""
    file_size = os.path.getsize(audio_file)

    if file_size > 25 * 1024 * 1024:  # 25MB limit
        print("File too large, splitting...")
        # Implementation splits file and processes chunks
        return transcribe_split_file(audio_file)
    else:
        return transcriber.transcribe(audio_file)
```

## 📊 Return Values and Error Handling

### Standard Return Format

All transcription methods return consistent dictionary format:

```python
{
    # Success indicator
    "success": bool,

    # Transcription results
    "text": str,              # Plain text transcription
    "segments": list,         # Timestamped segments
    "language": str,          # Detected/specified language

    # File information
    "files_created": list,    # Output file paths
    "output_directory": str,  # Output directory path

    # Processing metadata
    "method_used": str,       # transcription method
    "model": str,             # model used
    "processing_time": float, # seconds taken
    "audio_duration": float,  # audio length in seconds

    # Error information (if success=False)
    "error": str,             # error message
    "error_type": str,        # error category
    "troubleshooting": str    # helpful suggestions
}
```

### Error Categories

#### File Errors
```python
{
    "error_type": "FileError",
    "error": "File not found: audio.mp4",
    "troubleshooting": "Check file path and permissions"
}
```

#### Model Errors
```python
{
    "error_type": "ModelError",
    "error": "Model 'huge' not available",
    "troubleshooting": "Available models: tiny, base, small, medium, large"
}
```

#### Environment Errors
```python
{
    "error_type": "EnvironmentError",
    "error": "No transcription method available",
    "troubleshooting": "Install Whisper, setup Docker, or configure API key"
}
```

#### Processing Errors
```python
{
    "error_type": "ProcessingError",
    "error": "Transcription failed: corrupted audio",
    "troubleshooting": "Check audio file format and integrity"
}
```

### Error Handling Patterns

#### Basic Error Handling
```python
result = transcriber.transcribe("audio.mp4")

if result['success']:
    print(f"Transcription: {result['text']}")
    print(f"Files: {result['files_created']}")
else:
    print(f"Error: {result['error']}")
    print(f"Suggestion: {result['troubleshooting']}")
```

#### Robust Error Handling
```python
def safe_transcribe(audio_file, fallback_model="small"):
    """Transcribe with automatic fallback and retry logic."""

    try:
        # Try primary method
        result = transcriber.transcribe(audio_file, model="medium")

        if result['success']:
            return result

        # Try fallback model
        print(f"Retrying with {fallback_model} model...")
        result = transcriber.transcribe(audio_file, model=fallback_model)

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "UnexpectedError",
            "troubleshooting": "Check logs and system resources"
        }
```

## 🔗 Integration Examples

### Batch Processing

```python
import os
from pathlib import Path

def batch_transcribe(input_dir, output_dir="batch_output"):
    """Transcribe all audio files in a directory."""

    audio_extensions = ['.mp3', '.mp4', '.wav', '.m4a']
    results = []

    for file_path in Path(input_dir).iterdir():
        if file_path.suffix.lower() in audio_extensions:
            print(f"Processing: {file_path.name}")

            result = transcriber.transcribe(
                str(file_path),
                model="small",
                output_dir=output_dir
            )

            results.append({
                "file": file_path.name,
                "success": result['success'],
                "processing_time": result.get('processing_time', 0)
            })

    return results

# Usage
results = batch_transcribe("input_audio/")
successful = sum(1 for r in results if r['success'])
print(f"Processed {successful}/{len(results)} files successfully")
```

### Web Application Integration

```python
from flask import Flask, request, jsonify
import tempfile
import os

app = Flask(__name__)
transcriber = CleanTranscriber()

@app.route('/transcribe', methods=['POST'])
def api_transcribe():
    """Web endpoint for transcription."""

    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files['audio']
    model = request.form.get('model', 'small')
    language = request.form.get('language', 'en')

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False,
                                   suffix=os.path.splitext(file.filename)[1]) as tmp:
        file.save(tmp.name)

        # Transcribe
        result = transcriber.transcribe(
            tmp.name,
            model=model,
            language=language,
            mode="production"
        )

        # Cleanup
        os.unlink(tmp.name)

        return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

### Async Processing

```python
import asyncio
import concurrent.futures

async def async_transcribe_batch(audio_files, max_workers=3):
    """Asynchronously transcribe multiple files."""

    loop = asyncio.get_event_loop()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all transcription tasks
        tasks = [
            loop.run_in_executor(
                executor,
                transcriber.transcribe,
                audio_file,
                "small",  # model
                "en"      # language
            )
            for audio_file in audio_files
        ]

        # Wait for all to complete
        results = await asyncio.gather(*tasks)

    return results

# Usage
audio_files = ["file1.mp4", "file2.mp4", "file3.mp4"]
results = asyncio.run(async_transcribe_batch(audio_files))

for i, result in enumerate(results):
    print(f"File {i+1}: {'Success' if result['success'] else 'Failed'}")
```

### Custom Output Processing

```python
def transcribe_with_summary(audio_file, model="small"):
    """Transcribe and generate summary."""

    # Transcribe
    result = transcriber.transcribe(audio_file, model=model)

    if not result['success']:
        return result

    # Add summary processing
    text = result['text']
    word_count = len(text.split())
    duration = result.get('audio_duration', 0)

    # Calculate statistics
    wpm = word_count / (duration / 60) if duration > 0 else 0

    # Enhance result
    result.update({
        "statistics": {
            "word_count": word_count,
            "duration_minutes": duration / 60,
            "words_per_minute": round(wpm, 1),
            "character_count": len(text)
        }
    })

    return result

# Usage
result = transcribe_with_summary("meeting.mp4", model="medium")
if result['success']:
    stats = result['statistics']
    print(f"Transcribed {stats['word_count']} words in {stats['duration_minutes']:.1f} minutes")
    print(f"Speaking rate: {stats['words_per_minute']} WPM")
```

## 📚 Advanced Usage Patterns

### Configuration Management

```python
# Create configuration file
config = {
    "default_model": "small",
    "default_language": "en",
    "output_directory": "transcriptions",
    "quality_settings": {
        "draft": {"model": "tiny", "language": "auto"},
        "standard": {"model": "small", "language": "en"},
        "high": {"model": "medium", "language": "en"},
        "premium": {"model": "large", "language": "en"}
    }
}

def transcribe_with_quality(audio_file, quality="standard"):
    """Transcribe using predefined quality settings."""
    settings = config["quality_settings"][quality]

    return transcriber.transcribe(
        audio_file,
        model=settings["model"],
        language=settings["language"],
        output_dir=config["output_directory"]
    )
```

### Plugin System

```python
class TranscriptionPlugin:
    """Base class for transcription plugins."""

    def pre_process(self, audio_file):
        """Called before transcription."""
        return audio_file

    def post_process(self, result):
        """Called after transcription."""
        return result

class NoiseReductionPlugin(TranscriptionPlugin):
    """Plugin to reduce background noise."""

    def pre_process(self, audio_file):
        # Apply noise reduction
        cleaned_file = apply_noise_reduction(audio_file)
        return cleaned_file

class SentimentAnalysisPlugin(TranscriptionPlugin):
    """Plugin to analyze sentiment."""

    def post_process(self, result):
        if result['success']:
            sentiment = analyze_sentiment(result['text'])
            result['sentiment'] = sentiment
        return result

# Usage with plugins
transcriber = PluginTranscriber(plugins=[
    NoiseReductionPlugin(),
    SentimentAnalysisPlugin()
])

result = transcriber.transcribe("meeting.mp4")
print(f"Sentiment: {result.get('sentiment', 'N/A')}")
```

---

**Related Documentation**:
- [CLEAN_TRANSCRIBE_GUIDE.md](CLEAN_TRANSCRIBE_GUIDE.md) - User-friendly transcription guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Problem solving and debugging
- [MODEL_SELECTION_GUIDE.md](MODEL_SELECTION_GUIDE.md) - Model comparison and selection
- [EXAMPLES.md](EXAMPLES.md) - Real-world usage examples
