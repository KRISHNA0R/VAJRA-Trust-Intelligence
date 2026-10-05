#!/usr/bin/env python
# tools/quick_compare.py
"""
Quick comparison of results from multiple models on the same video.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_timeline(timeline_path):
    """Load timeline.json file."""
    try:
        with open(timeline_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {timeline_path}: {e}")
        return None


def format_segments(segments):
    """Format segment list as string."""
    if not segments:
        return "None"
    
    result = []
    for start, end in segments:
        duration = end - start
        result.append(f"{start:.1f}s-{end:.1f}s ({duration:.1f}s)")
    
    return ", ".join(result)


def main():
    parser = argparse.ArgumentParser(
        description="Compare results from multiple models"
    )
    parser.add_argument("--results_dir", required=True,
                       help="Directory containing model results (e.g., runs/model_comparison)")
    parser.add_argument("--video", required=True,
                       help="Video name (e.g., input)")
    
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    video_name = args.video
    
    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        return 1
    
    print("="*100)
    print(f"Model Comparison Report - Video: {video_name}")
    print("="*100)
    print()
    
    # Collect all model results
    results = []
    
    for model_dir in results_dir.iterdir():
        if not model_dir.is_dir():
            continue
        
        timeline_path = model_dir / video_name / "timeline.json"
        
        if not timeline_path.exists():
            continue
        
        timeline = load_timeline(timeline_path)
        if timeline:
            results.append({
                'model': timeline.get('model', model_dir.name),
                'overall_score': timeline.get('overall_score', 0),
                'average_score': timeline.get('average_score', 0),
                'num_segments': timeline.get('num_suspicious_segments', 0),
                'segments': timeline.get('suspicious_segments', []),
                'total_frames': timeline.get('total_frames', 0),
                'threshold': timeline.get('threshold', 0)
            })
    
    if not results:
        print(f"No results found for video '{video_name}' in {results_dir}")
        return 1
    
    # Sort by overall score (descending)
    results.sort(key=lambda x: x['overall_score'], reverse=True)
    
    # Print table
    print(f"{'Model':<20} {'Overall':<10} {'Average':<10} {'Segments':<10} {'Frames':<10} {'Threshold':<10}")
    print("-"*100)
    
    for r in results:
        print(f"{r['model']:<20} {r['overall_score']:<10.4f} {r['average_score']:<10.4f} "
              f"{r['num_segments']:<10} {r['total_frames']:<10} {r['threshold']:<10.2f}")
    
    print("-"*100)
    print()
    
    # Detailed segments
    print("Suspicious Segments by Model:")
    print("-"*100)
    
    for r in results:
        print(f"\n{r['model']}:")
        if r['segments']:
            for i, (start, end) in enumerate(r['segments'], 1):
                duration = end - start
                print(f"  Segment {i}: {start:.2f}s - {end:.2f}s (duration: {duration:.2f}s)")
        else:
            print("  No suspicious segments detected")
    
    print()
    print("="*100)
    
    # Consensus analysis
    print("\nConsensus Analysis:")
    print("-"*100)
    
    models_detecting = sum(1 for r in results if r['num_segments'] > 0)
    avg_overall_score = sum(r['overall_score'] for r in results) / len(results)
    
    print(f"Models detecting suspicious content: {models_detecting}/{len(results)}")
    print(f"Average overall score: {avg_overall_score:.4f}")
    
    if models_detecting >= len(results) * 0.6:
        print("⚠️  Strong consensus: Multiple models detected suspicious content")
    elif models_detecting >= len(results) * 0.3:
        print("⚠️  Moderate consensus: Some models detected suspicious content")
    else:
        print("✓ Weak consensus: Few models detected suspicious content")
    
    print()


if __name__ == "__main__":
    sys.exit(main())

