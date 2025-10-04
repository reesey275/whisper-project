# AI Agents Development Guidelines

This document provides guidelines for AI agents working on this Whisper transcription project to maintain consistency, organization, and best practices.

## 🎯 Project Overview

This is a comprehensive Whisper transcription system supporting:
- **Local Whisper** (OpenAI's implementation)
- **Docker containers** (isolated environments)  
- **Cloud APIs** (OpenAI, AssemblyAI, Rev AI, Speechmatics)
- **Universal interface** (auto-detection of best method)

## 📁 Directory Structure - DO NOT VIOLATE

```
whisper-project/
├── transcribe.py              # Universal interface (main entry point)
├── requirements.txt           # Python dependencies
├── README.md                  # User documentation
├── .env                       # API keys (gitignored)
├── .env.template             # Template for API keys
├── setup.sh                  # Automated setup script
├── test_setup.py             # System verification
├── demo.py                   # Interactive demonstration
├── 
├── local/                    # Local Whisper implementation
│   └── transcribe_local.py
├── docker/                   # Docker-based solutions
│   ├── transcribe_docker.py
│   ├── transcribe_docker.sh  
│   ├── docker-compose.yml
│   ├── Dockerfile.whisper
│   └── Dockerfile.faster-whisper
├── api/                      # Cloud API clients
│   ├── transcribe_api.py
│   └── alternative_apis.py
├── 
├── input/                    # ✅ Input audio files go here
├── output/                   # ✅ ALL outputs go here (organized by purpose)
│   ├── transcriptions/       # Regular transcription outputs
│   ├── test_results/         # Test and comparison results
│   └── batch_processing/     # Batch job results
├── 
├── test_audio/              # Test files for development
│   └── *.wav, *.mp3, etc.   # Keep ONLY source audio files
└── whisper-env/             # Python virtual environment
```

## 🚨 Critical Rules - NEVER BREAK THESE

### 1. Output Directory Management
- **NEVER** create output subdirectories inside `input/`, `test_audio/`, or other source directories
- **ALWAYS** use the root-level `output/` directory for ALL generated content
- **ORGANIZE** output with clear subdirectories: `output/transcriptions/`, `output/test_results/`, etc.
- **NO EXCEPTIONS** - this prevents directory structure chaos

### 2. File Organization Principles
```bash
# ✅ CORRECT - All outputs in output/
output/
├── transcriptions/user_audio.txt
├── test_results/model_comparison/
└── batch_processing/job_001/

# ❌ WRONG - Creates duplicate and confusing structure  
test_audio/
├── results/           # NO! Don't create outputs here
├── base_output/       # NO! Don't create outputs here
└── transcriptions/    # NO! Don't create outputs here
```

### 3. Testing and Comparison Protocols
When testing multiple models/methods:
- Create **one organized comparison** in `output/test_results/`
- Use **clear naming**: `tiny_model/`, `base_model/`, `small_model/`, etc.
- Include **summary documentation** explaining the test setup and results
- **Clean up temporary files** after consolidating results

### 4. Project Structure Integrity
- **DO NOT** modify the core directory structure without documentation
- **DO NOT** create duplicate functionality across directories
- **MAINTAIN** separation of concerns: local/, docker/, api/
- **PRESERVE** the universal interface as the main entry point

## 🔧 Development Workflow

### Before Making Changes
1. **Read existing documentation** (README.md, this file)
2. **Understand the current structure** with `tree` or `ls -la`
3. **Plan your approach** - where will files go?
4. **Consider the user experience** - will this be confusing?

### During Development
1. **Use consistent naming conventions**
2. **Create logical groupings** of related files
3. **Document your changes** as you go
4. **Test in isolation** before integrating

### After Development  
1. **Clean up temporary files and directories**
2. **Consolidate results** into proper locations
3. **Update documentation** to reflect changes
4. **Verify the project still works** end-to-end

## 📝 Documentation Standards

### Code Comments
- Explain **WHY** not just what
- Include **usage examples** in docstrings
- Note **dependencies** and requirements
- Document **error handling** approaches

### File Headers
Every Python file should have:
```python
#!/usr/bin/env python3
"""
Brief description of the file's purpose

This module provides [specific functionality] for the Whisper transcription
project. It [key features and use cases].

Usage:
    python script.py input.wav --model medium
    
Dependencies:
    - whisper (for local transcription)
    - docker (for containerized processing)
"""
```

### Directory README Files
Each major directory should have a README.md explaining:
- **Purpose** of the directory
- **Key files** and their functions
- **Usage examples**
- **Dependencies** or setup requirements

## 🧪 Testing Guidelines

### Test Organization
- Keep **test files** in `test_audio/`
- Put **test results** in `output/test_results/`
- Include **comparison summaries** for different approaches
- **Clean up** intermediate test outputs

### Test Documentation
- **Document test setup**: audio source, models tested, environment
- **Include quantitative results**: processing time, accuracy metrics
- **Provide qualitative analysis**: when to use each approach
- **Maintain test history**: don't lose valuable comparison data

## 🚀 Performance Considerations

### Model Selection Guidance
- **tiny**: Fast drafts, testing, real-time applications
- **base**: General purpose, balanced speed/accuracy
- **small**: High accuracy needs, important transcriptions
- **medium/large**: Critical accuracy, batch processing

### Resource Management
- **Monitor disk usage** - audio files and models are large
- **Clean up temporary files** - Docker layers, model caches
- **Use appropriate output formats** - TXT for simple, SRT/VTT for timestamps

## 🔍 Troubleshooting Approach

### When Things Go Wrong
1. **Check the directory structure** - are files where they should be?
2. **Verify dependencies** - Python packages, Docker images, system libraries
3. **Test components individually** - local, Docker, API separately
4. **Check permissions** - file system, Docker daemon, API keys
5. **Review logs** - enable verbose output for debugging

### Common Issues
- **Permission denied**: Check Docker daemon, file ownership
- **Import errors**: Verify virtual environment activation, package installation
- **Audio format issues**: Ensure FFmpeg is installed and working
- **API failures**: Check network connectivity, API key validity

## 📚 Learning Resources

### Understanding Whisper
- [OpenAI Whisper GitHub](https://github.com/openai/whisper)
- [Whisper Model Cards](https://github.com/openai/whisper/blob/main/model-card.md)
- [Audio preprocessing best practices](https://platform.openai.com/docs/guides/speech-to-text)

### Docker Best Practices
- [Docker official documentation](https://docs.docker.com/)
- [Container optimization techniques](https://docs.docker.com/develop/dev-best-practices/)

---

## 🎯 Remember: Consistency Over Cleverness

The goal is to create a **maintainable, understandable, and reliable** system. When in doubt:
- **Follow established patterns** rather than inventing new ones
- **Ask "Will this confuse a user?"** before implementing
- **Document your reasoning** for future reference
- **Clean up after yourself** - leave it better than you found it

*This document is living and should be updated as the project evolves.*