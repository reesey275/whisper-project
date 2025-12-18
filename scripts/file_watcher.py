#!/usr/bin/env python3
"""
File Watcher Service - Automatically processes new files in input directory
"""
import logging
import os
import subprocess
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class WhisperFileHandler(FileSystemEventHandler):
    def __init__(self, output_dir="/app/output/auto-transcriptions"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processing = set()  # Track files being processed

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if it's an audio/video file
        if file_path.suffix.lower() in [
            ".mp3",
            ".mp4",
            ".wav",
            ".m4a",
            ".flac",
            ".ogg",
            ".webm",
        ]:
            self.process_file(file_path)

    def process_file(self, file_path):
        if str(file_path) in self.processing:
            return

        try:
            self.processing.add(str(file_path))
            logger.info(f"Processing new file: {file_path.name}")

            # Wait a bit to ensure file is fully written
            time.sleep(2)

            # Build output filename
            output_file = self.output_dir / f"{file_path.stem}.txt"

            # Run transcription
            cmd = [
                "python",
                "/app/transcribe.py",
                str(file_path),
                "--output-dir",
                str(self.output_dir),
                "--model",
                os.getenv("WHISPER_DEFAULT_MODEL", "base"),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"Successfully transcribed: {file_path.name}")
            else:
                logger.error(f"Failed to transcribe {file_path.name}: {result.stderr}")

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {str(e)}")
        finally:
            self.processing.discard(str(file_path))


def main():
    watch_dir = os.getenv("WATCH_DIRECTORY", "/app/input")
    output_dir = os.getenv("OUTPUT_DIRECTORY", "/app/output/auto-transcriptions")

    logger.info(f"Starting file watcher on: {watch_dir}")
    logger.info(f"Output directory: {output_dir}")

    # Create directories if they don't exist
    Path(watch_dir).mkdir(parents=True, exist_ok=True)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    event_handler = WhisperFileHandler(output_dir)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("File watcher stopped")

    observer.join()


if __name__ == "__main__":
    main()
