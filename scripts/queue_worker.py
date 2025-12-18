#!/usr/bin/env python3
"""
Queue Worker - Processes transcription jobs from Redis queue
"""
import json
import logging
import os
import subprocess
import time
from pathlib import Path

import redis

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class WhisperQueueWorker:
    def __init__(self, redis_url="redis://redis:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.queue_name = "whisper:jobs"
        self.result_prefix = "whisper:result:"

    def process_job(self, job_data):
        """Process a single transcription job"""
        try:
            file_path = job_data["file_path"]
            output_dir = job_data.get("output_dir", "/app/output/queue-transcriptions")
            model = job_data.get("model", os.getenv("WHISPER_DEFAULT_MODEL", "base"))
            job_id = job_data["job_id"]

            logger.info(f"Processing job {job_id}: {file_path}")

            # Ensure output directory exists
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Build transcription command
            cmd = [
                "python",
                "/app/transcribe.py",
                file_path,
                "--output-dir",
                output_dir,
                "--model",
                model,
            ]

            # Run transcription
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Store result in Redis
            result_data = {
                "job_id": job_id,
                "status": "completed" if result.returncode == 0 else "failed",
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "timestamp": time.time(),
            }

            self.redis_client.setex(
                f"{self.result_prefix}{job_id}",
                3600,  # Keep results for 1 hour
                json.dumps(result_data),
            )

            if result.returncode == 0:
                logger.info(f"Job {job_id} completed successfully")
            else:
                logger.error(f"Job {job_id} failed: {result.stderr}")

            return result.returncode == 0

        except Exception as e:
            logger.error(f"Error processing job: {str(e)}")
            # Store error result
            error_data = {
                "job_id": job_data.get("job_id", "unknown"),
                "status": "error",
                "error": str(e),
                "timestamp": time.time(),
            }

            try:
                self.redis_client.setex(
                    f"{self.result_prefix}{job_data.get('job_id', 'unknown')}",
                    3600,
                    json.dumps(error_data),
                )
            except:
                pass

            return False

    def run(self):
        """Main worker loop"""
        logger.info("Whisper queue worker started")

        while True:
            try:
                # Block and wait for jobs (timeout 10 seconds)
                job = self.redis_client.blpop(self.queue_name, timeout=10)

                if job:
                    queue_name, job_data = job
                    job_data = json.loads(job_data)
                    self.process_job(job_data)
                else:
                    # No jobs available, continue waiting
                    logger.debug("No jobs available, waiting...")

            except KeyboardInterrupt:
                logger.info("Worker shutdown requested")
                break
            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                time.sleep(5)  # Wait before retrying

        logger.info("Whisper queue worker stopped")


def main():
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    worker = WhisperQueueWorker(redis_url)
    worker.run()


if __name__ == "__main__":
    main()
