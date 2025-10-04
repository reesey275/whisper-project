# Whisper Transcription Project 🎵→📝

![CI Pipeline](https://github.com/reesey275/whisper-project/workflows/Enterprise%20CI%20Pipeline/badge.svg)
![Quality Gate](https://img.shields.io/badge/quality-black%20%7C%20isort%20%7C%20flake8%20%7C%20mypy%20%7C%20bandit%20%7C%20safety-blue)
![Tests](https://img.shields.io/badge/tests-73%20total-green)
![Coverage](https://img.shields.io/badge/coverage-25%25%20→%2040%25-orange)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive, production-ready Whisper transcription system with multiple processing methods, organized output management, and Docker deployment capabilities.

**✨ Key Features:**
- 🎯 **Multiple Processing Methods**: Local, Docker, and API transcription
- 📁 **Organized Outputs**: Clean, timestamped, production-ready files
- 🐳 **Multi-Stack Deployment**: Scale to handle multiple projects
- 🤖 **Smart Model Selection**: From fast `tiny` to accurate `large` models
- 🌍 **English-Optimized**: Defaults to English for best performance
- 🔧 **Developer-Friendly**: Comprehensive documentation and examples

## 🚀 Quick Start

Choose your preferred approach based on your needs:

### 🔹 1. Local Installation (Simple & Reliable)
Best for: One-off transcriptions, learning, full control

```bash
# Install dependencies
pip install -U openai-whisper

# Run transcription
python local/transcribe_local.py yourfile.mp3 --model medium --language en
```

### 🔹 2. Docker (Zero Dependencies)
Best for: Avoiding Python conflicts, production use, GPU acceleration

```bash
# Using the provided script
./docker/transcribe_docker.sh whisper yourfile.mp3 medium en

# Or using Python wrapper
python docker/transcribe_docker.py yourfile.mp3 --faster-whisper --gpu
```

### 🔹 3. Cloud API (Zero Setup)
Best for: No local resources, high-quality results, minimal friction

```bash
# Set your API key
export OPENAI_API_KEY="your_api_key_here"

# Run transcription
python api/transcribe_api.py yourfile.mp3 --response-format srt
```

## 📁 Project Structure

```
whisper-project/
├── 📂 local/                 # Local Whisper installation
│   └── transcribe_local.py   # Full-featured local transcription script
├── 📂 docker/                # Docker-based solutions
│   ├── transcribe_docker.sh  # Bash scripts for Docker containers
│   ├── transcribe_docker.py  # Python wrapper for Docker
│   └── docker-compose.yml    # Docker Compose configuration
├── 📂 api/                   # Cloud API clients
│   ├── transcribe_api.py     # OpenAI API client
│   └── alternative_apis.py   # AssemblyAI, Rev AI, Speechmatics
├── 📂 input/                 # Place your audio files here
├── 📂 output/                # Transcription results go here
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 📋 Requirements & Setup

### System Requirements
- Python 3.8+
- For GPU acceleration: NVIDIA GPU + CUDA drivers
- For Docker: Docker Desktop or Docker Engine

### Installation Options

#### Option 1: Local Whisper
```bash
pip install -r requirements.txt
```

#### Option 2: Docker (no Python dependencies needed)
```bash
# Check Docker is running
docker --version

# Pull images (optional, will auto-pull when needed)
docker pull ghcr.io/onedr0p/whisper
docker pull ghcr.io/guillaumekln/faster-whisper
```

#### Option 3: API Keys Setup
```bash
# OpenAI API
export OPENAI_API_KEY="sk-your-key-here"

# Alternative services (optional)
export ASSEMBLYAI_API_KEY="your-assemblyai-key"
export REV_AI_API_KEY="your-rev-key"
export SPEECHMATICS_API_KEY="your-speechmatics-key"
```

## 🎯 Usage Examples

### Local Transcription

#### Basic Usage
```bash
# Simple transcription
python local/transcribe_local.py audio.mp3

# With specific model and language
python local/transcribe_local.py video.mp4 --model large --language en

# Translate to English
python local/transcribe_local.py spanish_audio.wav --task translate
```

#### Advanced Options
```bash
# Custom output directory
python local/transcribe_local.py podcast.mp3 --output-dir ./transcripts

# Quiet mode (minimal output)
python local/transcribe_local.py audio.wav --quiet
```

### Docker Transcription

#### Using Bash Scripts
```bash
# Standard Whisper
./docker/transcribe_docker.sh whisper audio.mp3 medium en ./output

# Faster Whisper (recommended)
./docker/transcribe_docker.sh faster video.mp4 large auto ./transcripts

# Batch process directory
./docker/transcribe_docker.sh batch ./input ./output medium true
```

#### Using Python Wrapper
```bash
# Basic usage
python docker/transcribe_docker.py audio.mp3

# With GPU acceleration
python docker/transcribe_docker.py video.mp4 --gpu --model large

# Batch processing
python docker/transcribe_docker.py ./input --batch --output-dir ./output
```

#### Using Docker Compose
```bash
# Standard Whisper
docker-compose --profile whisper run --rm whisper --model medium /data/input/audio.mp3

# Faster Whisper with GPU
docker-compose --profile gpu run --rm faster-whisper-gpu --model large /data/input/video.mp4
```

### API Transcription

#### OpenAI API
```bash
# Basic transcription
python api/transcribe_api.py audio.mp3

# With specific format and language
python api/transcribe_api.py video.mp4 --language en --response-format srt

# Translation to English
python api/transcribe_api.py foreign_audio.wav --task translate

# Batch processing
python api/transcribe_api.py ./input --batch --response-format verbose_json
```

#### Alternative APIs
```bash
# AssemblyAI with speaker labels
python api/alternative_apis.py audio.mp3 --service assemblyai --speaker-labels

# Rev AI with custom speaker names
python api/alternative_apis.py meeting.wav --service revai --speaker-names "Alice" "Bob" "Charlie"

# Speechmatics
python api/alternative_apis.py podcast.mp3 --service speechmatics --language en
```

## 🎛️ Model Comparison

| Model | Size | Speed | Accuracy | Best Use Case |
|-------|------|-------|----------|---------------|
| `tiny` | ~39 MB | ~32x realtime | Basic | Quick drafts, testing |
| `base` | ~74 MB | ~16x realtime | Good | General use, fast results |
| `small` | ~244 MB | ~6x realtime | Better | Balanced speed/quality |
| `medium` | ~769 MB | ~2x realtime | Great | **Recommended default** |
| `large` | ~1550 MB | ~1x realtime | Best | High accuracy needed |

## 🌍 Supported Languages

Whisper supports 99+ languages including:
- English (`en`) - Best supported
- Spanish (`es`)
- French (`fr`)
- German (`de`)
- Italian (`it`)
- Portuguese (`pt`)
- Russian (`ru`)
- Japanese (`ja`)
- Korean (`ko`)
- Chinese (`zh`)
- Arabic (`ar`)
- Hindi (`hi`)
- And many more...

Use `auto` or omit language parameter for automatic detection.

## 📄 Output Formats

All scripts generate multiple output formats:

- **`.txt`** - Plain text transcription
- **`.srt`** - SubRip subtitle format (with timestamps)
- **`.vtt`** - WebVTT subtitle format (web-compatible)
- **`.json`** - Structured data with metadata (API only)

## ⚡ Performance Tips

### Local Performance
- Use `medium` model for best balance of speed/accuracy
- Enable GPU acceleration if available: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
- Use SSD storage for model files and audio processing

### Docker Performance
- Use `faster-whisper` containers (2-4x faster than standard)
- Enable GPU support with `--gpu` flag
- Mount input/output directories for batch processing

### API Performance
- OpenAI API: Fastest processing, 25MB file limit
- Alternative APIs: Various limits and pricing models
- Consider file size limits and processing costs

## 🔧 Configuration

### Environment Variables
```bash
# API Keys
export OPENAI_API_KEY="your-openai-key"
export ASSEMBLYAI_API_KEY="your-assemblyai-key"
export REV_AI_API_KEY="your-rev-key"
export SPEECHMATICS_API_KEY="your-speechmatics-key"

# Local Whisper Model Cache
export WHISPER_CACHE_DIR="/path/to/model/cache"

# Docker Settings
export NVIDIA_VISIBLE_DEVICES=all  # For GPU Docker containers
```

### Batch Processing
Place audio files in the `input/` directory and run:

```bash
# Local batch
find input/ -name "*.mp3" -exec python local/transcribe_local.py {} \;

# Docker batch
./docker/transcribe_docker.sh batch ./input ./output medium true

# API batch
python api/transcribe_api.py ./input --batch
```

## 🐛 Troubleshooting

### Common Issues

#### Local Installation
```bash
# FFmpeg not found
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg          # macOS

# CUDA/GPU issues
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Memory errors with large files
# Use smaller model or split audio files
```

#### Docker Issues
```bash
# Docker not running
sudo systemctl start docker

# Permission errors
sudo usermod -aG docker $USER
# (then logout/login)

# GPU not detected
# Install nvidia-docker2 and restart Docker
```

#### API Issues
```bash
# File too large (>25MB for OpenAI)
# Compress audio or split into chunks

# Rate limiting
# Add delays between requests for batch processing

# Authentication errors
# Check API key is set correctly
echo $OPENAI_API_KEY
```

## 💰 Cost Comparison

| Method | Setup Cost | Processing Cost | Speed | Quality |
|--------|------------|-----------------|-------|---------|
| **Local** | Time to install | Free | Medium | Excellent |
| **Docker** | Time to setup | Free | Fast | Excellent |
| **OpenAI API** | None | ~$0.006/minute | Fastest | Excellent |
| **AssemblyAI** | None | ~$0.01/minute | Fast | Excellent |
| **Rev AI** | None | ~$0.02/minute | Medium | Good |

## 📈 Performance Benchmarks

Real-world testing on 16-core, 31GB RAM system with 33.3-second audio:

| Model | Processing Time | Realtime Factor | Quality | Memory | Best For |
|-------|----------------|-----------------|---------|--------|----------|
| `base` | 2.0s | **16.7x** | Good (361 chars) | <1GB | Development |
| `small` | 4.8s | **7.0x** | **Excellent (553 chars)** | 0.6GB | **Production** |
| `medium` | 11.1s | **3.0x** | High (492 chars) | <1GB | High-quality |
| `turbo` | 8.7s | **3.8x** | Good (358 chars) | <1GB | Optimized |

**Recommendation**: Use `small` model for best quality-to-speed balance.
*See [Model Selection Guide](docs/MODEL_SELECTION_GUIDE.md) for complete benchmark analysis.*

## 📋 API Documentation

**[📖 Function Behavior Contracts](FUNCTION_CONTRACTS.md)** - Complete interface specifications with exact return shapes and error conditions discovered through comprehensive testing.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests!

### Development Setup
```bash
git clone <this-repo>
cd whisper-project
make setup           # Professional setup with venv and dependencies
make test-fast       # Quick validation
make test-contracts  # Validate behavior contracts
make dev-check       # Complete quality check (lint + test + security)
```

## 📜 License

This project is open source. Please check individual component licenses:
- OpenAI Whisper: MIT License
- Docker images: Check respective repositories
- API services: Check terms of service

## 🙏 Acknowledgments

- OpenAI for the amazing Whisper model
- faster-whisper project for optimized inference
- Docker community for containerized solutions
- All the contributors to the transcription ecosystem

---

**Need help?** Create an issue or check the troubleshooting section above!

**Want the simplest solution?** Try the OpenAI API approach first - it's the fastest path to working transcription.
