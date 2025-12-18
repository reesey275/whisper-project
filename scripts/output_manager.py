#!/usr/bin/env python3
"""
Output Management System - Clean, organized transcription outputs
"""
import os
from datetime import datetime
from pathlib import Path


class OutputManager:
    """Manages organized output directory structure and file naming"""

    def __init__(self, base_dir="output"):
        self.base_dir = Path(base_dir)
        self.production_dir = self.base_dir / "production"
        self.development_dir = self.base_dir / "development"
        self.archive_dir = self.base_dir / "archive"
        self.temp_dir = self.base_dir / "temp"

        # Ensure directories exist
        for dir_path in [
            self.production_dir,
            self.development_dir,
            self.archive_dir,
            self.temp_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_output_path(self, audio_file, mode="production", model="small", timestamp=True):
        """
        Generate organized output path with clean naming

        Args:
            audio_file: Input audio file path
            mode: 'production', 'development', 'archive', or 'temp'
            model: Whisper model used
            timestamp: Include timestamp in filename

        Returns:
            Tuple of (directory_path, filename_base)
        """
        audio_path = Path(audio_file)
        base_name = audio_path.stem

        # Choose output directory
        if mode == "production":
            output_dir = self.production_dir
        elif mode == "development":
            output_dir = self.development_dir
        elif mode == "archive":
            output_dir = self.archive_dir
        else:
            output_dir = self.temp_dir

        # Create clean filename
        if timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_base = f"{base_name}_{model}_{ts}"
        else:
            filename_base = f"{base_name}_{model}"

        return output_dir, filename_base

    def save_transcription(
        self,
        audio_file,
        transcription_text,
        mode="production",
        model="small",
        formats=["txt", "srt", "vtt"],
    ):
        """
        Save transcription in organized format

        Args:
            audio_file: Source audio file
            transcription_text: Transcribed text
            mode: Output mode (production/development/etc)
            model: Model used for transcription
            formats: List of output formats to save

        Returns:
            Dictionary with saved file paths
        """
        output_dir, filename_base = self.get_output_path(audio_file, mode, model)
        saved_files = {}

        # Save text format
        if "txt" in formats:
            txt_path = output_dir / f"{filename_base}.txt"
            txt_path.write_text(transcription_text, encoding="utf-8")
            saved_files["txt"] = str(txt_path)

        # TODO: Add SRT and VTT format generation here
        # For now, just save the text format

        return saved_files

    def list_transcriptions(self, mode="production", pattern="*.txt"):
        """List transcriptions in organized manner"""
        if mode == "production":
            search_dir = self.production_dir
        elif mode == "development":
            search_dir = self.development_dir
        elif mode == "archive":
            search_dir = self.archive_dir
        else:
            search_dir = self.temp_dir

        return list(search_dir.glob(pattern))

    def cleanup_temp(self, older_than_hours=24):
        """Clean up temporary files older than specified hours"""
        import time

        cutoff_time = time.time() - (older_than_hours * 3600)

        cleaned = 0
        for temp_file in self.temp_dir.glob("*"):
            if temp_file.stat().st_mtime < cutoff_time:
                temp_file.unlink()
                cleaned += 1

        return cleaned


# Usage example and integration point
if __name__ == "__main__":
    # Demo of organized output system
    manager = OutputManager()

    print("📁 Organized Output System")
    print("=========================")
    print(f"Production: {manager.production_dir}")
    print(f"Development: {manager.development_dir}")
    print(f"Archive: {manager.archive_dir}")
    print(f"Temp: {manager.temp_dir}")

    # Example usage
    output_dir, filename = manager.get_output_path("test_audio.mp3", "production", "small")
    print(f"\nExample output: {output_dir}/{filename}.txt")
