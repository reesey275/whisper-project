#!/usr/bin/env python3
"""
Local Whisper Transcription Script

This script uses OpenAI's Whisper model installed locally to transcribe audio files.
It supports various audio formats and Whisper model sizes.

Usage:
    python transcribe_local.py input.mp3 --model medium --language en
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import whisper
except ImportError:
    print("❌ OpenAI Whisper not found. Install it with:")
    print("   pip install -U openai-whisper")
    sys.exit(1)


def transcribe_file(
    audio_path: str,
    model_name: str = "base",
    language: Optional[str] = None,
    task: str = "transcribe",
    output_dir: Optional[str] = None,
    verbose: bool = True,
) -> dict:
    """
    Transcribe an audio file using Whisper.

    Args:
        audio_path: Path to the audio file
        model_name: Whisper model size (tiny, base, small, medium, large)
        language: Language code (e.g., 'en', 'es', 'fr'). Auto-detect if None
        task: Either 'transcribe' or 'translate'
        output_dir: Directory to save output files. Same as input if None
        verbose: Print progress information

    Returns:
        Dictionary containing transcription results
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if verbose:
        print(f"🎵 Loading audio file: {audio_path}")
        print(f"🤖 Loading Whisper model: {model_name}")

    # Load the model
    start_time = time.time()
    model = whisper.load_model(model_name)
    load_time = time.time() - start_time

    if verbose:
        print(f"⏱️  Model loaded in {load_time:.2f} seconds")
        print(f"🎯 Starting {task}...")

    # Perform transcription
    start_time = time.time()
    result = model.transcribe(audio_path, language=language, task=task, verbose=verbose)
    transcribe_time = time.time() - start_time

    if verbose:
        print(f"✅ {task.capitalize()} completed in {transcribe_time:.2f} seconds")

    # Save output files
    if output_dir is None:
        output_dir = os.path.dirname(audio_path)

    audio_basename = Path(audio_path).stem
    output_base = os.path.join(output_dir, audio_basename)

    # Save as text file
    txt_path = f"{output_base}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result["text"])

    # Save as SRT (subtitle) file
    srt_path = f"{output_base}.srt"
    write_srt(result, srt_path)

    # Save as VTT (WebVTT) file
    vtt_path = f"{output_base}.vtt"
    write_vtt(result, vtt_path)

    if verbose:
        print(f"📄 Text saved to: {txt_path}")
        print(f"📺 SRT subtitles saved to: {srt_path}")
        print(f"🌐 VTT subtitles saved to: {vtt_path}")

    return result


def write_srt(result: dict, output_path: str):
    """Write transcription result as SRT subtitle file."""
    with open(output_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"], 1):
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()

            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")


def write_vtt(result: dict, output_path: str):
    """Write transcription result as WebVTT subtitle file."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")

        for segment in result["segments"]:
            start_time = format_timestamp(segment["start"], vtt_format=True)
            end_time = format_timestamp(segment["end"], vtt_format=True)
            text = segment["text"].strip()

            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")


def format_timestamp(seconds: float, vtt_format: bool = False) -> str:
    """Format seconds as timestamp string."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)

    if vtt_format:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python transcribe_local.py audio.mp3
  python transcribe_local.py video.mp4 --model medium --language en
  python transcribe_local.py podcast.wav --task translate --output-dir ./output

Available models (by size and accuracy):
  tiny    - ~39 MB,  ~32x realtime speed
  base    - ~74 MB,  ~16x realtime speed
  small   - ~244 MB, ~6x realtime speed
  medium  - ~769 MB, ~2x realtime speed
  large   - ~1550 MB, ~1x realtime speed
        """,
    )

    parser.add_argument("audio_file", help="Path to the audio/video file to transcribe")

    parser.add_argument(
        "--model",
        "-m",
        default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: small for better context)",
    )

    parser.add_argument("--language", "-l", default="en", help="Language code (default: en for English)")

    parser.add_argument(
        "--task",
        "-t",
        default="transcribe",
        choices=["transcribe", "translate"],
        help="Task to perform (default: transcribe)",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        help="Output directory for transcription files (default: same as input)",
    )

    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress verbose output")

    args = parser.parse_args()

    try:
        result = transcribe_file(
            audio_path=args.audio_file,
            model_name=args.model,
            language=args.language,
            task=args.task,
            output_dir=args.output_dir,
            verbose=not args.quiet,
        )

        if not args.quiet:
            print("\n🎉 Transcription complete!")
            print(f"📊 Detected language: {result.get('language', 'unknown')}")
            print(f"📝 Text length: {len(result['text'])} characters")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
