#!/bin/bash

# Quick Setup Script for Whisper Transcription Project
# This script helps you set up the project based on your preferred method

set -e

echo "🎵 Whisper Transcription Project Setup"
echo "======================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Function to install local dependencies
setup_local() {
    echo ""
    echo "📦 Setting up local Whisper..."
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        echo "❌ pip3 is required but not installed"
        exit 1
    fi
    
    # Install requirements  
    echo "Installing Python dependencies..."
    pip3 install -r requirements.txt
    
    echo "✅ Local setup complete!"
    echo ""
    echo "💡 Test with: python local/transcribe_local.py --help"
}

# Function to setup Docker
setup_docker() {
    echo ""
    echo "🐳 Setting up Docker..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed"
        echo "Please install Docker Desktop: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        echo "❌ Docker daemon is not running"
        echo "Please start Docker Desktop"
        exit 1
    fi
    
    echo "✅ Docker is available"
    
    # Pull Docker images
    echo "Pulling Whisper Docker images..."
    docker pull ghcr.io/onedr0p/whisper:latest || echo "⚠️  Failed to pull standard whisper image"
    docker pull ghcr.io/guillaumekln/faster-whisper:latest || echo "⚠️  Failed to pull faster-whisper image"
    
    # Make scripts executable
    chmod +x docker/transcribe_docker.sh
    
    echo "✅ Docker setup complete!"
    echo ""
    echo "💡 Test with: ./docker/transcribe_docker.sh help"
}

# Function to setup API keys
setup_api() {
    echo ""
    echo "🔑 Setting up API access..."
    
    # Install minimal requirements for API usage
    pip3 install openai requests
    
    # Copy environment template
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📄 Created .env file from template"
        echo "Please edit .env and add your API keys"
    else
        echo "📄 .env file already exists"
    fi
    
    echo "✅ API setup complete!"
    echo ""
    echo "💡 Edit .env file and add your API keys"
    echo "💡 Test with: python api/transcribe_api.py --help"
}

# Function to create sample audio
create_sample() {
    echo ""
    echo "🎵 Creating sample audio file..."
    
    # Create input directory
    mkdir -p input
    
    # Create a simple test file (requires ffmpeg)
    if command -v ffmpeg &> /dev/null; then
        # Generate a 5-second tone for testing
        ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -y input/test_tone.wav 2>/dev/null
        echo "✅ Created input/test_tone.wav for testing"
    else
        echo "⚠️  ffmpeg not found - cannot create sample audio"
        echo "Please place your own audio files in the input/ directory"
    fi
}

# Main setup logic
echo "Choose your setup method:"
echo "1) Local Whisper (full control, works offline)"
echo "2) Docker containers (clean, no dependencies)"  
echo "3) API services (fastest, requires internet)"
echo "4) All methods (comprehensive setup)"
echo "5) Just create directories and sample files"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        setup_local
        create_sample
        ;;
    2)
        setup_docker
        create_sample
        ;;
    3)
        setup_api
        create_sample
        ;;
    4)
        setup_local
        setup_docker  
        setup_api
        create_sample
        ;;
    5)
        create_sample
        echo "✅ Directories created"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📁 Project structure:"
echo "   input/     - Place your audio files here"
echo "   output/    - Transcription results appear here"
echo "   local/     - Local Whisper scripts"
echo "   docker/    - Docker-based solutions"
echo "   api/       - Cloud API clients"
echo ""
echo "🚀 Quick start:"
echo "   python transcribe.py --list-methods    # See available methods"
echo "   python transcribe.py input/audio.mp3   # Auto-transcribe"
echo ""
echo "📖 See README.md for detailed usage instructions"