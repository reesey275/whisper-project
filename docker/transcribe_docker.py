#!/usr/bin/env python3
"""
Python wrapper for Docker Whisper containers

This script provides a Python interface for running Whisper transcription
in Docker containers, making it easy to integrate into Python workflows.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union


class DockerWhisperTranscriber:
    """Docker-based Whisper transcription client."""

    def __init__(
        self,
        use_faster_whisper: bool = True,
        use_gpu: bool = False,
        default_model: str = "medium",
    ):
        """
        Initialize the Docker Whisper transcriber.

        Args:
            use_faster_whisper: Use faster-whisper instead of standard whisper
            use_gpu: Use GPU acceleration (requires NVIDIA Docker)
            default_model: Default model size to use
        """
        self.use_faster_whisper = use_faster_whisper
        self.use_gpu = use_gpu
        self.default_model = default_model

        # Check Docker availability
        if not self._check_docker():
            raise RuntimeError("Docker is not available or not running")

    def _check_docker(self) -> bool:
        """Check if Docker is available and running."""
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_docker_image(self) -> str:
        """Get the appropriate Docker image name."""
        if self.use_faster_whisper:
            return "faster-whisper:latest"
        else:
            return "whisper-local:latest"

    def transcribe(
        self,
        audio_file,
        model="base",
        language="en",
        task="transcribe",
        output_dir=".",
        output_format="txt",
    ):
        """
        Transcribe an audio file using Docker Whisper.

        Args:
            audio_file: Path to the audio file
            model: Model size (tiny, base, small, medium, large)
            language: Language code (e.g., 'en', 'es', 'fr')
            task: Either 'transcribe' or 'translate'
            output_dir: Directory to save output files
            output_format: Output format ('txt', 'srt', 'vtt', 'json', 'all')

        Returns:
            Dictionary with transcription results and output file paths
        """
        audio_path = Path(audio_file)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        model = model or self.default_model
        output_dir = Path(output_dir) if output_dir else audio_path.parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Prepare Docker command
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{audio_path.parent.absolute()}:/data/input:ro",
            "-v",
            f"{output_dir.absolute()}:/data/output",
        ]

        # Add GPU support if needed
        if self.use_gpu:
            docker_cmd.extend(["--runtime", "nvidia", "-e", "NVIDIA_VISIBLE_DEVICES=all"])

        # Add image and Whisper arguments
        docker_cmd.extend(
            [
                self._get_docker_image(),
                "--model",
                model,
                "--task",
                task,
                "--output_dir",
                "/data/output",
            ]
        )

        if language:
            docker_cmd.extend(["--language", language])

        # Add the audio file path at the end
        docker_cmd.append(f"/data/input/{audio_path.name}")

        print(f"🐳 Running Docker command: {' '.join(docker_cmd[2:])}")

        try:
            # Run the Docker container
            result = subprocess.run(docker_cmd, capture_output=True, text=True, check=True)

            # Find output files
            output_files = self._find_output_files(output_dir, audio_path.stem)

            return {
                "success": True,
                "audio_file": str(audio_path),
                "model": model,
                "language": language,
                "task": task,
                "output_files": output_files,
                "output_dir": str(output_dir),
                "docker_output": result.stdout,
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr,
                "audio_file": str(audio_path),
                "model": model,
            }

    def _find_output_files(self, output_dir: Path, basename: str) -> Dict[str, str]:
        """Find generated output files."""
        extensions = [".txt", ".srt", ".vtt", ".json"]
        output_files = {}

        for ext in extensions:
            file_path = output_dir / f"{basename}{ext}"
            if file_path.exists():
                output_files[ext[1:]] = str(file_path)

        return output_files

    def batch_transcribe(
        self,
        input_dir: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        model: Optional[str] = None,
        language: Optional[str] = None,
        file_patterns: List[str] = None,
    ) -> List[Dict]:
        """
        Batch transcribe multiple audio files.

        Args:
            input_dir: Directory containing audio files
            output_dir: Directory to save output files
            model: Model size to use
            language: Language code
            file_patterns: List of file patterns to match

        Returns:
            List of transcription results
        """
        if file_patterns is None:
            file_patterns = ["*.mp3", "*.mp4", "*.wav", "*.m4a", "*.flac", "*.ogg"]

        input_dir = Path(input_dir)
        output_dir = Path(output_dir) if output_dir else input_dir / "output"

        if not input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        # Find all audio files
        audio_files = []
        for pattern in file_patterns:
            audio_files.extend(input_dir.glob(pattern))

        if not audio_files:
            print(f"⚠️  No audio files found in {input_dir}")
            return []

        print(f"🔄 Found {len(audio_files)} audio files to process")

        results = []
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n📁 Processing {i}/{len(audio_files)}: {audio_file.name}")

            result = self.transcribe(
                audio_file=audio_file,
                model=model,
                language=language,
                output_dir=output_dir,
            )

            results.append(result)

            if result["success"]:
                print(f"✅ Completed: {audio_file.name}")
            else:
                print(f"❌ Failed: {audio_file.name} - {result.get('error', 'Unknown error')}")

        successful = sum(1 for r in results if r["success"])
        print(f"\n🎉 Batch processing complete: {successful}/{len(results)} files processed successfully")

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Docker-based Whisper transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("audio_file", help="Path to audio file or directory for batch processing")
    parser.add_argument(
        "--model",
        "-m",
        default="medium",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size",
    )
    parser.add_argument("--language", "-l", default="en", help="Language code (default: en for English)")
    parser.add_argument(
        "--task",
        "-t",
        default="transcribe",
        choices=["transcribe", "translate"],
        help="Task to perform",
    )
    parser.add_argument("--output-dir", "-o", help="Output directory")
    parser.add_argument(
        "--faster-whisper",
        action="store_true",
        help="Use faster-whisper (default: True)",
    )
    parser.add_argument(
        "--standard-whisper",
        action="store_true",
        help="Use standard whisper instead of faster-whisper",
    )
    parser.add_argument("--gpu", action="store_true", help="Use GPU acceleration")
    parser.add_argument("--batch", "-b", action="store_true", help="Batch process directory")

    args = parser.parse_args()

    # Initialize transcriber
    use_faster = not args.standard_whisper
    transcriber = DockerWhisperTranscriber(use_faster_whisper=use_faster, use_gpu=args.gpu, default_model=args.model)

    try:
        if args.batch:
            # Batch processing
            results = transcriber.batch_transcribe(
                input_dir=args.audio_file,
                output_dir=args.output_dir,
                model=args.model,
                language=args.language,
            )

            # Print summary
            successful = sum(1 for r in results if r["success"])
            print(f"\n📊 Summary: {successful}/{len(results)} files processed successfully")

        else:
            # Single file processing
            result = transcriber.transcribe(
                audio_file=args.audio_file,
                model=args.model,
                language=args.language,
                task=args.task,
                output_dir=args.output_dir,
            )

            if result["success"]:
                print("\n✅ Transcription completed successfully!")
                print("📂 Output files:")
                for format_type, file_path in result["output_files"].items():
                    print(f"  {format_type.upper()}: {file_path}")
            else:
                print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
