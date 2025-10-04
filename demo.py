#!/usr/bin/env python3
"""
Quick demo script showing how to use all three transcription methods.
This demonstrates the unified interface of our Whisper project.
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def demo_local_transcription():
    """Demo local transcription (without actual audio file)."""
    print("🎤 Local Whisper Transcription Demo")
    print("=" * 40)
    
    try:
        from local.transcribe_local import transcribe_file
        import whisper
        
        # Test that we can load a model
        models = whisper.available_models()
        print(f"✅ Local Whisper available with models: {', '.join(models[:3])}...")
        print("📝 Ready to transcribe audio files")
        print("   Usage: transcribe_file('/path/to/audio.mp3', model_name='tiny')")
        print()
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_docker_transcription():
    """Demo Docker-based transcription."""
    print("🐳 Docker Whisper Transcription Demo")
    print("=" * 40)
    
    try:
        from docker.transcribe_docker import DockerWhisperTranscriber
        
        # Test with standard whisper
        transcriber = DockerWhisperTranscriber(
            use_faster_whisper=False,
            default_model="tiny"
        )
        print(f"✅ Docker transcriber initialized (standard whisper)")
        print("📝 Ready to transcribe with Docker containers")
        print("   Usage: transcriber.transcribe('/path/to/audio.mp3')")
        
        # Test with faster whisper
        faster_transcriber = DockerWhisperTranscriber(
            use_faster_whisper=True,
            default_model="tiny"
        )
        print(f"✅ Faster-whisper transcriber initialized")
        print()
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_api_transcription():
    """Demo API-based transcription."""
    print("🔑 API Transcription Demo")
    print("=" * 40)
    
    try:
        # Check if API key is set
        env_file = project_root / '.env'
        api_key_configured = False
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
                if 'your_openai_api_key_here' in content:
                    print("⚠️  API key not configured (still using template values)")
                    print("   Add your OpenAI API key to .env file to use API transcription")
                else:
                    print("✅ API configuration appears to be set")
                    api_key_configured = True
        
        # Only try to initialize client if we have a real API key
        if api_key_configured or os.getenv('OPENAI_API_KEY'):
            from api.transcribe_api import OpenAIWhisperClient
            client = OpenAIWhisperClient()
            print("✅ API client initialized")
        else:
            print("✅ API client code available (needs API key to initialize)")
        
        print("📝 Ready to transcribe using OpenAI API (when API key is configured)")
        print("   Usage: client.transcribe('/path/to/audio.mp3')")
        print()
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_universal_interface():
    """Demo the universal transcription interface."""
    print("🌟 Universal Transcription Interface Demo")
    print("=" * 40)
    
    try:
        # Import the main transcription script
        import transcribe
        
        print("✅ Universal interface loaded")
        print("📝 This script automatically detects the best available method:")
        print("   1. Tries local Whisper first (fastest for repeated use)")
        print("   2. Falls back to Docker if local installation fails")
        print("   3. Uses API as final fallback")
        print()
        print("Usage examples:")
        print("  python transcribe.py audio.mp3")
        print("  python transcribe.py audio.mp3 --model medium --language en")
        print("  python transcribe.py audio.mp3 --method docker")
        print("  python transcribe.py audio.mp3 --method api")
        print()
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_next_steps():
    """Show next steps for the user."""
    print("🚀 Next Steps")
    print("=" * 40)
    print("1. 📁 Add audio files to transcribe")
    print("   - Supported formats: MP3, MP4, WAV, M4A, FLAC, OGG")
    print()
    print("2. 🔑 Configure API keys (optional)")
    print("   - Edit .env file with your OpenAI API key")
    print("   - Add other service keys as needed")
    print()
    print("3. 🎤 Start transcribing!")
    print("   - Local:  python local/transcribe_local.py your_audio.mp3")
    print("   - Docker: python docker/transcribe_docker.py your_audio.mp3")
    print("   - API:    python api/transcribe_api.py your_audio.mp3")
    print("   - Auto:   python transcribe.py your_audio.mp3")
    print()
    print("4. 📚 Read the documentation")
    print("   - Check README.md for detailed usage instructions")
    print("   - Explore all the advanced options and features")
    print()

def main():
    """Run the demo."""
    print("🎉 Whisper Project Demo")
    print("=" * 50)
    print("Welcome to your complete Whisper transcription project!")
    print("This demo shows all available transcription methods.")
    print("=" * 50)
    print()
    
    demos = [
        demo_local_transcription,
        demo_docker_transcription,
        demo_api_transcription,
        demo_universal_interface
    ]
    
    success_count = 0
    for demo in demos:
        try:
            if demo():
                success_count += 1
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        print()
    
    print("=" * 50)
    print(f"📊 Demo Summary: {success_count}/{len(demos)} components working")
    
    if success_count == len(demos):
        print("🎉 All components are working perfectly!")
    else:
        print("⚠️  Some components need attention - check the output above")
    
    print()
    show_next_steps()

if __name__ == "__main__":
    main()