# Clean Transcription Interface Guide

The `clean_transcribe.py` is the **recommended interface** for most users. It provides organized outputs, clean file management, and simple usage patterns.

## 🎯 Overview

### Why Use Clean Transcribe?
- **Organized Outputs**: No more scattered files across random directories
- **Production Ready**: Timestamped files with proper naming conventions
- **Development Friendly**: Simple names for quick iteration and testing
- **Quality Preview**: Immediate content preview after transcription
- **File Management**: Built-in listing and organization features

### Output Structure
```
output/
├── production/          # Production transcriptions (timestamped)
│   ├── audio_small_20251003_143022.txt
│   ├── audio_small_20251003_143022.srt
│   └── audio_small_20251003_143022.vtt
├── development/         # Development transcriptions (simple names)
│   ├── audio_base.txt
│   ├── audio_base.srt
│   └── audio_base.vtt
├── archive/            # Archived transcriptions
└── temp/              # Temporary files (auto-cleanup)
```

## 📖 Usage Guide

### Basic Commands

#### Production Transcription
```bash
# Basic production transcription (recommended)
python clean_transcribe.py audio.mp4

# Specify model quality
python clean_transcribe.py audio.mp4 --model medium

# Different language
python clean_transcribe.py audio.mp4 --language es
```

**Output**: Creates timestamped files in `output/production/`
- Format: `filename_model_YYYYMMDD_HHMMSS.txt`
- Example: `interview_small_20251003_143022.txt`

#### Development Transcription
```bash
# Development mode (simple names)
python clean_transcribe.py audio.mp4 --dev

# Quick testing with base model
python clean_transcribe.py audio.mp4 --dev --model base

# Multiple dev iterations
python clean_transcribe.py test1.mp4 --dev --model tiny
python clean_transcribe.py test2.mp4 --dev --model tiny
```

**Output**: Creates simple files in `output/development/`
- Format: `filename_model.txt`
- Example: `interview_small.txt`
- Overwrites previous versions with same name

### File Management

#### List Transcriptions
```bash
# List production transcriptions
python clean_transcribe.py --list

# List development transcriptions
python clean_transcribe.py --list --dev
```

**Sample Output**:
```
📁 Production Transcriptions:
========================================
📄 interview_small_20251003_143022.txt
   Model: small | Size: 1,234 bytes | Modified: 2025-10-03 14:30
📄 meeting_medium_20251003_150815.txt  
   Model: medium | Size: 2,567 bytes | Modified: 2025-10-03 15:08
```

## 🎚️ Model Selection

### Quality vs Speed Trade-offs

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `tiny` | 39MB | **15.9x realtime** | Poor | **Avoid - poor quality** |
| `base` | 74MB | **16.7x realtime** | Good | **Development/previews** |
| `small` | 244MB | **7.0x realtime** | **Excellent** | **Recommended default** |
| `medium` | 769MB | **3.0x realtime** | Superior | **High-quality production** |
| `turbo` | ~150MB | **3.8x realtime** | Good | **Optimized processing** |
| `large-v3` | 1550MB | Variable* | High | **System dependent** |

*Performance varies significantly with system load

### Model Selection Examples

#### For Development/Testing
```bash
# Quick iteration - use tiny or base
python clean_transcribe.py test_audio.mp4 --dev --model base
```

#### For Production Quality
```bash
# Balanced quality (recommended)
python clean_transcribe.py important_call.mp4 --model small

# Maximum quality
python clean_transcribe.py legal_deposition.mp4 --model large
```

#### Context Quality Comparison
Based on real testing with the same 33.3-second audio clip:

**Tiny Model (Poor Quality - 180 chars)**:
```
Come on now. Let it flow. Oh, I'm just saying I've never ever heard that they 
It's fags. There's no no big of a guy trying to stick it. I hope not I'm gonna 
shut you plenty of time
```
*Broken sentences, missing context, poor accuracy*

**Small Model (Excellent Quality - 553 chars)**:
```
Come on now, let it flow, let it flow. Let it flow. Max. Let the heat flow with you. 
I swear, guys who never talk about how small their peepee is, unless they want to put 
it in your butt. I'm just saying. I'm just saying. I've never, ever heard that before, 
but, you know, I'm aware. It's facts. It's not that big of a fun. I've never had a guy 
try to stick it. I hope not...
```
*Complete sentences, natural flow, excellent accuracy and context preservation*

## 🌍 Language Support

### Default Language
The system defaults to English (`en`) for optimal performance:

```bash
# Uses English by default
python clean_transcribe.py audio.mp4

# Explicit English (same result)
python clean_transcribe.py audio.mp4 --language en
```

### Other Languages
```bash
# Spanish
python clean_transcribe.py audio.mp4 --language es

# French  
python clean_transcribe.py audio.mp4 --language fr

# German
python clean_transcribe.py audio.mp4 --language de

# Auto-detect (slower)
python clean_transcribe.py audio.mp4 --language auto
```

## 📋 Complete Command Reference

### Syntax
```bash
python clean_transcribe.py [audio_file] [options]
python clean_transcribe.py [--list] [--dev]
```

### Parameters

#### File Processing
| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `audio_file` | Audio/video file to transcribe | Required | `audio.mp4` |
| `--model`, `-m` | Whisper model size | `small` | `--model medium` |
| `--language`, `-l` | Language code | `en` | `--language es` |
| `--dev` | Development mode (simple names) | Production | `--dev` |

#### File Management
| Parameter | Description | Example |
|-----------|-------------|---------|
| `--list` | List transcriptions | `--list` |
| `--list --dev` | List development transcriptions | `--list --dev` |

### Exit Codes
- `0`: Success
- `1`: Transcription failed
- `2`: Invalid arguments

## 🔄 Workflow Examples

### Development Workflow
```bash
# 1. Quick test with tiny model
python clean_transcribe.py sample.mp4 --dev --model tiny

# 2. Review results
python clean_transcribe.py --list --dev

# 3. Try better quality
python clean_transcribe.py sample.mp4 --dev --model small

# 4. Final production version
python clean_transcribe.py sample.mp4 --model small
```

### Production Workflow
```bash
# 1. Process important files with quality model
python clean_transcribe.py meeting_2025_Q1.mp4 --model medium

# 2. Batch process multiple files
for file in input/*.mp4; do
    python clean_transcribe.py "$file" --model small
done

# 3. Review all transcriptions
python clean_transcribe.py --list

# 4. Archive older files
mv output/production/old_* output/archive/
```

### Quality Assurance Workflow
```bash
# 1. Test with multiple models for comparison
python clean_transcribe.py test.mp4 --dev --model base
python clean_transcribe.py test.mp4 --dev --model small  
python clean_transcribe.py test.mp4 --dev --model medium

# 2. Compare outputs
ls -la output/development/test_*

# 3. Choose best model for production
python clean_transcribe.py final.mp4 --model medium
```

## 🛠️ Advanced Features

### Integration with Other Scripts
```bash
# Use with universal interface
python transcribe.py audio.mp4 --output-dir output/production

# Process through Docker stack
docker-compose exec whisper-core python clean_transcribe.py /app/input/audio.mp4
```

### Custom Output Processing
```python
# Python integration
from clean_transcribe import CleanTranscriber

transcriber = CleanTranscriber()
result = transcriber.transcribe(
    audio_file="audio.mp4",
    model="small",
    language="en",
    mode="production"
)

if result['success']:
    print(f"Files created: {result['files']}")
    print(f"Output directory: {result['output_dir']}")
```

## 🔧 Troubleshooting

### Common Issues

#### "Command not found"
```bash
# Ensure virtual environment is activated
source whisper-env/bin/activate
```

#### "Permission denied"
```bash
# Make script executable
chmod +x clean_transcribe.py
```

#### Poor quality results
```bash
# Use better model
python clean_transcribe.py audio.mp4 --model medium

# Specify correct language
python clean_transcribe.py audio.mp4 --language en
```

#### Files not found
```bash
# Check output structure
ls -la output/*/

# List transcriptions
python clean_transcribe.py --list
python clean_transcribe.py --list --dev
```

### Performance Tips

1. **Model Selection**: Use `small` for best balance of quality and speed
2. **Development Mode**: Use `--dev` for quick iteration
3. **Language Specification**: Always specify language for best performance
4. **Batch Processing**: Process multiple files in sequence rather than parallel

## 📊 Performance Benchmarks

Based on real testing with a 33.3-second audio clip on 16-core, 31GB RAM system:

| Model | Processing Time | Realtime Factor | Output Quality | Model Size |
|-------|----------------|-----------------|----------------|-----------|
| `tiny` | 2.1 seconds | **15.9x** | Poor (180 chars) | 39MB |
| `base` | 2.0 seconds | **16.7x** | Good (361 chars) | 74MB |
| `small` | 4.8 seconds | **7.0x** | **Excellent (553 chars)** | 244MB |
| `medium` | 11.1 seconds | **3.0x** | High (492 chars) | 769MB |
| `turbo` | 8.7 seconds | **3.8x** | Good (358 chars) | ~150MB |
| `large-v3` | 144.2 seconds* | 0.2x* | Variable (304 chars) | 1550MB |

*Large-v3 performance impacted by concurrent system load

**Recommendation**: Use `small` model for the best quality-to-speed ratio (7.0x realtime, 553 characters).

---

**Next**: See [API_REFERENCE.md](API_REFERENCE.md) for programmatic usage and [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed problem solving.