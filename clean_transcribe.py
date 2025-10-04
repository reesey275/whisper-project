#!/usr/bin/env python3
"""
Clean Whisper Transcription Tool

A simple, organized transcription interface that produces clean,
well-organized outputs without directory chaos.

Usage:
    python clean_transcribe.py audio.mp4                    # Production transcription
    python clean_transcribe.py audio.mp4 --dev              # Development/testing
    python clean_transcribe.py audio.mp4 --model medium     # Specify model
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import shutil

class CleanTranscriber:
    """Clean, organized transcription with proper file management"""
    
    def __init__(self):
        self.base_dir = Path("output")
        self.production_dir = self.base_dir / "production"
        self.development_dir = self.base_dir / "development" 
        self.archive_dir = self.base_dir / "archive"
        
        # Ensure clean directories exist
        for dir_path in [self.production_dir, self.development_dir, self.archive_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_clean_output_path(self, audio_file, mode="production", model="small"):
        """Generate clean, organized output path"""
        audio_path = Path(audio_file)
        base_name = audio_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Choose directory based on mode
        if mode == "development":
            output_dir = self.development_dir
            # For dev, use simple names
            filename_base = f"{base_name}_{model}"
        else:
            output_dir = self.production_dir
            # For production, include timestamp
            filename_base = f"{base_name}_{model}_{timestamp}"
        
        return output_dir, filename_base
    
    def transcribe(self, audio_file, model="small", language="en", mode="production"):
        """
        Perform clean transcription with organized output
        
        Args:
            audio_file: Path to audio/video file
            model: Whisper model (small, base, medium, large)
            language: Language code (en, es, fr, etc.)
            mode: Output mode (production or development)
            
        Returns:
            Dictionary with transcription results and file paths
        """
        print(f"🎵 Clean Transcription Starting...")
        print(f"📁 File: {Path(audio_file).name}")
        print(f"🤖 Model: {model}")
        print(f"🌍 Language: {language}")
        print(f"📂 Mode: {mode}")
        print("=" * 50)
        
        # Get organized output path
        output_dir, filename_base = self.get_clean_output_path(audio_file, mode, model)
        
        # Use the existing transcribe.py but with clean output
        cmd = [
            sys.executable, "transcribe.py",
            str(audio_file),
            "--model", model,
            "--language", language,
            "--output-dir", str(output_dir)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Find the generated files and rename them cleanly
            generated_files = list(output_dir.glob(f"{Path(audio_file).stem}*"))
            clean_files = {}
            
            for file_path in generated_files:
                if file_path.suffix == '.txt':
                    new_path = output_dir / f"{filename_base}.txt"
                    shutil.move(str(file_path), str(new_path))
                    clean_files['txt'] = str(new_path)
                elif file_path.suffix == '.srt':
                    new_path = output_dir / f"{filename_base}.srt"
                    shutil.move(str(file_path), str(new_path))
                    clean_files['srt'] = str(new_path)
                elif file_path.suffix == '.vtt':
                    new_path = output_dir / f"{filename_base}.vtt"
                    shutil.move(str(file_path), str(new_path))
                    clean_files['vtt'] = str(new_path)
            
            print(f"\n✅ Transcription completed successfully!")
            print(f"📂 Output directory: {output_dir}")
            print(f"📄 Files created:")
            for fmt, path in clean_files.items():
                print(f"   {fmt.upper()}: {Path(path).name}")
            
            # Show content preview
            if 'txt' in clean_files:
                with open(clean_files['txt'], 'r', encoding='utf-8') as f:
                    content = f.read()
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(f"\n📝 Content preview:")
                    print(f"   {preview}")
            
            return {
                'success': True,
                'files': clean_files,
                'output_dir': str(output_dir),
                'model': model,
                'mode': mode
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Transcription failed: {e}")
            print(f"Error output: {e.stderr}")
            return {'success': False, 'error': str(e)}
    
    def list_transcriptions(self, mode="production"):
        """List all transcriptions in organized manner"""
        if mode == "development":
            search_dir = self.development_dir
        else:
            search_dir = self.production_dir
            
        txt_files = list(search_dir.glob("*.txt"))
        
        if not txt_files:
            print(f"📁 No transcriptions found in {mode} directory")
            return []
        
        print(f"📁 {mode.title()} Transcriptions:")
        print("=" * 40)
        
        transcriptions = []
        for txt_file in sorted(txt_files):
            # Parse filename for info
            parts = txt_file.stem.split('_')
            if len(parts) >= 2:
                base_name = '_'.join(parts[:-1]) if len(parts) > 2 else parts[0]
                model = parts[-1]
                
                size = txt_file.stat().st_size
                modified = datetime.fromtimestamp(txt_file.stat().st_mtime)
                
                print(f"📄 {txt_file.name}")
                print(f"   Model: {model} | Size: {size} bytes | Modified: {modified.strftime('%Y-%m-%d %H:%M')}")
                
                transcriptions.append({
                    'file': str(txt_file),
                    'name': base_name,
                    'model': model,
                    'size': size,
                    'modified': modified
                })
        
        return transcriptions

def main():
    parser = argparse.ArgumentParser(
        description="Clean Whisper Transcription Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python clean_transcribe.py audio.mp4                    # Production transcription
  python clean_transcribe.py audio.mp4 --dev              # Development mode  
  python clean_transcribe.py audio.mp4 --model medium     # Use medium model
  python clean_transcribe.py --list                       # List transcriptions
  python clean_transcribe.py --list --dev                 # List dev transcriptions
        """
    )
    
    parser.add_argument("audio_file", nargs='?', help="Audio/video file to transcribe")
    parser.add_argument("--model", "-m", default="small", 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper model (default: small)")
    parser.add_argument("--language", "-l", default="en",
                       help="Language code (default: en)")
    parser.add_argument("--dev", action="store_true",
                       help="Development mode (simpler filenames)")
    parser.add_argument("--list", action="store_true",
                       help="List existing transcriptions")
    
    args = parser.parse_args()
    
    transcriber = CleanTranscriber()
    
    if args.list:
        mode = "development" if args.dev else "production"
        transcriber.list_transcriptions(mode)
    elif args.audio_file:
        mode = "development" if args.dev else "production"
        result = transcriber.transcribe(
            args.audio_file, 
            model=args.model,
            language=args.language,
            mode=mode
        )
        
        if not result['success']:
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()