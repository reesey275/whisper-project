#!/usr/bin/env python3
"""
OpenAI API Whisper Transcription Client

This script uses OpenAI's Transcription API for cloud-based audio transcription.
It's the fastest option with zero setup but requires an API key and internet connection.

Usage:
    python transcribe_api.py audio.mp3 --api-key your_api_key
    python transcribe_api.py video.mp4 --task translate --language en
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, List, Union
import json

try:
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI library not found. Install it with:")
    print("   pip install openai")
    sys.exit(1)


class OpenAIWhisperClient:
    """OpenAI API client for Whisper transcription."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass it as a parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
    
    def transcribe(self,
                   audio_path: Union[str, Path],
                   model: str = "whisper-1",
                   language: Optional[str] = None,
                   prompt: Optional[str] = None,
                   response_format: str = "json",
                   temperature: float = 0.0,
                   timestamp_granularities: Optional[List[str]] = None) -> Dict:
        """
        Transcribe an audio file using OpenAI's Whisper API.
        
        Args:
            audio_path: Path to the audio file
            model: Model to use (whisper-1 is the only option currently)
            language: Language of the input audio (optional)
            prompt: Optional text to guide the model's style
            response_format: Format of the response (json, text, srt, verbose_json, vtt)
            temperature: Sampling temperature (0.0 to 1.0)
            timestamp_granularities: List of timestamp granularities (word, segment)
            
        Returns:
            Dictionary containing transcription results
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Check file size (OpenAI limit is 25MB)
        file_size = audio_path.stat().st_size
        max_size = 25 * 1024 * 1024  # 25MB
        if file_size > max_size:
            raise ValueError(f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds OpenAI's 25MB limit")
        
        print(f"🎵 Transcribing: {audio_path.name}")
        print(f"📊 File size: {file_size / 1024 / 1024:.1f}MB")
        print(f"🤖 Model: {model}")
        print(f"🌍 Language: {language or 'auto-detect'}")
        
        start_time = time.time()
        
        try:
            with open(audio_path, 'rb') as audio_file:
                # Prepare transcription parameters
                transcription_params = {
                    "model": model,
                    "file": audio_file,
                    "response_format": response_format,
                    "temperature": temperature
                }
                
                if language:
                    transcription_params["language"] = language
                
                if prompt:
                    transcription_params["prompt"] = prompt
                
                if timestamp_granularities:
                    transcription_params["timestamp_granularities"] = timestamp_granularities
                
                # Make the API request
                response = self.client.audio.transcriptions.create(**transcription_params)
                
                transcription_time = time.time() - start_time
                print(f"✅ Transcription completed in {transcription_time:.2f} seconds")
                
                return {
                    "success": True,
                    "audio_file": str(audio_path),
                    "model": model,
                    "language": language,
                    "response_format": response_format,
                    "transcription_time": transcription_time,
                    "file_size_mb": file_size / 1024 / 1024,
                    "response": response
                }
                
        except Exception as e:
            return {
                "success": False,
                "audio_file": str(audio_path),
                "error": str(e),
                "transcription_time": time.time() - start_time
            }
    
    def translate(self,
                  audio_path: Union[str, Path],
                  model: str = "whisper-1",
                  prompt: Optional[str] = None,
                  response_format: str = "json",
                  temperature: float = 0.0) -> Dict:
        """
        Translate an audio file to English using OpenAI's Whisper API.
        
        Args:
            audio_path: Path to the audio file
            model: Model to use (whisper-1 is the only option currently)
            prompt: Optional text to guide the model's style
            response_format: Format of the response (json, text, srt, verbose_json, vtt)
            temperature: Sampling temperature (0.0 to 1.0)
            
        Returns:
            Dictionary containing translation results
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Check file size (OpenAI limit is 25MB)
        file_size = audio_path.stat().st_size
        max_size = 25 * 1024 * 1024  # 25MB
        if file_size > max_size:
            raise ValueError(f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds OpenAI's 25MB limit")
        
        print(f"🌐 Translating to English: {audio_path.name}")
        print(f"📊 File size: {file_size / 1024 / 1024:.1f}MB")
        print(f"🤖 Model: {model}")
        
        start_time = time.time()
        
        try:
            with open(audio_path, 'rb') as audio_file:
                # Make the API request
                response = self.client.audio.translations.create(
                    model=model,
                    file=audio_file,
                    prompt=prompt,
                    response_format=response_format,
                    temperature=temperature
                )
                
                translation_time = time.time() - start_time
                print(f"✅ Translation completed in {translation_time:.2f} seconds")
                
                return {
                    "success": True,
                    "audio_file": str(audio_path),
                    "model": model,
                    "response_format": response_format,
                    "translation_time": translation_time,
                    "file_size_mb": file_size / 1024 / 1024,
                    "response": response
                }
                
        except Exception as e:
            return {
                "success": False,
                "audio_file": str(audio_path),
                "error": str(e),
                "translation_time": time.time() - start_time
            }
    
    def save_response(self, result: Dict, output_dir: Optional[Union[str, Path]] = None) -> Dict[str, str]:
        """
        Save API response to files.
        
        Args:
            result: Result dictionary from transcribe() or translate()
            output_dir: Directory to save output files
            
        Returns:
            Dictionary mapping format types to file paths
        """
        if not result["success"]:
            raise ValueError("Cannot save failed transcription result")
        
        audio_path = Path(result["audio_file"])
        if output_dir is None:
            output_dir = audio_path.parent / "output"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        basename = audio_path.stem
        response = result["response"]
        response_format = result["response_format"]
        
        saved_files = {}
        
        if response_format == "json":
            # Save as JSON
            json_path = output_dir / f"{basename}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(response.model_dump() if hasattr(response, 'model_dump') else response, f, indent=2)
            saved_files["json"] = str(json_path)
            
            # Also save as text if available
            if hasattr(response, 'text'):
                text_path = output_dir / f"{basename}.txt"
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                saved_files["txt"] = str(text_path)
                
        elif response_format == "verbose_json":
            # Save as JSON with verbose information
            json_path = output_dir / f"{basename}_verbose.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(response.model_dump() if hasattr(response, 'model_dump') else response, f, indent=2)
            saved_files["json"] = str(json_path)
            
            # Also save as text
            if hasattr(response, 'text'):
                text_path = output_dir / f"{basename}.txt"
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                saved_files["txt"] = str(text_path)
        
        elif response_format == "text":
            # Save as plain text
            text_path = output_dir / f"{basename}.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(str(response))
            saved_files["txt"] = str(text_path)
            
        elif response_format == "srt":
            # Save as SRT subtitles
            srt_path = output_dir / f"{basename}.srt"
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(str(response))
            saved_files["srt"] = str(srt_path)
            
        elif response_format == "vtt":
            # Save as WebVTT subtitles
            vtt_path = output_dir / f"{basename}.vtt"
            with open(vtt_path, 'w', encoding='utf-8') as f:
                f.write(str(response))
            saved_files["vtt"] = str(vtt_path)
        
        return saved_files
    
    def batch_transcribe(self,
                        input_dir: Union[str, Path],
                        output_dir: Optional[Union[str, Path]] = None,
                        language: Optional[str] = None,
                        response_format: str = "json",
                        file_patterns: List[str] = None) -> List[Dict]:
        """
        Batch transcribe multiple audio files.
        
        Args:
            input_dir: Directory containing audio files
            output_dir: Directory to save output files
            language: Language code
            response_format: Format of the response
            file_patterns: List of file patterns to match
            
        Returns:
            List of transcription results
        """
        if file_patterns is None:
            file_patterns = ['*.mp3', '*.mp4', '*.wav', '*.m4a', '*.flac', '*.ogg']
        
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
        total_cost_estimate = 0.0
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n📁 Processing {i}/{len(audio_files)}: {audio_file.name}")
            
            # Estimate cost (approximate)
            file_size_mb = audio_file.stat().st_size / 1024 / 1024
            estimated_cost = file_size_mb * 0.006  # $0.006 per minute (rough estimate)
            total_cost_estimate += estimated_cost
            
            result = self.transcribe(
                audio_path=audio_file,
                language=language,
                response_format=response_format
            )
            
            if result["success"]:
                # Save the result
                saved_files = self.save_response(result, output_dir)
                result["saved_files"] = saved_files
                print(f"✅ Completed: {audio_file.name}")
                for format_type, file_path in saved_files.items():
                    print(f"   📄 {format_type.upper()}: {file_path}")
            else:
                print(f"❌ Failed: {audio_file.name} - {result.get('error', 'Unknown error')}")
            
            results.append(result)
        
        successful = sum(1 for r in results if r["success"])
        print(f"\n🎉 Batch processing complete: {successful}/{len(results)} files processed successfully")
        print(f"💰 Estimated total cost: ${total_cost_estimate:.2f}")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="OpenAI API Whisper transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python transcribe_api.py audio.mp3
  python transcribe_api.py video.mp4 --language en --response-format srt
  python transcribe_api.py podcast.wav --task translate --output-dir ./transcripts
  python transcribe_api.py --batch ./input --response-format verbose_json

Environment Variables:
  OPENAI_API_KEY: Your OpenAI API key (required)

Response Formats:
  json          - JSON with text only
  verbose_json  - JSON with timestamps and metadata
  text          - Plain text only
  srt           - SRT subtitle format
  vtt           - WebVTT subtitle format
        """
    )
    
    parser.add_argument("audio_file", nargs='?', help="Path to audio file or directory (for batch)")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--language", "-l", default="en", help="Language code (default: en for English)")
    parser.add_argument("--task", "-t", default="transcribe", 
                       choices=["transcribe", "translate"],
                       help="Task to perform (default: transcribe)")
    parser.add_argument("--response-format", "-f", default="json",
                       choices=["json", "text", "srt", "verbose_json", "vtt"],
                       help="Response format (default: json)")
    parser.add_argument("--output-dir", "-o", help="Output directory")
    parser.add_argument("--temperature", type=float, default=0.0,
                       help="Sampling temperature (0.0-1.0, default: 0.0)")
    parser.add_argument("--prompt", help="Optional prompt to guide the model")
    parser.add_argument("--batch", "-b", action="store_true", 
                       help="Batch process directory")
    parser.add_argument("--timestamps", action="store_true",
                       help="Include word-level timestamps (verbose_json format only)")
    
    args = parser.parse_args()
    
    if not args.audio_file:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Initialize client
        client = OpenAIWhisperClient(api_key=args.api_key)
        
        if args.batch:
            # Batch processing
            results = client.batch_transcribe(
                input_dir=args.audio_file,
                output_dir=args.output_dir,
                language=args.language,
                response_format=args.response_format
            )
            
            # Print summary
            successful = sum(1 for r in results if r["success"])
            total_time = sum(r.get("transcription_time", 0) for r in results)
            print(f"\n📊 Summary:")
            print(f"   Files processed: {successful}/{len(results)}")
            print(f"   Total time: {total_time:.2f} seconds")
            
        else:
            # Single file processing
            timestamp_granularities = None
            if args.timestamps and args.response_format == "verbose_json":
                timestamp_granularities = ["word"]
            
            if args.task == "transcribe":
                result = client.transcribe(
                    audio_path=args.audio_file,
                    language=args.language,
                    response_format=args.response_format,
                    temperature=args.temperature,
                    prompt=args.prompt,
                    timestamp_granularities=timestamp_granularities
                )
            else:  # translate
                result = client.translate(
                    audio_path=args.audio_file,
                    response_format=args.response_format,
                    temperature=args.temperature,
                    prompt=args.prompt
                )
            
            if result["success"]:
                # Save the result
                saved_files = client.save_response(result, args.output_dir)
                
                print(f"\n✅ {args.task.capitalize()} completed successfully!")
                print(f"⏱️  Processing time: {result.get('transcription_time', result.get('translation_time', 0)):.2f} seconds")
                print(f"📊 File size: {result['file_size_mb']:.1f}MB")
                print(f"📂 Output files:")
                for format_type, file_path in saved_files.items():
                    print(f"   {format_type.upper()}: {file_path}")
                
                # Print text preview if available
                response = result["response"]
                if hasattr(response, 'text') and len(response.text) > 0:
                    preview = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    print(f"\n📝 Preview:")
                    print(f"   {preview}")
                
            else:
                print(f"❌ {args.task.capitalize()} failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
                
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()