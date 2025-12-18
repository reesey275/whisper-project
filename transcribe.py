#!/usr/bin/env python3
"""
Universal Whisper Transcription Interface

This script provides a unified interface to all transcription methods
in the project. It automatically chooses the best available method
or allows you to specify your preference.

Usage:
    python transcribe.py audio.mp3                    # Auto-detect best method
    python transcribe.py audio.mp3 --method local     # Force local method
    python transcribe.py audio.mp3 --method docker    # Force Docker method
    python transcribe.py audio.mp3 --method api       # Force API method
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "scripts"))
import json

from output_manager import OutputManager

# Add project paths
sys.path.append(str(Path(__file__).parent / "local"))
sys.path.append(str(Path(__file__).parent / "docker"))
sys.path.append(str(Path(__file__).parent / "api"))


def check_local_whisper():
    """Check if local Whisper is available."""
    try:
        import whisper

        return True
    except ImportError:
        return False


def check_docker():
    """Check if Docker is available."""
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_openai_api():
    """Check if OpenAI API is configured."""
    try:
        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        return api_key is not None
    except ImportError:
        return False


def detect_best_method():
    """Detect the best available transcription method."""
    methods = []

    if check_openai_api():
        methods.append(("api", "OpenAI API (fastest, requires internet)"))

    if check_docker():
        methods.append(("docker", "Docker (no dependencies, consistent)"))

    if check_local_whisper():
        methods.append(("local", "Local Whisper (full control, offline)"))

    return methods


def transcribe_local(audio_path, **kwargs):
    """Transcribe using local Whisper."""
    try:
        from local.transcribe_local import transcribe_file

        result = transcribe_file(
            audio_path=audio_path,
            model_name=kwargs.get("model", "base"),
            language=kwargs.get("language"),
            task=kwargs.get("task", "transcribe"),
            output_dir=kwargs.get("output_dir"),
            verbose=not kwargs.get("quiet", False),
        )

        return {
            "success": True,
            "method": "local",
            "text": result["text"],
            "language": result.get("language"),
            "output_dir": kwargs.get("output_dir", os.path.dirname(audio_path)),
        }

    except Exception as e:
        return {"success": False, "method": "local", "error": str(e)}


def transcribe_docker(audio_path, **kwargs):
    """Transcribe using Docker."""
    try:
        from docker.transcribe_docker import DockerWhisperTranscriber

        transcriber = DockerWhisperTranscriber(
            use_faster_whisper=kwargs.get("use_faster", True),
            use_gpu=kwargs.get("gpu", False),
            default_model=kwargs.get("model", "medium"),
        )

        result = transcriber.transcribe(
            audio_file=audio_path,
            model=kwargs.get("model"),
            language=kwargs.get("language"),
            task=kwargs.get("task", "transcribe"),
            output_dir=kwargs.get("output_dir"),
        )

        return result

    except Exception as e:
        return {"success": False, "method": "docker", "error": str(e)}


def transcribe_api(audio_path, **kwargs):
    """Transcribe using OpenAI API."""
    try:
        from api.transcribe_api import OpenAIWhisperClient

        client = OpenAIWhisperClient()

        if kwargs.get("task", "transcribe") == "translate":
            result = client.translate(
                audio_path=audio_path,
                response_format=kwargs.get("response_format", "json"),
            )
        else:
            result = client.transcribe(
                audio_path=audio_path,
                language=kwargs.get("language"),
                response_format=kwargs.get("response_format", "json"),
            )

        if result["success"]:
            # Save the result
            saved_files = client.save_response(result, kwargs.get("output_dir"))
            result["saved_files"] = saved_files

        return result

    except Exception as e:
        return {"success": False, "method": "api", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Universal Whisper transcription interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Methods:
  local   - Use locally installed Whisper (pip install openai-whisper)
  docker  - Use Docker containers (requires Docker)
  api     - Use OpenAI API (requires OPENAI_API_KEY)
  auto    - Automatically choose best available method (default)

Examples:
  python transcribe.py audio.mp3
  python transcribe.py video.mp4 --method docker --model large
  python transcribe.py podcast.wav --method api --language en
  python transcribe.py interview.m4a --method local --task translate
        """,
    )

    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument(
        "--method",
        "-m",
        default="auto",
        choices=["auto", "local", "docker", "api"],
        help="Transcription method (default: auto)",
    )
    parser.add_argument("--model", default="small", help="Model size (default: small for good context)")
    parser.add_argument("--language", "-l", default="en", help="Language code (default: en for English)")
    parser.add_argument(
        "--task",
        "-t",
        default="transcribe",
        choices=["transcribe", "translate"],
        help="Task to perform (default: transcribe)",
    )
    parser.add_argument("--output-dir", "-o", help="Output directory (default: organized structure)")
    parser.add_argument(
        "--mode",
        "-mode",
        default="production",
        choices=["production", "development", "archive", "temp"],
        help="Output organization mode (default: production)",
    )
    parser.add_argument("--gpu", action="store_true", help="Use GPU acceleration (Docker method)")
    parser.add_argument(
        "--faster",
        action="store_true",
        default=True,
        help="Use faster-whisper (Docker method)",
    )
    parser.add_argument(
        "--response-format",
        default="json",
        choices=["json", "text", "srt", "verbose_json", "vtt"],
        help="Response format for API method",
    )
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress verbose output")
    parser.add_argument("--list-methods", action="store_true", help="List available methods and exit")

    args = parser.parse_args()

    # List available methods if requested
    if args.list_methods:
        print("🔍 Detecting available transcription methods...")
        methods = detect_best_method()

        if methods:
            print("\n✅ Available methods:")
            for i, (method, description) in enumerate(methods, 1):
                print(f"  {i}. {method:8} - {description}")

            print(f"\n🎯 Recommended: {methods[0][0]} ({methods[0][1]})")
        else:
            print("\n❌ No transcription methods available!")
            print("Please install dependencies or configure API keys.")

        return

    if not args.audio_file:
        parser.print_help()
        return

    # Check if audio file exists
    if not os.path.exists(args.audio_file):
        print(f"❌ Error: Audio file not found: {args.audio_file}")
        sys.exit(1)

    # Determine method to use
    if args.method == "auto":
        methods = detect_best_method()
        if not methods:
            print("❌ No transcription methods available!")
            print("Please install dependencies or configure API keys.")
            print("Run with --list-methods to see what's missing.")
            sys.exit(1)

        method = methods[0][0]  # Use the first (best) available method
        if not args.quiet:
            print(f"🎯 Auto-selected method: {method}")
    else:
        method = args.method

    # Prepare arguments
    kwargs = {
        "model": args.model,
        "language": args.language,
        "task": args.task,
        "output_dir": args.output_dir,
        "gpu": args.gpu,
        "use_faster": args.faster,
        "response_format": args.response_format,
        "quiet": args.quiet,
    }

    # Run transcription
    if not args.quiet:
        print(f"🎵 Transcribing: {args.audio_file}")
        print(f"🔧 Method: {method}")
        print(f"🤖 Model: {args.model}")
        print(f"🌍 Language: {args.language or 'auto-detect'}")
        print(f"🎯 Task: {args.task}")

    try:
        if method == "local":
            result = transcribe_local(args.audio_file, **kwargs)
        elif method == "docker":
            result = transcribe_docker(args.audio_file, **kwargs)
        elif method == "api":
            result = transcribe_api(args.audio_file, **kwargs)
        else:
            print(f"❌ Unknown method: {method}")
            sys.exit(1)

        # Handle results
        if result["success"]:
            if not args.quiet:
                print("\n✅ Transcription completed successfully!")
                print(f"🔧 Method used: {result.get('method', method)}")

                if "transcription_time" in result:
                    print(f"⏱️  Processing time: {result['transcription_time']:.2f} seconds")

                # Show output files
                if "output_files" in result:
                    print("📂 Output files:")
                    for format_type, file_path in result["output_files"].items():
                        print(f"   {format_type.upper()}: {file_path}")
                elif "saved_files" in result:
                    print("📂 Output files:")
                    for format_type, file_path in result["saved_files"].items():
                        print(f"   {format_type.upper()}: {file_path}")
                elif "output_dir" in result:
                    print(f"📂 Output directory: {result['output_dir']}")

                # Show text preview
                if "text" in result and result["text"]:
                    preview = result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
                    print("\n📝 Preview:")
                    print(f"   {preview}")
                elif hasattr(result.get("response", {}), "text"):
                    text = result["response"].text
                    preview = text[:200] + "..." if len(text) > 200 else text
                    print("\n📝 Preview:")
                    print(f"   {preview}")

        else:
            print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Transcription cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
