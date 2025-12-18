#!/bin/bash
"""
Docker Whisper Transcription Scripts

This directory contains scripts for running Whisper transcription using Docker containers.
These solutions avoid Python dependency conflicts and can utilize GPU acceleration.
"""

# Standard OpenAI Whisper Docker Container
transcribe_with_whisper() {
    local input_file="$1"
    local model="${2:-medium}"
    local language="${3:-auto}"
    local output_dir="${4:-./output}"

    if [ -z "$input_file" ]; then
        echo "Usage: transcribe_with_whisper <input_file> [model] [language] [output_dir]"
        echo "Example: transcribe_with_whisper audio.mp3 medium en ./output"
        return 1
    fi

    if [ ! -f "$input_file" ]; then
        echo "❌ Error: File '$input_file' not found"
        return 1
    fi

    echo "🐳 Running OpenAI Whisper in Docker container..."
    echo "📁 Input: $input_file"
    echo "🤖 Model: $model"
    echo "🌍 Language: $language"
    echo "📂 Output: $output_dir"

    mkdir -p "$output_dir"

    # Use our custom whisper container
    docker run --rm \
        -v "$(pwd):/data" \
        whisper-local:latest \
        --model "$model" \
        --language "$language" \
        --output_dir "/data/$output_dir" \
        "/data/$input_file"
}

# Faster Whisper Docker Container (Optimized)
transcribe_with_faster_whisper() {
    local input_file="$1"
    local model="${2:-medium}"
    local language="${3:-auto}"
    local output_dir="${4:-./output}"

    if [ -z "$input_file" ]; then
        echo "Usage: transcribe_with_faster_whisper <input_file> [model] [language] [output_dir]"
        echo "Example: transcribe_with_faster_whisper audio.mp3 medium en ./output"
        return 1
    fi

    if [ ! -f "$input_file" ]; then
        echo "❌ Error: File '$input_file' not found"
        return 1
    fi

    echo "🚀 Running Faster-Whisper in Docker container..."
    echo "📁 Input: $input_file"
    echo "🤖 Model: $model"
    echo "🌍 Language: $language"
    echo "📂 Output: $output_dir"

    mkdir -p "$output_dir"

    # Use our custom faster-whisper container
    docker run --rm \
        -v "$(pwd):/data" \
        faster-whisper:latest \
        --model "$model" \
        --language "$language" \
        --output_dir "/data/$output_dir" \
        "/data/$input_file"
}

# Batch process all audio files in a directory
batch_transcribe() {
    local input_dir="${1:-./input}"
    local output_dir="${2:-./output}"
    local model="${3:-medium}"
    local use_faster="${4:-false}"

    echo "🔄 Starting batch transcription..."
    echo "📂 Input directory: $input_dir"
    echo "📂 Output directory: $output_dir"
    echo "🤖 Model: $model"

    if [ ! -d "$input_dir" ]; then
        echo "❌ Error: Input directory '$input_dir' not found"
        return 1
    fi

    mkdir -p "$output_dir"

    local count=0
    for file in "$input_dir"/*.{mp3,mp4,wav,m4a,flac,ogg}; do
        [ -f "$file" ] || continue

        echo "🎵 Processing: $(basename "$file")"

        if [ "$use_faster" = "true" ]; then
            transcribe_with_faster_whisper "$file" "$model" "auto" "$output_dir"
        else
            transcribe_with_whisper "$file" "$model" "auto" "$output_dir"
        fi

        ((count++))
    done

    echo "✅ Batch processing complete! Processed $count files."
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed or not in PATH"
        echo "Please install Docker first: https://docs.docker.com/get-docker/"
        return 1
    fi

    if ! docker info &> /dev/null; then
        echo "❌ Docker daemon is not running"
        echo "Please start Docker daemon"
        return 1
    fi

    echo "✅ Docker is available and running"
    return 0
}

# Show usage information
show_usage() {
    echo "Docker Whisper Transcription Scripts"
    echo "===================================="
    echo ""
    echo "Available functions:"
    echo "  transcribe_with_whisper <file> [model] [language] [output_dir]"
    echo "  transcribe_with_faster_whisper <file> [model] [language] [output_dir]"
    echo "  batch_transcribe [input_dir] [output_dir] [model] [use_faster]"
    echo "  check_docker"
    echo ""
    echo "Models: tiny, base, small, medium, large"
    echo "Languages: en, es, fr, de, it, ja, ko, zh, etc. (use 'auto' for detection)"
    echo ""
    echo "Examples:"
    echo "  transcribe_with_whisper audio.mp3"
    echo "  transcribe_with_faster_whisper video.mp4 large en ./transcripts"
    echo "  batch_transcribe ./input ./output medium true"
}

# Main script logic
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    case "${1:-help}" in
        "whisper")
            shift
            transcribe_with_whisper "$@"
            ;;
        "faster")
            shift
            transcribe_with_faster_whisper "$@"
            ;;
        "batch")
            shift
            batch_transcribe "$@"
            ;;
        "check")
            check_docker
            ;;
        "help"|*)
            show_usage
            ;;
    esac
fi
