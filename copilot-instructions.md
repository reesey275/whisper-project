# Copilot Instructions for Whisper Project

## Context
You are working on a comprehensive Whisper transcription system that supports local processing, Docker containers, and cloud APIs. This system is designed for both developers and end-users who need reliable audio transcription capabilities.

## Core Architecture
- **Universal Interface**: `transcribe.py` - auto-detects best available method
- **Local Processing**: Direct OpenAI Whisper installation with multiple model sizes
- **Docker Support**: Custom containers for isolated, consistent processing
- **Cloud APIs**: OpenAI, AssemblyAI, Rev AI, and Speechmatics integration
- **Multiple Output Formats**: TXT, SRT, VTT subtitles with timestamps

## Directory Structure - STRICTLY ENFORCE
```
whisper-project/
├── transcribe.py              # Main entry point - universal interface
├── local/transcribe_local.py  # Local Whisper implementation
├── docker/                    # Docker solutions (scripts + containers)
├── api/                       # Cloud API clients
├── input/                     # User audio files
├── output/                    # ALL generated content goes here
│   ├── transcriptions/        # Regular user outputs
│   ├── test_results/          # Development testing results
│   └── batch_processing/      # Batch job outputs
├── test_audio/               # Development test files (source only)
└── whisper-env/              # Python virtual environment
```

## Critical Rules - Never Violate

### 1. Output Directory Management
**NEVER create output subdirectories inside source directories**
- ✅ ALWAYS use `output/` for generated content
- ✅ Organize with clear subdirectories: `output/transcriptions/`, `output/test_results/`
- ❌ NEVER create: `test_audio/results/`, `input/outputs/`, `local/transcriptions/`
- ❌ NEVER create temporary output dirs like: `test_audio/base_output/`

### 2. File Organization
- Keep source files (audio, code) separate from generated content
- Use consistent naming: model names, timestamps, clear purposes
- Clean up temporary files after consolidating results
- Document test setups and comparison results

### 3. User Experience Priority
- Maintain simple, clear interfaces for end users
- Provide helpful error messages with actionable solutions
- Include usage examples in all documentation
- Test commands work as documented

## Development Workflow

### Before Making Changes
1. Understand current structure: `tree -L 2` or `ls -la`
2. Check existing documentation (README.md, AGENTS.md)
3. Plan where new files will go
4. Consider impact on user experience

### During Development
1. Use the established directory structure
2. Follow naming conventions: `transcribe_*.py` for main scripts
3. Include proper error handling and user feedback
4. Test both success and failure scenarios

### After Development
1. Clean up temporary files and directories
2. Update relevant documentation (README.md, docstrings)
3. Test the universal interface still works
4. Verify all three methods (local, Docker, API) function

## Code Standards

### Python Files
- Include comprehensive docstrings with usage examples
- Use type hints where appropriate
- Handle errors gracefully with user-friendly messages
- Follow the established pattern: class-based or function-based consistently

### Shell Scripts
- Include usage examples in comments
- Check for required dependencies
- Provide clear error messages
- Use absolute paths to avoid confusion

### Docker Files
- Keep images efficient and minimal
- Document the purpose and usage
- Use consistent tagging: `whisper-local:latest`, `faster-whisper:latest`
- Include health checks where appropriate

## Testing Guidelines

### Test Organization
- Source audio files: `test_audio/`
- Test results: `output/test_results/`
- Include comparison summaries between methods/models
- Document test conditions: audio quality, duration, content type

### Model Comparison Standards
When testing different models:
- Use consistent test audio across all models
- Document: processing time, accuracy, resource usage
- Organize results clearly: `tiny_model/`, `base_model/`, `small_model/`
- Include summary with recommendations

## Common Patterns

### Error Handling
```python
try:
    result = transcribe_audio(file_path)
    print("✅ Transcription completed successfully!")
except FileNotFoundError:
    print("❌ Audio file not found. Please check the file path.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Transcription failed: {e}")
    sys.exit(1)
```

### User Feedback
- Use emoji prefixes: ✅ success, ❌ error, ⚠️ warning, 🎵 processing
- Include progress indicators for long operations
- Show file paths for generated outputs
- Provide next steps or usage examples

### Configuration Management
- Use `.env` files for API keys (with `.env.template`)
- Support command-line arguments with sensible defaults
- Include validation for required dependencies
- Graceful fallbacks when optional features unavailable

## Performance Considerations

### Model Selection Guidance
- **tiny**: Real-time, drafts, testing (fastest, least accurate)
- **base**: General purpose (balanced speed/accuracy)
- **small**: Important transcriptions (higher accuracy)
- **medium/large**: Critical accuracy needs (slower, most accurate)

### Resource Management
- Monitor disk usage (models and audio files are large)
- Clean up temporary Docker containers and images
- Provide disk space warnings for large batch jobs
- Use streaming for very large audio files when possible

## User Support

### Documentation Requirements
- Clear installation instructions for all platforms
- Working examples for common use cases
- Troubleshooting section with common issues
- Performance expectations and hardware requirements

### Help Text Standards
```bash
# Good help text includes:
- Brief description of what the tool does
- Usage examples with real file names
- Available options with explanations
- Links to more detailed documentation
```

## Maintenance Tasks

### Regular Checks
- Verify all dependency versions are compatible
- Test Docker images build successfully
- Confirm API endpoints and authentication work
- Check for security updates in dependencies

### Documentation Updates
- Keep README.md current with new features
- Update API key setup instructions
- Refresh performance benchmarks
- Add new troubleshooting scenarios

## Remember
- **Consistency over cleverness** - follow established patterns
- **User experience first** - make it work reliably for end users
- **Clean up after yourself** - no temporary directories left behind
- **Document your reasoning** - help future developers understand decisions

When in doubt, refer to AGENTS.md for detailed development guidelines.
