# Troubleshooting Guide

Comprehensive solutions for common issues, debugging steps, and system optimization.

## 📋 Quick Problem Solver

### Most Common Issues

| Problem | Quick Solution | Full Section |
|---------|---------------|--------------|
| 🚫 "Command not found" | `source whisper-env/bin/activate` | [Environment Issues](#-environment-issues) |
| 🐌 Very slow transcription | Use `--model small` instead of tiny | [Performance Issues](#-performance-issues) |  
| 📄 Poor quality output | Use `--model medium --language en` | [Quality Issues](#-quality-issues) |
| 🐳 Docker container fails | `docker-compose up --build` | [Docker Issues](#-docker-issues) |
| 💾 "Out of memory" error | Use smaller model or reduce batch size | [Memory Issues](#-memory-issues) |
| 🔑 API key errors | `export OPENAI_API_KEY="your-key"` | [API Issues](#-api-issues) |

## 🔧 Environment Issues

### Virtual Environment Problems

#### Problem: "Command not found" or "Module not found"
```bash
# Error examples:
bash: transcribe.py: command not found
ModuleNotFoundError: No module named 'whisper'
```

**Solution: Activate Virtual Environment**
```bash
# Navigate to project directory
cd /home/chad/whisper-project

# Activate virtual environment
source whisper-env/bin/activate

# Verify activation (should show whisper-env in prompt)
which python
# Should output: /home/chad/whisper-project/whisper-env/bin/python
```

**Permanent Solution: Add to .bashrc**
```bash
# Add to ~/.bashrc for automatic activation
echo "alias whisper-activate='cd /home/chad/whisper-project && source whisper-env/bin/activate'" >> ~/.bashrc
source ~/.bashrc

# Now you can use: whisper-activate
```

#### Problem: Virtual Environment Corrupted
```bash
# Symptoms:
pip: command not found
python: can't open file '/path/to/python': [Errno 2] No such file or directory
```

**Solution: Recreate Environment**
```bash
# Remove corrupted environment
rm -rf whisper-env

# Create new environment
python3 -m venv whisper-env
source whisper-env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Python Version Issues

#### Problem: Wrong Python Version
```bash
# Check current version
python --version
# If shows Python 2.x or older Python 3.x
```

**Solution: Use Correct Python**
```bash
# Ubuntu/Debian: Install Python 3.8+
sudo apt update
sudo apt install python3.8 python3.8-venv python3.8-dev

# Create environment with specific version
python3.8 -m venv whisper-env
source whisper-env/bin/activate
```

### Package Installation Issues

#### Problem: "Failed building wheel" or compilation errors
```bash
# Common error pattern:
ERROR: Failed building wheel for torch
Building wheel for whisper (setup.py) ... error
```

**Solution: Install System Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y \
    python3-dev \
    build-essential \
    ffmpeg \
    libffi-dev \
    libssl-dev \
    rustc

# Then reinstall packages
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### Problem: FFmpeg not found
```bash
# Error:
RuntimeError: FFmpeg not found
```

**Solution: Install FFmpeg**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Verify installation
ffmpeg -version

# Alternative: Snap installation
sudo snap install ffmpeg
```

## 🐌 Performance Issues

### Slow Transcription Speed

#### Problem: Transcription takes too long
**Root Cause Analysis:**
```bash
# Check system resources
htop          # CPU usage
free -h       # Memory usage
nvidia-smi    # GPU usage (if available)
```

**Solutions by Model Size:**

| Current Model | Issue | Recommended Solution |
|---------------|-------|---------------------|
| `tiny` | Poor quality | Upgrade to `small` |
| `base` | Still slow | Use `small` (sweet spot) |
| `medium` | Very slow | Use `small` for most content |
| `large` | Extremely slow | Reserve for critical accuracy needs |

```bash
# Quick fix: Use optimal model
python transcribe.py audio.mp4 --model small --language en

# For batch processing: Use base model
for file in *.mp4; do
    python transcribe.py "$file" --model base --language en
done
```

#### Problem: CPU bottleneck
```bash
# Check CPU usage during transcription
python transcribe.py audio.mp4 --model small &
PID=$!
while kill -0 $PID 2>/dev/null; do
    ps -p $PID -o %cpu,%mem,cmd
    sleep 5
done
```

**Solutions:**
1. **Use Docker with resource limits:**
   ```bash
   # Limit container resources
   docker run --cpus="2.0" --memory="4g" whisper-local:latest transcribe.py audio.mp4
   ```

2. **Process smaller chunks:**
   ```bash
   # Split large files
   ffmpeg -i large_audio.mp4 -f segment -segment_time 600 -c copy chunk_%03d.mp4
   ```

### GPU Acceleration Issues

#### Problem: GPU not being used
```bash
# Check if GPU is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

**Solution: Enable GPU support**
```bash
# Install CUDA-enabled PyTorch
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Use GPU Docker image
docker run --gpus all whisper-gpu:latest transcribe.py audio.mp4
```

#### Problem: Out of GPU memory
```bash
# Error:
RuntimeError: CUDA out of memory
```

**Solutions:**
```bash
# Use smaller model
python transcribe.py audio.mp4 --model small

# Clear GPU cache
python -c "import torch; torch.cuda.empty_cache()"

# Use CPU instead
CUDA_VISIBLE_DEVICES="" python transcribe.py audio.mp4
```

## 📉 Quality Issues

### Poor Transcription Accuracy

#### Problem: Transcription contains many errors
**Diagnostic Steps:**
```bash
# Test with different models
python transcribe.py sample.mp4 --model tiny > tiny_output.txt
python transcribe.py sample.mp4 --model small > small_output.txt
python transcribe.py sample.mp4 --model medium > medium_output.txt

# Compare results
diff tiny_output.txt small_output.txt
```

**Model Quality Comparison (same 32-second audio):**

| Model | Output Sample | Quality Rating |
|-------|---------------|----------------|
| `tiny` | "Come on now. Let it flow. Oh, I'm just saying I've never ever heard that they It's fags." | ❌ Poor (181 chars) |
| `small` | "Come on now, let it flow, let it flow, let it flow. Max, let the heat flow with you. I swear, guys don't ever talk about how small their peepee is unless they want to put it in your butt." | ✅ Excellent (496 chars) |

**Solutions:**
1. **Use appropriate model size:**
   ```bash
   # For production quality
   python transcribe.py audio.mp4 --model small
   
   # For maximum accuracy
   python transcribe.py audio.mp4 --model medium
   ```

2. **Specify correct language:**
   ```bash
   # Better than auto-detection
   python transcribe.py audio.mp4 --language en
   
   # For non-English content
   python transcribe.py spanish_audio.mp4 --language es
   ```

#### Problem: Missing words or broken sentences
**Root Causes:**
- Audio quality issues
- Background noise
- Multiple speakers
- Technical jargon

**Solutions:**
```bash
# Pre-process audio for better quality
ffmpeg -i noisy_audio.mp4 -af "highpass=f=200,lowpass=f=3000" cleaned_audio.mp4
python transcribe.py cleaned_audio.mp4 --model medium

# Use larger model for complex audio
python transcribe.py conference_call.mp4 --model large --language en
```

### Language Detection Issues

#### Problem: Wrong language detected
```bash
# Symptoms:
# - Gibberish output
# - Mixed language transcription
# - "Unable to detect language" error
```

**Solutions:**
```bash
# Always specify language when known
python transcribe.py audio.mp4 --language en

# For multilingual content, use auto-detection with larger model
python transcribe.py multilingual.mp4 --language auto --model medium

# Check supported languages
python -c "import whisper; print(whisper.available_languages())"
```

## 🐳 Docker Issues

### Container Startup Problems

#### Problem: "Docker not found" or "Permission denied"
```bash
# Check Docker installation
docker --version
systemctl status docker
```

**Solutions:**
```bash
# Install Docker (Ubuntu)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

#### Problem: "No such image" error
```bash
# Error:
docker: Error response from daemon: pull access denied for whisper-local
```

**Solution: Build images**
```bash
# Build all required images
docker-compose build

# Or build individually
docker build -t whisper-local:latest -f docker/Dockerfile.whisper .
docker build -t faster-whisper:latest -f docker/Dockerfile.faster-whisper .

# Verify images
docker images | grep whisper
```

### Docker Compose Issues

#### Problem: Services fail to start
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs whisper-core
docker-compose logs faster-whisper-service
```

**Common Solutions:**
```bash
# Rebuild services
docker-compose down
docker-compose up --build

# Reset volumes
docker-compose down -v
docker-compose up

# Check port conflicts
netstat -tulpn | grep :8000
```

#### Problem: Volume mounting issues
```bash
# Error:
bind: permission denied
```

**Solution: Fix permissions**
```bash
# Make sure directories exist and are writable
mkdir -p input output logs
chmod 755 input output logs

# Or use absolute paths in docker-compose.yml
volumes:
  - "/absolute/path/to/input:/app/input"
  - "/absolute/path/to/output:/app/output"
```

### Container Performance Issues

#### Problem: Slow Docker transcription
**Diagnostic:**
```bash
# Check container resources
docker stats whisper-core

# Check container logs for bottlenecks
docker-compose logs -f whisper-core
```

**Solutions:**
```bash
# Increase container resources
docker-compose -f docker-compose.yml -f docker-compose.override.yml up

# Use GPU acceleration (if available)
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up

# Optimize Docker settings
echo '{"max-concurrent-downloads": 1, "max-concurrent-uploads": 1}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker
```

## 💾 Memory Issues

### Out of Memory Errors

#### Problem: "MemoryError" or system freeze during transcription
```bash
# Monitor memory usage
free -h
watch -n 1 'free -h && ps aux --sort=-%mem | head -10'
```

**Solutions by File Size:**

| Audio Length | Recommended Model | Memory Usage | Command |
|--------------|------------------|--------------|---------|
| < 10 minutes | `small` | ~2GB | `python transcribe.py audio.mp4 --model small` |
| 10-30 minutes | `base` | ~1GB | `python transcribe.py audio.mp4 --model base` |
| 30+ minutes | `tiny` or split | ~500MB | Split file or use tiny model |

**File Splitting for Large Audio:**
```bash
# Split large file into 10-minute chunks
ffmpeg -i large_audio.mp4 -f segment -segment_time 600 -c copy chunk_%03d.mp4

# Process chunks individually
for chunk in chunk_*.mp4; do
    python transcribe.py "$chunk" --model small
done

# Combine results
cat output/chunk_*_small.txt > combined_transcription.txt
```

#### Problem: Docker container killed (OOMKilled)
```bash
# Check container exit codes
docker-compose ps
# Look for exit code 137 (OOMKilled)
```

**Solutions:**
```bash
# Increase Docker memory limit
# Edit docker-compose.yml:
services:
  whisper-core:
    mem_limit: 4g
    memswap_limit: 4g

# Or use resource constraints
docker run --memory="4g" --memory-swap="4g" whisper-local:latest
```

### Swap Space Issues

#### Problem: System becomes unresponsive during processing
**Solution: Increase swap space**
```bash
# Check current swap
free -h
swapon --show

# Create swap file (4GB)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 🔑 API Issues

### OpenAI API Problems

#### Problem: "Invalid API key" or "Authentication failed"
```bash
# Check API key
echo $OPENAI_API_KEY
# Should show your API key, not empty
```

**Solutions:**
```bash
# Set API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Make permanent
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# Test API key
python -c "
import openai
client = openai.OpenAI()
print('API key is valid!')
"
```

#### Problem: "Rate limit exceeded" or "Quota exceeded"
```bash
# Error examples:
openai.RateLimitError: Rate limit reached
openai.QuotaExceededError: You exceeded your current quota
```

**Solutions:**
```bash
# Check API usage
python -c "
import openai
client = openai.OpenAI()
# Check your usage at https://platform.openai.com/usage
"

# Use local transcription instead
python transcribe.py audio.mp4 --method local

# Or Docker method
python transcribe.py audio.mp4 --method docker
```

#### Problem: File size too large for API
```bash
# Error:
File size 30MB exceeds the maximum allowed size of 25MB
```

**Solution: Compress or split file**
```bash
# Compress audio
ffmpeg -i large_audio.mp4 -ac 1 -ar 16000 -b:a 64k compressed_audio.mp4

# Check file size
ls -lh compressed_audio.mp4

# Split if still too large
ffmpeg -i compressed_audio.mp4 -f segment -segment_time 300 -c copy api_chunk_%03d.mp4
```

## 📁 File and Format Issues

### Unsupported File Formats

#### Problem: "Format not supported" error
**Supported formats:** MP3, MP4, M4A, WAV, WEBM, FLAC

**Solution: Convert unsupported formats**
```bash
# Convert various formats to MP4
ffmpeg -i audio.avi -c:a aac audio.mp4          # AVI to MP4
ffmpeg -i audio.mov -c:a aac audio.mp4          # MOV to MP4  
ffmpeg -i audio.mkv -c:a aac audio.mp4          # MKV to MP4
ffmpeg -i audio.wmv -c:a aac audio.mp4          # WMV to MP4

# Convert to WAV for maximum compatibility
ffmpeg -i input_file.any output_file.wav
```

### Corrupted or Invalid Files

#### Problem: "Unable to load audio" or "Invalid file format"
**Diagnostic steps:**
```bash
# Check file integrity
ffprobe audio.mp4 2>&1 | grep "Invalid"

# Get file information
mediainfo audio.mp4

# Try to play file
ffplay audio.mp4  # Press 'q' to quit
```

**Solutions:**
```bash
# Repair corrupted file
ffmpeg -i corrupted.mp4 -c copy repaired.mp4

# Extract audio only
ffmpeg -i video.mp4 -vn -acodec copy audio_only.mp4

# Re-encode if necessary
ffmpeg -i problematic.mp4 -c:a aac -b:a 128k fixed.mp4
```

### Path and Permission Issues

#### Problem: File not found or permission denied
```bash
# Check file existence and permissions
ls -la audio.mp4
file audio.mp4
```

**Solutions:**
```bash
# Use absolute paths
python transcribe.py /full/path/to/audio.mp4

# Fix permissions
chmod 644 audio.mp4

# Check directory permissions
ls -la .
chmod 755 .  # If needed
```

## 🔍 Debugging Tools and Techniques

### Enable Detailed Logging

#### Method 1: Verbose Mode
```bash
# Enable verbose output
python transcribe.py audio.mp4 --verbose

# Save logs to file
python transcribe.py audio.mp4 --verbose 2>&1 | tee transcription.log
```

#### Method 2: Python Logging
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Test transcription with debug info
result = transcriber.transcribe("audio.mp4", model="small")
print(f"Debug info: {result}")
```

### System Diagnostics

#### Complete System Check
```bash
#!/bin/bash
# system_check.sh - Comprehensive system diagnostic

echo "=== System Information ==="
uname -a
lsb_release -a 2>/dev/null || cat /etc/os-release

echo -e "\n=== Python Environment ==="
which python3
python3 --version
pip --version

echo -e "\n=== Virtual Environment ==="
echo "VIRTUAL_ENV: $VIRTUAL_ENV"
which python
python --version

echo -e "\n=== System Resources ==="
free -h
df -h /
lscpu | grep "Model name"

echo -e "\n=== FFmpeg ==="
which ffmpeg
ffmpeg -version | head -1

echo -e "\n=== Docker ==="
which docker
docker --version
docker images | grep whisper

echo -e "\n=== GPU Information ==="
nvidia-smi 2>/dev/null || echo "No NVIDIA GPU detected"

echo -e "\n=== Network Connectivity ==="
ping -c 1 api.openai.com >/dev/null 2>&1 && echo "OpenAI API reachable" || echo "OpenAI API not reachable"

echo -e "\n=== Project Structure ==="
ls -la
```

**Run diagnostic:**
```bash
chmod +x system_check.sh
./system_check.sh > system_report.txt
```

### Performance Profiling

#### Profile Transcription Performance
```python
import time
import psutil
import os

def profile_transcription(audio_file, model="small"):
    """Profile transcription performance."""
    
    # Get initial system state
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    start_time = time.time()
    
    # Run transcription
    result = transcriber.transcribe(audio_file, model=model)
    
    # Get final state
    end_time = time.time()
    end_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Calculate metrics
    processing_time = end_time - start_time
    memory_used = end_memory - start_memory
    
    print(f"Performance Profile:")
    print(f"  Processing time: {processing_time:.2f}s")
    print(f"  Memory used: {memory_used:.1f}MB")
    print(f"  Peak memory: {end_memory:.1f}MB")
    
    if result['success'] and 'audio_duration' in result:
        real_time_factor = result['audio_duration'] / processing_time
        print(f"  Real-time factor: {real_time_factor:.1f}x")
    
    return result

# Usage
result = profile_transcription("audio.mp4", model="small")
```

## 📞 Getting Help

### Collect Information for Support

When reporting issues, collect this information:

```bash
#!/bin/bash
# collect_debug_info.sh

echo "=== Whisper Project Debug Information ==="
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Working directory: $(pwd)"

echo -e "\n=== System ==="
uname -a
python --version
pip list | grep -E "(whisper|torch|ffmpeg)"

echo -e "\n=== Error Details ==="
echo "Command that failed: $1"
echo "Error message:"
# Run the failing command and capture output
$1 2>&1 | tail -20

echo -e "\n=== Recent logs ==="
ls -la *.log 2>/dev/null | tail -5
tail -20 *.log 2>/dev/null

echo -e "\n=== File information ==="
if [ -f "$2" ]; then
    ls -la "$2"
    file "$2"
    ffprobe "$2" 2>&1 | head -10
fi
```

**Usage:**
```bash
# Collect debug info for failed command
./collect_debug_info.sh "python transcribe.py problematic.mp4" "problematic.mp4"
```

### Common Support Questions

#### Q: Which model should I use?
**A:** Use `small` for the best balance of quality and speed. Only use `tiny` for quick testing, and `medium`/`large` for critical accuracy needs.

#### Q: Why is transcription so slow?
**A:** Check that you're using the `small` model, not `tiny`. Specify the language explicitly (`--language en`) to skip auto-detection.

#### Q: How do I process multiple files?
**A:** Use batch processing:
```bash
for file in *.mp4; do
    python clean_transcribe.py "$file" --model small
done
```

#### Q: Can I use this commercially?
**A:** Yes, but check the license terms for your specific model and any third-party dependencies.

#### Q: How do I improve accuracy?
**A:** Use a larger model (`medium` or `large`), specify the correct language, and ensure good audio quality.

### Emergency Recovery

#### Complete Project Reset
```bash
# Backup any important transcriptions
cp -r output output_backup_$(date +%Y%m%d_%H%M%S)

# Reset environment
deactivate 2>/dev/null || true
rm -rf whisper-env

# Reinstall from scratch
python3 -m venv whisper-env
source whisper-env/bin/activate
pip install -r requirements.txt

# Test installation
python transcribe.py --help
```

#### Docker Reset
```bash
# Stop all containers
docker-compose down

# Remove all whisper-related containers and images
docker container prune -f
docker rmi $(docker images | grep whisper | awk '{print $3}')

# Rebuild everything
docker-compose build --no-cache
docker-compose up
```

---

**Related Documentation**:
- [CLEAN_TRANSCRIBE_GUIDE.md](CLEAN_TRANSCRIBE_GUIDE.md) - User-friendly interface guide
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- [MODEL_SELECTION_GUIDE.md](MODEL_SELECTION_GUIDE.md) - Model comparison and selection
- [DOCKER_GUIDE.md](DOCKER_GUIDE.md) - Docker deployment and configuration

**Need more help?** Check the project README.md or create an issue with debug information.