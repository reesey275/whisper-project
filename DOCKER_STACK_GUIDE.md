# Docker Development Stack Guide

## 🐳 Overview

This Docker stack provides a comprehensive, scalable solution for Whisper transcription with multiple deployment configurations and the ability to run multiple independent stacks simultaneously.

## 📋 Stack Components

### Core Services
- **whisper-core**: Main transcription service using your custom `whisper-local:latest` image
- **whisper-watcher**: Automatic file processing when files are added to input directory
- **redis**: Job queue for batch processing
- **whisper-worker**: Scalable workers for queue processing

### Optional Services (Profiles)
- **Web UI**: Browser-based interface for file uploads and management
- **API Gateway**: Production-ready API with load balancing
- **GPU Support**: NVIDIA GPU acceleration for faster processing

## 🚀 Quick Start

### 1. Basic Stack (Single File Processing)
```bash
# Start core Whisper service
docker-compose up -d whisper-core

# Transcribe a file
docker-compose exec whisper-core python transcribe.py /app/input/your-file.mp4
```

### 2. Auto-Processing Stack (Watch Directory)
```bash
# Start with automatic file watching
docker-compose --profile auto up -d

# Drop files into input/ directory - they'll be auto-transcribed
cp your-video.mp4 input/
```

### 3. Queue Processing Stack (Batch Jobs)
```bash
# Start with Redis queue system
docker-compose --profile queue up -d

# Submit jobs via queue client
docker-compose exec whisper-core python /app/scripts/queue_client.py submit --file /app/input/video.mp4

# Check queue status
docker-compose exec whisper-core python /app/scripts/queue_client.py status
```

## 🔧 Environment Configurations

### Development Environment
```bash
# Hot reload, debugging, exposed ports
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Access development API: http://localhost:8000
# Access development UI: http://localhost:3000
```

### Production Environment
```bash
# Optimized for performance, scaling, load balancing
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Includes nginx load balancer and multiple worker replicas
```

### GPU-Accelerated Environment
```bash
# Requires NVIDIA Docker runtime
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d

# Uses CUDA for significantly faster processing
```

## 🔄 Multiple Stack Management

### Running Multiple Independent Stacks

You can run multiple completely independent Whisper stacks for different projects or users:

```bash
# Project Alpha (Development)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml -p project-alpha up -d

# Project Beta (Production)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml -p project-beta up -d

# ML Processing (GPU)
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml -p ml-processing up -d
```

### Using the Stack Manager Script

```bash
# Start different configurations
./scripts/stack-manager.sh start dev project-alpha
./scripts/stack-manager.sh start prod project-beta
./scripts/stack-manager.sh start gpu ml-work

# List all running stacks
./scripts/stack-manager.sh list

# View logs
./scripts/stack-manager.sh logs project-alpha whisper-core

# Stop specific stack
./scripts/stack-manager.sh stop project-alpha
```

## 📁 Directory Structure

```
whisper-project/
├── docker-compose.yml          # Base configuration
├── docker-compose.dev.yml      # Development overrides
├── docker-compose.prod.yml     # Production overrides
├── docker-compose.gpu.yml      # GPU acceleration
├── scripts/
│   ├── stack-manager.sh        # Multi-stack management
│   ├── file_watcher.py         # Auto file processing
│   ├── queue_worker.py         # Redis queue worker
│   └── queue_client.py         # Job submission client
├── input/                      # Input files (mounted to all stacks)
├── output/
│   ├── transcriptions/         # Manual transcription results
│   ├── auto-transcriptions/    # Auto-watcher results
│   └── queue-transcriptions/   # Queue processing results
└── [existing project files]
```

## ⚙️ Configuration Options

### Environment Variables

```bash
# Core service settings
WHISPER_DEFAULT_MODEL=base      # Default model (tiny, base, small, medium, large)
WHISPER_DEVICE=cpu              # Processing device (cpu, cuda)
DEBUG=0                         # Debug mode (0/1)
LOG_LEVEL=INFO                  # Logging level

# File watcher settings
WATCH_DIRECTORY=/app/input      # Directory to monitor
OUTPUT_DIRECTORY=/app/output/auto-transcriptions

# Queue settings
REDIS_URL=redis://redis:6379    # Redis connection
```

### Volume Mounts

- `./input:/app/input:ro` - Input files (read-only for safety)
- `./output:/app/output` - Output transcriptions
- `whisper-models:/root/.cache/whisper` - Cached Whisper models
- `redis-data:/data` - Redis persistence

### Network Isolation

Each stack gets its own network namespace, so multiple stacks can run without port conflicts:

- Stack 1: `project-alpha_whisper-network`
- Stack 2: `project-beta_whisper-network`
- Stack 3: `ml-processing_whisper-network`

## 🎯 Usage Patterns

### Pattern 1: Development & Testing
```bash
# Start development environment
./scripts/stack-manager.sh start dev whisper-dev

# Mount your code, hot reload enabled
# API available at localhost:8000
# UI available at localhost:3000
```

### Pattern 2: Production Transcription Service
```bash
# Start production stack with queue processing
./scripts/stack-manager.sh start full whisper-prod

# Submit batch jobs
docker-compose -p whisper-prod exec whisper-core python /app/scripts/queue_client.py submit --file /app/input/batch1.mp4
```

### Pattern 3: Multi-Tenant Setup
```bash
# Tenant A - Standard processing
./scripts/stack-manager.sh start prod tenant-a

# Tenant B - GPU-accelerated
./scripts/stack-manager.sh start gpu tenant-b

# Each tenant has isolated input/output directories
```

### Pattern 4: Auto-Processing Pipeline
```bash
# Start auto-watcher
./scripts/stack-manager.sh start auto media-pipeline

# Files dropped in input/ are automatically processed
# Results appear in output/auto-transcriptions/
```

## 🔍 Monitoring & Debugging

### View Service Logs
```bash
# All services
docker-compose -p project-name logs -f

# Specific service
docker-compose -p project-name logs -f whisper-core
```

### Check Service Status
```bash
# List running containers
docker-compose -p project-name ps

# Check resource usage
docker stats
```

### Queue Monitoring
```bash
# Queue status
docker-compose -p project-name exec whisper-core python /app/scripts/queue_client.py status

# Redis CLI access
docker-compose -p project-name exec redis redis-cli
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**: Use different project names (`-p`) for multiple stacks
2. **Model Downloads**: First run may be slow while downloading Whisper models
3. **GPU Issues**: Ensure NVIDIA Docker runtime is installed for GPU support
4. **File Permissions**: Input files should be readable by Docker containers

### Reset Everything
```bash
# Stop all stacks and clean up
docker-compose down -v --remove-orphans
docker system prune -f

# Rebuild custom images if needed
docker build -t whisper-local:latest -f docker/Dockerfile .
```

## 📊 Performance Considerations

### Scaling Workers
```bash
# Scale queue workers in production
docker-compose -p project-name up -d --scale whisper-worker=4
```

### Resource Limits
- **CPU**: Each worker can use ~2 CPU cores during transcription
- **Memory**: 2-4GB RAM per worker depending on model size
- **GPU**: Significantly faster, can handle larger models efficiently

### Model Selection
- **tiny**: Fastest, lowest quality (39 MB)
- **base**: Good balance (74 MB)
- **small**: Better quality (244 MB)
- **medium**: High quality (769 MB)
- **large**: Best quality (1550 MB)

## 🎉 Benefits of This Stack

✅ **Multiple Independent Stacks**: Run several projects simultaneously
✅ **Environment Flexibility**: Development, production, GPU configurations
✅ **Auto-Processing**: Drop files and get transcriptions automatically
✅ **Queue System**: Handle batch jobs efficiently
✅ **Scalable**: Add more workers as needed
✅ **Isolated**: Each stack has its own network and resources
✅ **Production Ready**: Load balancing, monitoring, persistence

This Docker stack transforms your Whisper project into a enterprise-ready transcription service that can handle everything from single file processing to large-scale batch operations! 🚀