#!/usr/bin/env python
# tools/list_models.py
"""
List all available DeepfakeBench models and their status.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.weight_registry import WEIGHT_REGISTRY

DFB_WEIGHTS_DIR = "models/vendors/DeepfakeBench/training/weights"


def format_size(bytes_size):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def main():
    print("="*80)
    print("DeepfakeBench Models - Status Report")
    print("="*80)
    print()
    
    print(f"Weight directory: {DFB_WEIGHTS_DIR}")
    print()
    
    # Check each model
    models_found = 0
    models_missing = 0
    total_size = 0
    
    print(f"{'Model Key':<20} {'Weight File':<25} {'Size':<12} {'Input Size':<12} {'Status':<10}")
    print("-"*80)
    
    for weight_file, meta in sorted(WEIGHT_REGISTRY.items(), key=lambda x: x[1]['model_key']):
        model_key = meta['model_key']
        input_size = meta['input_size']
        weight_path = os.path.join(DFB_WEIGHTS_DIR, weight_file)
        
        if os.path.exists(weight_path):
            size = os.path.getsize(weight_path)
            size_str = format_size(size)
            status = "✓ Ready"
            models_found += 1
            total_size += size
        else:
            size_str = "N/A"
            status = "✗ Missing"
            models_missing += 1
        
        print(f"{model_key:<20} {weight_file:<25} {size_str:<12} {input_size}x{input_size:<7} {status:<10}")
    
    print("-"*80)
    print()
    print(f"Summary:")
    print(f"  Total models: {len(WEIGHT_REGISTRY)}")
    print(f"  Ready: {models_found}")
    print(f"  Missing: {models_missing}")
    print(f"  Total size: {format_size(total_size)}")
    print()
    
    if models_missing > 0:
        print("⚠️  Some models are missing. Please download the missing weight files.")
    else:
        print("✅ All models are ready for inference!")
    
    print()
    print("To run inference with a model:")
    print("  python tools/predict_frames.py --input <video> --model <model_key>")
    print()
    print("Example:")
    print("  python tools/predict_frames.py --input video.mp4 --model xception --fps 3")
    print()


if __name__ == "__main__":
    main()

