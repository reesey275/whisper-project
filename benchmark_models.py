#!/usr/bin/env python3
"""
SAFE Whisper Model Performance Benchmark
Prevents WSL2 crashes by running one model at a time with memory monitoring
"""

import gc
import os
import sys
import time

import whisper

# Try to import psutil, install if not available
try:
    import psutil
except ImportError:
    print("Installing psutil for memory monitoring...")
    os.system("pip install psutil")
    import psutil


def get_memory_usage():
    """Get current memory usage in GB."""
    memory = psutil.virtual_memory()
    return {
        "used_gb": memory.used / (1024**3),
        "available_gb": memory.available / (1024**3),
        "percent": memory.percent,
    }


def safe_benchmark_model(model_name, audio_file, max_memory_gb=10):
    """Safely benchmark a specific model with memory monitoring."""

    # Check memory before starting
    mem_before = get_memory_usage()
    print(
        f"Testing {model_name}... (Mem: {mem_before['used_gb']:.1f}GB used, {mem_before['available_gb']:.1f}GB free)",
        end=" ",
    )
    sys.stdout.flush()

    # Skip if insufficient memory
    if mem_before["available_gb"] < 3.0:  # Need at least 3GB free
        print(f"⏭️ SKIPPED - Insufficient memory ({mem_before['available_gb']:.1f}GB free)")
        return {
            "model": model_name,
            "skipped": True,
            "reason": f'Insufficient memory: {mem_before["available_gb"]:.1f}GB free',
            "success": False,
        }

    try:
        # Force garbage collection before starting
        gc.collect()

        start_time = time.time()

        # Load model with timeout protection
        print("Loading...", end=" ")
        sys.stdout.flush()
        model = whisper.load_model(model_name)

        # Check memory after model load
        mem_loaded = get_memory_usage()
        if mem_loaded["percent"] > 90:  # Over 90% memory usage
            print("⚠️ HIGH MEMORY - Cleaning up and skipping")
            del model
            gc.collect()
            return {
                "model": model_name,
                "skipped": True,
                "reason": f'Memory too high after model load: {mem_loaded["percent"]:.1f}%',
                "success": False,
            }

        print("Transcribing...", end=" ")
        sys.stdout.flush()

        # Transcribe with minimal parameters to reduce memory usage
        result = model.transcribe(
            audio_file,
            language="en",
            verbose=False,
            word_timestamps=False,  # Reduce memory usage
            condition_on_previous_text=False,  # Reduce memory usage
        )

        end_time = time.time()
        processing_time = end_time - start_time

        text = result["text"].strip()
        text_length = len(text)

        # Calculate real-time factor
        audio_duration = 33.3  # Known duration of test file
        realtime_factor = audio_duration / processing_time if processing_time > 0 else 0

        # Clean up immediately
        del model
        del result
        gc.collect()

        mem_after = get_memory_usage()

        print(f"✅ {processing_time:.2f}s ({realtime_factor:.1f}x RT) [{text_length} chars]")

        return {
            "model": model_name,
            "processing_time": processing_time,
            "realtime_factor": realtime_factor,
            "text_length": text_length,
            "text": text,
            "memory_before_gb": mem_before["used_gb"],
            "memory_after_gb": mem_after["used_gb"],
            "success": True,
        }

    except Exception as e:
        print(f"❌ ERROR: {str(e)[:50]}...")
        # Clean up on error
        try:
            if "model" in locals():
                del model
        except:
            pass
        gc.collect()

        return {"model": model_name, "error": str(e), "success": False}


def main():
    audio_file = "input/clip_01HFH2CT9MX85PPV0DSMHWYTA5.mp4"

    if not os.path.exists(audio_file):
        print(f"Error: Audio file {audio_file} not found")
        return

    print("🎵 Whisper Model Performance Benchmark")
    print("=" * 60)
    print(f"📁 Audio file: {audio_file}")
    print("⏱️  Duration: 33.3 seconds")
    print("🌍 Language: English")
    print("=" * 60)
    print()

    # Models to benchmark (focusing on main models)
    models_to_test = ["tiny", "base", "small", "medium", "large-v3", "turbo"]

    results = []

    for model_name in models_to_test:
        result = safe_benchmark_model(model_name, audio_file)
        if result["success"]:
            results.append(result)

        # Wait between models to let system stabilize
        time.sleep(3)

        # Force garbage collection
        gc.collect()

    if not results:
        print("\n❌ No successful benchmarks completed")
        return

    # Print results table
    print("\n" + "=" * 85)
    print("📊 BENCHMARK RESULTS")
    print("=" * 85)
    print(f"{'Model':<12} {'Time (s)':<10} {'RT Factor':<12} {'Chars':<8} {'Memory (GB)':<12} {'Sample':<30}")
    print("-" * 85)

    for result in results:
        sample = result["text"][:25] + "..." if len(result["text"]) > 25 else result["text"]
        mem_usage = result.get("memory_after_gb", 0) - result.get("memory_before_gb", 0)
        print(
            f"{result['model']:<12} {result['processing_time']:<10.2f} {result['realtime_factor']:<12.1f} {result['text_length']:<8} {mem_usage:<12.1f} {sample:<30}"
        )

    # Performance recommendations
    print("\n🏆 PERFORMANCE ANALYSIS")
    print("-" * 40)

    if results:
        fastest = min(results, key=lambda x: x["processing_time"])
        highest_quality = max(results, key=lambda x: x["text_length"])
        most_efficient = max(results, key=lambda x: x["text_length"] / max(x["processing_time"], 0.1))

        print(f"⚡ Fastest: {fastest['model']} ({fastest['processing_time']:.1f}s, {fastest['realtime_factor']:.1f}x realtime)")
        print(f"🎯 Best Quality: {highest_quality['model']} ({highest_quality['text_length']} characters)")
        print(f"⚖️  Most Efficient: {most_efficient['model']} (best quality/time ratio)")

    # Print full transcriptions
    print("\n" + "=" * 85)
    print("📝 FULL TRANSCRIPTIONS (Quality Comparison)")
    print("=" * 85)

    for result in results:
        print(f"\n[{result['model'].upper()} Model - {result['text_length']} chars - {result['processing_time']:.1f}s]:")
        print(f"'{result['text']}'")
        print(f"Memory used: {result.get('memory_after_gb', 0) - result.get('memory_before_gb', 0):.1f}GB")


if __name__ == "__main__":
    main()
