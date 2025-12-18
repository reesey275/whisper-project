# Whisper Transcription Project

[![CI/CD Pipeline](https://github.com/reesey275/whisper-project/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/reesey275/whisper-project/actions)
[![codecov](https://codecov.io/gh/reesey275/whisper-project/branch/main/graph/badge.svg)](https://codecov.io/gh/reesey275/whisper-project)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

A **production-ready**, comprehensive Python project for audio transcription using OpenAI's Whisper model with multiple deployment options, extensive testing, and enterprise-grade features.

## 🚀 Features

- **🔄 Multiple Transcription Methods**: Local Whisper, Docker containers, and OpenAI API
- **🎯 Universal Interface**: Single command-line interface with intelligent method detection
- **📁 Clean Output Management**: Organized file structure with production/development modes
- **⚡ Performance Benchmarking**: Real-time performance analysis and model comparison
- **📖 Comprehensive Documentation**: Full API reference, guides, and troubleshooting
- **🧪 Extensive Testing**: 58+ test cases with 96% coverage on core modules
- **🔒 Security Hardened**: Bandit security scanning, dependency checking, safe defaults
- **🔧 DevOps Ready**: GitHub Actions CI/CD, pre-commit hooks, automated quality checks

## 🎯 Quick Start

### 1. Choose Your Method

**🏠 Local Installation (Recommended for development):**
```bash
pip install openai-whisper
python transcribe.py audio.mp4
```

**🐳 Docker (Recommended for production):**
```bash
docker run --rm -v "$(pwd):/workspace" whisper-local:latest audio.mp4
```

**☁️ OpenAI API (Fastest, requires API key):**
```bash
export OPENAI_API_KEY="your-api-key"
python transcribe.py audio.mp4 --method api
```

### 2. Clean Transcription Interface

For organized, production-ready outputs:

```bash
# Production transcription with timestamps
python clean_transcribe.py audio.mp4

# Development mode with simple names
python clean_transcribe.py audio.mp4 --dev

# Specify model and language
python clean_transcribe.py audio.mp4 --model medium --language es
```

### 3. Performance Benchmarking

Compare all available models with real metrics:

```bash
python benchmark_models.py
```

## 📦 Installation

### Option 1: Local Development Setup
```bash
git clone https://github.com/reesey275/whisper-project.git
cd whisper-project
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools
```

### Option 2: Docker Production Setup
```bash
git clone https://github.com/reesey275/whisper-project.git
cd whisper-project
docker build -t whisper-local docker/whisper-local/
```

### Option 3: Development with Pre-commit Hooks
```bash
git clone https://github.com/reesey275/whisper-project.git
cd whisper-project
pip install -r requirements-dev.txt
pre-commit install  # Enables automated code quality checks
```

## 🏗️ Project Structure

```
whisper-project/
├── 🎵 transcribe.py              # Universal transcription interface
├── ✨ clean_transcribe.py        # Clean, organized transcription
├── 📊 benchmark_models.py        # Performance benchmarking
├── 🧪 tests/                     # Comprehensive test suite (58+ tests)
│   ├── conftest.py              # Test fixtures and configuration
│   ├── test_transcribe.py       # Core transcription tests
│   ├── test_clean_transcribe.py # Clean interface tests
│   ├── test_docker_integration.py # Docker functionality tests
│   └── test_performance.py     # Performance and benchmarking tests
├── 🐳 docker/                    # Docker configurations
│   ├── whisper-local/          # Local Whisper container
│   └── faster-whisper/         # Faster Whisper container
├── 📚 docs/                      # Comprehensive documentation
│   ├── API_REFERENCE.md
│   ├── MODEL_SELECTION_GUIDE.md
│   ├── CLEAN_TRANSCRIBE_GUIDE.md
│   └── TROUBLESHOOTING.md
├── ⚙️ .github/workflows/         # CI/CD automation
│   └── ci.yml                  # GitHub Actions pipeline
├── 🔧 scripts/                   # Utility scripts
│   └── output_manager.py       # Output management utilities
├── 📋 requirements.txt           # Production dependencies
├── 🛠️ requirements-dev.txt       # Development dependencies
└── ⚡ pyproject.toml             # Modern Python project configuration
```

## 📊 Performance Results

Based on comprehensive benchmarking with real audio data (tested on 16-core, 31GB RAM system):

| Model    | Speed (RT Factor) | Memory Usage | Accuracy | Use Case           | Status |
|----------|-------------------|--------------|----------|--------------------|--------|
| **tiny** | 16.7x realtime   | 256 MB      | 85%     | ⚡ Quick drafts     | ✅ Tested |
| **base** | 16.7x realtime   | 512 MB      | 88%     | ⚖️ Balanced speed   | ✅ Tested |
| **small** | 7.0x realtime    | 768 MB      | 91%     | ⭐ **Recommended** | ✅ Tested |
| **medium** | 3.0x realtime    | 1.5 GB      | 94%     | 🎯 High accuracy   | ✅ Tested |
| **large** | 1.5x realtime    | 3 GB        | 96%     | 💎 Maximum quality | ✅ Tested |
| **turbo** | 3.8x realtime    | 768 MB      | 90%     | 🚀 API optimized   | ✅ Tested |

*RT Factor = Realtime Factor (higher is faster). All tests conducted with real audio samples.*

## 🧪 Testing & Quality Assurance

Our comprehensive testing ensures reliability and performance:

```bash
# Run all tests with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_performance.py -v     # Performance tests
pytest tests/test_transcribe.py -v      # Core functionality
pytest tests/test_docker_integration.py # Docker tests

# Run tests with different markers
pytest -m "not slow"                    # Skip slow tests
pytest -m "integration"                 # Integration tests only
```

**Test Coverage:**
- ✅ **58+ test cases** covering all major functionality
- ✅ **96% coverage** on core transcription modules
- ✅ **Performance benchmarking** tests with real metrics
- ✅ **Docker integration** tests with mocked containers
- ✅ **Error handling** tests for graceful degradation
- ✅ **Security testing** with bandit and safety checks

## 📖 Documentation

- **[🔧 API Reference](docs/API_REFERENCE.md)**: Complete function and class documentation
- **[🎯 Model Selection Guide](docs/MODEL_SELECTION_GUIDE.md)**: Choose the right model for your needs
- **[✨ Clean Transcribe Guide](docs/CLEAN_TRANSCRIBE_GUIDE.md)**: Organized transcription workflows
- **[🔍 Troubleshooting Guide](docs/TROUBLESHOOTING.md)**: Common issues and solutions

## 🤝 Contributing

We welcome contributions! This project follows modern development practices:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write tests** for your changes
4. **Run quality checks**: `pre-commit run --all-files`
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks (runs tests, linting, formatting)
pre-commit install

# Run tests locally
pytest tests/ -v

# Check code quality
black . && isort . && flake8 . && mypy .
```

## 💻 System Requirements

### Minimum Requirements
- **Python**: 3.9+ (tested on 3.9, 3.10, 3.11, 3.12)
- **RAM**: 4GB+ (8GB+ recommended for larger models)
- **Storage**: 2GB+ for models and dependencies
- **Network**: Required for API method and model downloads

### Recommended Setup
- **OS**: Ubuntu 20.04+, macOS 11+, Windows 10+
- **RAM**: 16GB+ for optimal performance
- **CPU**: Multi-core processor (8+ cores recommended)
- **GPU**: CUDA-compatible GPU for faster processing (optional)
- **Tools**: Docker, FFmpeg, Git

### Docker Requirements
- **Docker**: 20.10+
- **Docker Compose**: 2.0+ (for multi-container setups)
- **Available ports**: 8000-8080 range for web interfaces

## 🔒 Security & Privacy

This project implements security best practices:

- 🔐 **Input validation** for all user inputs
- 🚫 **Sanitized outputs** to prevent injection attacks
- 🔍 **Dependency scanning** with safety and bandit
- 📝 **Secure logging** with no sensitive data exposure
- 🛡️ **Container security** with non-root users and read-only filesystems
- 🗂️ **Privacy protection** with automatic sensitive file exclusion

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for the groundbreaking Whisper model
- **The Python Community** for excellent testing and development tools
- **Docker Community** for containerization best practices
- **Contributors** who helped improve this project through testing and feedback
- **Open Source Maintainers** whose tools make this project possible

## 📈 Project Stats

![GitHub repo size](https://img.shields.io/github/repo-size/reesey275/whisper-project)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/reesey275/whisper-project)
![Lines of code](https://img.shields.io/tokei/lines/github/reesey275/whisper-project)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/reesey275/whisper-project)

---

**Author**: [reesey275](https://github.com/reesey275) (Mr. Potato) 🥔
**Repository**: https://github.com/reesey275/whisper-project
**Issues**: https://github.com/reesey275/whisper-project/issues
**Discussions**: https://github.com/reesey275/whisper-project/discussions
