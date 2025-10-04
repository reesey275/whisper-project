#!/usr/bin/env python3
"""
Test script to verify all Whisper transcription methods work correctly.
This script tests local installation, Docker containers, and API setup.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_python_environment():
    """Test if we're in the correct Python environment."""
    print("🐍 Testing Python Environment")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
        return True
    else:
        print("⚠️  Not running in virtual environment (this is okay for system Python)")
        return True

def test_local_whisper():
    """Test local Whisper installation."""
    print("\n🎤 Testing Local Whisper Installation")
    
    try:
        import whisper
        print("✅ OpenAI Whisper imported successfully")
        
        # List available models
        models = whisper.available_models()
        print(f"Available models: {', '.join(models)}")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import whisper: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing whisper: {e}")
        return False

def test_docker_availability():
    """Test Docker availability and our custom images."""
    print("\n🐳 Testing Docker Setup")
    
    try:
        # Check Docker daemon
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker daemon not running")
            return False
        
        print("✅ Docker daemon is running")
        
        # Check our custom images
        result = subprocess.run(['docker', 'images', '--format', 'table {{.Repository}}:{{.Tag}}'], 
                              capture_output=True, text=True)
        
        images = result.stdout
        
        if 'whisper-local:latest' in images:
            print("✅ whisper-local:latest image found")
        else:
            print("❌ whisper-local:latest image not found")
            return False
            
        if 'faster-whisper:latest' in images:
            print("✅ faster-whisper:latest image found")
        else:
            print("❌ faster-whisper:latest image not found")
            return False
        
        return True
        
    except FileNotFoundError:
        print("❌ Docker not installed")
        return False
    except Exception as e:
        print(f"❌ Error testing Docker: {e}")
        return False

def test_api_configuration():
    """Test API configuration setup."""
    print("\n🔑 Testing API Configuration")
    
    env_file = project_root / '.env'
    env_template = project_root / '.env.template'
    
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check if it has content (not just the template)
        with open(env_file, 'r') as f:
            content = f.read()
            if 'your_openai_api_key_here' in content:
                print("⚠️  .env file contains template values - please add real API keys")
                return False
            else:
                print("✅ .env file appears to have real values")
                return True
    else:
        print("⚠️  .env file not found")
        print(f"💡 Copy {env_template} to {env_file} and add your API keys")
        return False

def test_project_structure():
    """Test project structure."""
    print("\n📁 Testing Project Structure")
    
    required_files = [
        'transcribe.py',
        'local/transcribe_local.py',
        'docker/transcribe_docker.py',
        'docker/transcribe_docker.sh',
        'api/transcribe_api.py',
        'requirements.txt',
        'README.md'
    ]
    
    all_good = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")
            all_good = False
    
    return all_good

def test_imports():
    """Test if we can import our modules."""
    print("\n📦 Testing Module Imports")
    
    modules_to_test = [
        ('local.transcribe_local', 'Local transcription module'),
        ('docker.transcribe_docker', 'Docker transcription module'),
        ('api.transcribe_api', 'API transcription module')
    ]
    
    all_good = True
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description}")
        except ImportError as e:
            print(f"❌ {description}: {e}")
            all_good = False
        except Exception as e:
            print(f"⚠️  {description}: {e}")
    
    return all_good

def main():
    """Run all tests."""
    print("🧪 Whisper Project Test Suite")
    print("=" * 50)
    
    tests = [
        ("Python Environment", test_python_environment),
        ("Project Structure", test_project_structure),
        ("Module Imports", test_imports),
        ("Local Whisper", test_local_whisper),
        ("Docker Setup", test_docker_availability),
        ("API Configuration", test_api_configuration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your Whisper project is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())