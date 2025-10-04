# Contributing to Whisper Transcription Project

Thank you for your interest in contributing to the Whisper Transcription Project! This document provides guidelines and information for contributors.

## 🚀 Quick Start for Contributors

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/whisper-project.git
   cd whisper-project
   ```
3. **Set up development environment**:
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install
   ```

## 🎯 Ways to Contribute

### 🐛 Bug Reports
- Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include system information (OS, Python version, etc.)
- Provide minimal reproduction steps
- Include relevant logs and error messages

### ✨ Feature Requests
- Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Describe the problem you're trying to solve
- Explain why this feature would be beneficial
- Consider implementation complexity

### 📝 Documentation Improvements
- Fix typos, grammar, or unclear explanations
- Add examples or use cases
- Improve API documentation
- Translate documentation (if applicable)

### 🔧 Code Contributions
- Bug fixes
- Performance improvements
- New transcription methods
- Additional output formats
- Enhanced error handling

## 🛠️ Development Setup

### Prerequisites
- Python 3.9+ (we test on 3.9, 3.10, 3.11, 3.12)
- Git
- FFmpeg (for audio processing)
- Docker (optional, for container testing)

### Environment Setup

1. **Create virtual environment**:
   ```bash
   python -m venv whisper-env
   source whisper-env/bin/activate  # Linux/Mac
   # whisper-env\Scripts\activate     # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Verify setup**:
   ```bash
   pytest tests/ --tb=short
   ```

## 📋 Development Workflow

### 1. Creating a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
# or
git checkout -b docs/improvement-description
```

### 2. Making Changes

#### Code Style
We use automated formatting and linting:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run quality checks:
```bash
# Format code
black .
isort .

# Check linting
flake8 .

# Type checking
mypy . --ignore-missing-imports

# Or run all pre-commit hooks
pre-commit run --all-files
```

#### Writing Tests
All new features and bug fixes should include tests:

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test files
pytest tests/test_transcribe.py -v

# Run tests with markers
pytest -m "not slow"  # Skip slow tests
pytest -m "integration"  # Run only integration tests
```

#### Test Categories
- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **Performance tests**: Benchmark and performance validation
- **Docker tests**: Container functionality

### 3. Commit Guidelines

#### Commit Message Format
```
type(scope): brief description

Longer description explaining the change, why it was made,
and any important details.

Fixes #123
```

#### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

#### Examples
```bash
git commit -m "feat(transcribe): add support for WebM audio format"
git commit -m "fix(docker): resolve container permission issues"
git commit -m "docs(api): improve function documentation with examples"
git commit -m "test(performance): add memory usage benchmarks"
```

### 4. Running Tests Locally

Before pushing your changes:

```bash
# Run the full test suite
pytest tests/ --cov=. --cov-report=term-missing

# Check code quality
pre-commit run --all-files

# Build documentation (if applicable)
cd docs && make html
```

## 🧪 Testing Guidelines

### Writing Good Tests

1. **Test file naming**: `test_*.py`
2. **Test function naming**: `test_descriptive_name()`
3. **Use fixtures**: Defined in `tests/conftest.py`
4. **Mock external dependencies**: Use `unittest.mock` or `pytest-mock`
5. **Test edge cases**: Empty inputs, large files, network failures

### Test Structure
```python
def test_feature_with_valid_input(sample_audio_file, temp_dir):
    """Test that feature works correctly with valid input."""
    # Arrange
    expected_output = "expected result"

    # Act
    result = feature_function(sample_audio_file)

    # Assert
    assert result == expected_output
    assert os.path.exists(result_file)
```

### Test Markers
```python
import pytest

@pytest.mark.slow
def test_large_file_processing():
    """Mark tests that take significant time."""
    pass

@pytest.mark.integration
def test_docker_transcription():
    """Mark integration tests."""
    pass

@pytest.mark.api
def test_openai_api_call():
    """Mark tests requiring API access."""
    pass
```

## 📚 Documentation Guidelines

### Code Documentation

#### Docstrings
Use Google-style docstrings:

```python
def transcribe_audio(audio_path: str, model: str = "base") -> dict:
    """Transcribe audio file using specified model.

    Args:
        audio_path: Path to the audio file to transcribe.
        model: Whisper model to use ('tiny', 'base', 'small', etc.).

    Returns:
        Dictionary containing transcription results with keys:
        - 'text': Full transcription text
        - 'segments': List of segment dictionaries
        - 'language': Detected language code

    Raises:
        FileNotFoundError: If audio file doesn't exist.
        ValueError: If model name is invalid.

    Example:
        >>> result = transcribe_audio("audio.mp3", "small")
        >>> print(result['text'])
        "Hello, this is a test transcription."
    """
```

#### Type Hints
Use type hints for all function parameters and return values:

```python
from typing import Dict, List, Optional, Union
from pathlib import Path

def process_files(
    file_paths: List[Union[str, Path]],
    output_dir: Optional[str] = None
) -> Dict[str, str]:
    """Type hints improve code clarity and enable better tooling."""
    pass
```

### Documentation Files

#### Markdown Structure
```markdown
# Title

Brief description of the content.

## Section Header

Content with examples:

```bash
# Code examples with proper syntax highlighting
python script.py --option value
```

### Subsection

- Use bullet points for lists
- Include **bold** for emphasis
- Add `inline code` for commands/variables

## See Also

- [Related Documentation](link)
- [External Resources](link)
```

## 🔍 Code Review Process

### Before Submitting PR

1. **Self-review your changes**
2. **Run full test suite**
3. **Update documentation** if needed
4. **Add changelog entry** for significant changes
5. **Rebase** on latest main branch

### Pull Request Guidelines

#### PR Title Format
```
[type] Brief description of changes

Examples:
[feat] Add WebM audio format support
[fix] Resolve Docker permission issues
[docs] Improve API reference with examples
```

#### PR Description Template
```markdown
## Changes Made
- Brief bullet point list of changes
- Include motivation for changes

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Documentation
- [ ] Updated relevant documentation
- [ ] Added docstrings for new functions
- [ ] Updated API reference if needed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] No breaking changes (or documented)
```

### Review Criteria

Reviewers will check for:
- **Functionality**: Does the code work as intended?
- **Testing**: Are there adequate tests?
- **Performance**: Any performance implications?
- **Security**: No security vulnerabilities introduced?
- **Documentation**: Is documentation updated?
- **Style**: Follows project conventions?

## 🐳 Docker Development

### Building Images Locally
```bash
# Build whisper-local image
docker build -t whisper-local:dev docker/whisper-local/

# Build faster-whisper image
docker build -t faster-whisper:dev docker/faster-whisper/

# Test images
docker run --rm whisper-local:dev --help
```

### Testing Docker Integration
```bash
# Run Docker-specific tests
pytest tests/test_docker_integration.py -v

# Test with actual containers
docker run --rm -v "$(pwd)/tests/data:/input" \
  whisper-local:dev /input/sample.wav
```

## 🚨 Troubleshooting Development Issues

### Common Issues

#### Pre-commit Hook Failures
```bash
# Fix formatting issues
black .
isort .

# Commit again
git commit -m "Your commit message"
```

#### Test Failures
```bash
# Run specific failing test
pytest tests/test_specific.py::test_function -v

# Run with debugging
pytest tests/test_specific.py::test_function -v -s --tb=long

# Skip slow tests during development
pytest tests/ -m "not slow"
```

#### Import Errors
```bash
# Ensure you're in virtual environment
source whisper-env/bin/activate

# Reinstall dependencies
pip install -r requirements-dev.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Docker Issues
```bash
# Clean Docker environment
docker system prune -f

# Rebuild images
docker build --no-cache -t whisper-local:dev docker/whisper-local/

# Check logs
docker logs container_name
```

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Request Comments**: Code-specific discussions

### Mentorship
New contributors are welcome! If you're new to:
- **Python development**: Start with documentation improvements
- **Testing**: Look for issues labeled `good-first-issue`
- **Docker**: Check out container-related tasks
- **Open source**: We're happy to guide you through the process

## 🏆 Recognition

Contributors are recognized in:
- Repository contributors page
- Release notes for significant contributions
- Project documentation acknowledgments

## 📝 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

**Questions?** Feel free to ask in [GitHub Discussions](https://github.com/reesey275/whisper-project/discussions) or open an issue!
