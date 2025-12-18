#!/usr/bin/env python3
"""
Alternative API Clients for Whisper Transcription

This script provides clients for other transcription services as alternatives
to OpenAI's API, including AssemblyAI, Rev AI, and others.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests

# Optional imports for different services
try:
    import assemblyai as aai

    ASSEMBLYAI_AVAILABLE = True
except ImportError:
    ASSEMBLYAI_AVAILABLE = False


class AssemblyAIClient:
    """AssemblyAI transcription client."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize AssemblyAI client."""
        if not ASSEMBLYAI_AVAILABLE:
            raise ImportError("AssemblyAI SDK not installed. Run: pip install assemblyai")

        self.api_key = api_key or os.getenv("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            raise ValueError("AssemblyAI API key required. Set ASSEMBLYAI_API_KEY environment variable.")

        aai.settings.api_key = self.api_key

    def transcribe(
        self,
        audio_path: Union[str, Path],
        language_code: Optional[str] = None,
        speaker_labels: bool = False,
        auto_punctuation: bool = True,
        format_text: bool = True,
    ) -> Dict:
        """
        Transcribe audio using AssemblyAI.

        Args:
            audio_path: Path to audio file
            language_code: Language code (e.g., 'en', 'es')
            speaker_labels: Enable speaker diarization
            auto_punctuation: Enable automatic punctuation
            format_text: Enable text formatting

        Returns:
            Transcription result dictionary
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"🎵 Transcribing with AssemblyAI: {audio_path.name}")
        start_time = time.time()

        try:
            # Configure transcription settings
            config = aai.TranscriptionConfig(
                language_code=language_code,
                speaker_labels=speaker_labels,
                auto_punctuation=auto_punctuation,
                format_text=format_text,
            )

            # Create transcriber and transcribe
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(str(audio_path), config=config)

            transcription_time = time.time() - start_time

            if transcript.status == aai.TranscriptStatus.error:
                return {
                    "success": False,
                    "error": transcript.error,
                    "audio_file": str(audio_path),
                }

            return {
                "success": True,
                "audio_file": str(audio_path),
                "transcription_time": transcription_time,
                "text": transcript.text,
                "confidence": transcript.confidence,
                "words": transcript.words if hasattr(transcript, "words") else None,
                "utterances": transcript.utterances if speaker_labels else None,
                "service": "AssemblyAI",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "audio_file": str(audio_path),
                "transcription_time": time.time() - start_time,
            }


class RevAIClient:
    """Rev AI transcription client (using REST API)."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Rev AI client."""
        self.api_key = api_key or os.getenv("REV_AI_API_KEY")
        if not self.api_key:
            raise ValueError("Rev AI API key required. Set REV_AI_API_KEY environment variable.")

        self.base_url = "https://api.rev.ai/speechtotext/v1"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def transcribe(
        self,
        audio_path: Union[str, Path],
        language: str = "en",
        speaker_names: Optional[List[str]] = None,
    ) -> Dict:
        """
        Transcribe audio using Rev AI.

        Args:
            audio_path: Path to audio file
            language: Language code
            speaker_names: List of speaker names for diarization

        Returns:
            Transcription result dictionary
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"🎵 Transcribing with Rev AI: {audio_path.name}")
        start_time = time.time()

        try:
            # Submit job
            with open(audio_path, "rb") as audio_file:
                files = {"media": (audio_path.name, audio_file, "audio/mpeg")}

                options = {
                    "language": language,
                    "metadata": json.dumps({"filename": audio_path.name}),
                }

                if speaker_names:
                    options["speaker_names"] = json.dumps(speaker_names)

                response = requests.post(
                    f"{self.base_url}/jobs",
                    headers=self.headers,
                    files=files,
                    data=options,
                )

                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Failed to submit job: {response.text}",
                        "audio_file": str(audio_path),
                    }

                job = response.json()
                job_id = job["id"]

            # Poll for completion
            print(f"📋 Job submitted: {job_id}")
            print("⏳ Waiting for transcription to complete...")

            while True:
                response = requests.get(f"{self.base_url}/jobs/{job_id}", headers=self.headers)

                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Failed to get job status: {response.text}",
                        "audio_file": str(audio_path),
                    }

                job_status = response.json()
                status = job_status["status"]

                if status == "transcribed":
                    break
                elif status == "failed":
                    return {
                        "success": False,
                        "error": f"Transcription failed: {job_status.get('failure_detail', 'Unknown error')}",
                        "audio_file": str(audio_path),
                    }

                time.sleep(2)  # Wait 2 seconds before polling again

            # Get transcript
            response = requests.get(f"{self.base_url}/jobs/{job_id}/transcript", headers=self.headers)

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get transcript: {response.text}",
                    "audio_file": str(audio_path),
                }

            transcript_data = response.json()
            transcription_time = time.time() - start_time

            # Extract text from monologues
            text_parts = []
            for monologue in transcript_data.get("monologues", []):
                for element in monologue.get("elements", []):
                    if element.get("type") == "text":
                        text_parts.append(element.get("value", ""))

            full_text = "".join(text_parts)

            return {
                "success": True,
                "audio_file": str(audio_path),
                "transcription_time": transcription_time,
                "text": full_text,
                "job_id": job_id,
                "monologues": transcript_data.get("monologues", []),
                "service": "Rev AI",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "audio_file": str(audio_path),
                "transcription_time": time.time() - start_time,
            }


class SpeechmaticsClient:
    """Speechmatics transcription client."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Speechmatics client."""
        self.api_key = api_key or os.getenv("SPEECHMATICS_API_KEY")
        if not self.api_key:
            raise ValueError("Speechmatics API key required. Set SPEECHMATICS_API_KEY environment variable.")

        self.base_url = "https://asr.api.speechmatics.com/v2"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def transcribe(
        self,
        audio_path: Union[str, Path],
        language: str = "en",
        enable_partials: bool = False,
        diarization: str = "none",
    ) -> Dict:
        """
        Transcribe audio using Speechmatics.

        Args:
            audio_path: Path to audio file
            language: Language code
            enable_partials: Enable partial results
            diarization: Diarization mode ("none", "speaker", "channel")

        Returns:
            Transcription result dictionary
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        print(f"🎵 Transcribing with Speechmatics: {audio_path.name}")
        start_time = time.time()

        try:
            # Prepare configuration
            config = {
                "type": "transcription",
                "transcription_config": {
                    "language": language,
                    "enable_partials": enable_partials,
                    "diarization": diarization,
                },
            }

            # Submit job
            with open(audio_path, "rb") as audio_file:
                files = {
                    "data_file": (audio_path.name, audio_file),
                    "config": (None, json.dumps(config)),
                }

                response = requests.post(f"{self.base_url}/jobs", headers=self.headers, files=files)

                if response.status_code != 201:
                    return {
                        "success": False,
                        "error": f"Failed to submit job: {response.text}",
                        "audio_file": str(audio_path),
                    }

                job = response.json()
                job_id = job["id"]

            # Poll for completion
            print(f"📋 Job submitted: {job_id}")
            print("⏳ Waiting for transcription to complete...")

            while True:
                response = requests.get(f"{self.base_url}/jobs/{job_id}", headers=self.headers)

                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Failed to get job status: {response.text}",
                        "audio_file": str(audio_path),
                    }

                job_status = response.json()["job"]
                status = job_status["status"]

                if status == "done":
                    break
                elif status in ["rejected", "expired"]:
                    return {
                        "success": False,
                        "error": f"Job {status}: {job_status.get('errors', 'Unknown error')}",
                        "audio_file": str(audio_path),
                    }

                time.sleep(3)  # Wait 3 seconds before polling again

            # Get transcript
            response = requests.get(
                f"{self.base_url}/jobs/{job_id}/transcript?format=json-v2",
                headers=self.headers,
            )

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to get transcript: {response.text}",
                    "audio_file": str(audio_path),
                }

            transcript_data = response.json()
            transcription_time = time.time() - start_time

            # Extract text
            text_parts = []
            for result in transcript_data.get("results", []):
                for alternative in result.get("alternatives", []):
                    text_parts.append(alternative.get("content", ""))

            full_text = " ".join(text_parts)

            return {
                "success": True,
                "audio_file": str(audio_path),
                "transcription_time": transcription_time,
                "text": full_text,
                "job_id": job_id,
                "results": transcript_data.get("results", []),
                "service": "Speechmatics",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "audio_file": str(audio_path),
                "transcription_time": time.time() - start_time,
            }


def save_result(result: Dict, output_dir: Optional[Union[str, Path]] = None) -> Dict[str, str]:
    """Save transcription result to files."""
    if not result["success"]:
        raise ValueError("Cannot save failed transcription result")

    audio_path = Path(result["audio_file"])
    if output_dir is None:
        output_dir = audio_path.parent / "output"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    basename = audio_path.stem
    service = result.get("service", "unknown").lower().replace(" ", "_")

    saved_files = {}

    # Save as text
    if "text" in result:
        text_path = output_dir / f"{basename}_{service}.txt"
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        saved_files["txt"] = str(text_path)

    # Save full result as JSON
    json_path = output_dir / f"{basename}_{service}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str)
    saved_files["json"] = str(json_path)

    return saved_files


def main():
    parser = argparse.ArgumentParser(
        description="Alternative API transcription clients",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument(
        "--service",
        "-s",
        required=True,
        choices=["assemblyai", "revai", "speechmatics"],
        help="Transcription service to use",
    )
    parser.add_argument("--api-key", help="API key for the service")
    parser.add_argument("--language", "-l", default="en", help="Language code")
    parser.add_argument("--output-dir", "-o", help="Output directory")

    # Service-specific options
    parser.add_argument(
        "--speaker-labels",
        action="store_true",
        help="Enable speaker diarization (AssemblyAI)",
    )
    parser.add_argument("--speaker-names", nargs="+", help="Speaker names for diarization (Rev AI)")

    args = parser.parse_args()

    try:
        # Initialize the appropriate client
        if args.service == "assemblyai":
            client = AssemblyAIClient(api_key=args.api_key)
            result = client.transcribe(
                audio_path=args.audio_file,
                language_code=args.language,
                speaker_labels=args.speaker_labels,
            )
        elif args.service == "revai":
            client = RevAIClient(api_key=args.api_key)
            result = client.transcribe(
                audio_path=args.audio_file,
                language=args.language,
                speaker_names=args.speaker_names,
            )
        elif args.service == "speechmatics":
            client = SpeechmaticsClient(api_key=args.api_key)
            result = client.transcribe(audio_path=args.audio_file, language=args.language)

        if result["success"]:
            # Save the result
            saved_files = save_result(result, args.output_dir)

            print("\n✅ Transcription completed successfully!")
            print(f"⏱️  Processing time: {result['transcription_time']:.2f} seconds")
            print(f"🏢 Service: {result['service']}")
            print("📂 Output files:")
            for format_type, file_path in saved_files.items():
                print(f"   {format_type.upper()}: {file_path}")

            # Print text preview
            if "text" in result and len(result["text"]) > 0:
                preview = result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
                print("\n📝 Preview:")
                print(f"   {preview}")
        else:
            print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
