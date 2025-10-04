#!/usr/bin/env python3
"""
Queue Client - Submit jobs to the Redis queue and check results
"""
import os
import json
import uuid
import time
import redis
import argparse
from pathlib import Path

class WhisperQueueClient:
    def __init__(self, redis_url="redis://redis:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.queue_name = "whisper:jobs"
        self.result_prefix = "whisper:result:"
        
    def submit_job(self, file_path, output_dir=None, model="base"):
        """Submit a transcription job to the queue"""
        job_id = str(uuid.uuid4())
        
        job_data = {
            'job_id': job_id,
            'file_path': file_path,
            'output_dir': output_dir or '/app/output/queue-transcriptions',
            'model': model,
            'submitted_at': time.time()
        }
        
        # Add job to queue
        self.redis_client.rpush(self.queue_name, json.dumps(job_data))
        
        print(f"Job submitted: {job_id}")
        print(f"File: {file_path}")
        print(f"Model: {model}")
        
        return job_id
    
    def get_result(self, job_id):
        """Get the result of a job"""
        result_key = f"{self.result_prefix}{job_id}"
        result_data = self.redis_client.get(result_key)
        
        if result_data:
            return json.loads(result_data)
        return None
    
    def wait_for_result(self, job_id, timeout=300):
        """Wait for a job to complete"""
        print(f"Waiting for job {job_id} to complete...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.get_result(job_id)
            if result:
                return result
            time.sleep(2)
            
        return None
    
    def list_queue_status(self):
        """Show queue status"""
        queue_length = self.redis_client.llen(self.queue_name)
        print(f"Jobs in queue: {queue_length}")
        
        # Show recent results
        result_keys = self.redis_client.keys(f"{self.result_prefix}*")
        if result_keys:
            print(f"Recent results: {len(result_keys)}")
            for key in result_keys[:5]:  # Show latest 5
                result = json.loads(self.redis_client.get(key))
                print(f"  {result['job_id']}: {result['status']}")

def main():
    parser = argparse.ArgumentParser(description='Whisper Queue Client')
    parser.add_argument('command', choices=['submit', 'status', 'result', 'wait'])
    parser.add_argument('--file', help='File to transcribe')
    parser.add_argument('--job-id', help='Job ID to check')
    parser.add_argument('--model', default='base', help='Whisper model to use')
    parser.add_argument('--output-dir', help='Output directory')
    parser.add_argument('--redis-url', default='redis://redis:6379', help='Redis URL')
    
    args = parser.parse_args()
    
    client = WhisperQueueClient(args.redis_url)
    
    if args.command == 'submit':
        if not args.file:
            print("Error: --file is required for submit command")
            return
        job_id = client.submit_job(args.file, args.output_dir, args.model)
        
    elif args.command == 'status':
        client.list_queue_status()
        
    elif args.command == 'result':
        if not args.job_id:
            print("Error: --job-id is required for result command")
            return
        result = client.get_result(args.job_id)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("No result found")
            
    elif args.command == 'wait':
        if not args.job_id:
            print("Error: --job-id is required for wait command")
            return
        result = client.wait_for_result(args.job_id)
        if result:
            print("Job completed!")
            print(json.dumps(result, indent=2))
        else:
            print("Job timed out or failed")

if __name__ == "__main__":
    main()