#!/usr/bin/env python
# tools/aggregate_runs.py
"""
Aggregate results from multiple model runs into a summary CSV.
"""

import os
import sys
import json
import csv
import argparse
import glob
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate frame-level detection results into summary CSV"
    )
    parser.add_argument("--root", default="runs/image_infer",
                       help="Root directory containing model results (default: runs/image_infer)")
    parser.add_argument("--out", default="runs/summary.csv",
                       help="Output CSV file path (default: runs/summary.csv)")
    parser.add_argument("--verbose", action="store_true",
                       help="Print detailed progress")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.root):
        print(f"[aggregate] ERROR: Root directory not found: {args.root}")
        return 1
    
    print(f"[aggregate] Scanning directory: {args.root}")
    
    # Collect results
    rows = [["model", "video", "overall_score", "average_score", "segments", 
             "flagged_sec", "total_frames", "fps", "threshold", "dir"]]
    
    count = 0
    
    # Iterate through model directories
    for model_dir in sorted(glob.glob(os.path.join(args.root, "*"))):
        if not os.path.isdir(model_dir):
            continue
        
        model_name = os.path.basename(model_dir)
        
        # Iterate through video directories
        for video_dir in sorted(glob.glob(os.path.join(model_dir, "*"))):
            if not os.path.isdir(video_dir):
                continue
            
            timeline_path = os.path.join(video_dir, "timeline.json")
            
            if not os.path.exists(timeline_path):
                if args.verbose:
                    print(f"[aggregate] Skipping (no timeline): {video_dir}")
                continue
            
            try:
                with open(timeline_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                video_name = os.path.basename(video_dir)
                
                # Extract metrics
                overall_score = data.get("overall_score", 0.0)
                average_score = data.get("average_score", 0.0)
                segments = data.get("segments_sec", data.get("suspicious_segments", []))
                num_segments = len(segments)
                
                # Calculate total flagged duration
                flagged_duration = sum(end - start for start, end in segments)
                
                total_frames = data.get("total_frames", 0)
                fps = data.get("fps", 0.0)
                threshold = data.get("threshold", 0.0)
                
                rows.append([
                    model_name,
                    video_name,
                    f"{overall_score:.6f}",
                    f"{average_score:.6f}",
                    num_segments,
                    f"{flagged_duration:.2f}",
                    total_frames,
                    fps,
                    threshold,
                    video_dir
                ])
                
                count += 1
                
                if args.verbose:
                    print(f"[aggregate] Added: {model_name}/{video_name}")
                
            except Exception as e:
                print(f"[aggregate] ERROR processing {timeline_path}: {e}")
                continue
    
    # Write output CSV
    os.makedirs(os.path.dirname(args.out) if os.path.dirname(args.out) else ".", exist_ok=True)
    
    try:
        with open(args.out, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        print(f"\n[aggregate] Summary written to: {args.out}")
        print(f"[aggregate] Total entries: {count}")
        print(f"[aggregate] Total rows (including header): {len(rows)}")
        
        # Print statistics
        if count > 0:
            print(f"\n[aggregate] Statistics:")
            
            # Count by model
            models = {}
            for row in rows[1:]:
                model = row[0]
                models[model] = models.get(model, 0) + 1
            
            print(f"  Models processed:")
            for model, cnt in sorted(models.items()):
                print(f"    - {model}: {cnt} video(s)")
            
            # Overall score stats
            scores = [float(row[2]) for row in rows[1:]]
            if scores:
                print(f"\n  Overall scores:")
                print(f"    - Min: {min(scores):.4f}")
                print(f"    - Max: {max(scores):.4f}")
                print(f"    - Mean: {sum(scores)/len(scores):.4f}")
            
            # Flagged videos
            flagged = sum(1 for row in rows[1:] if int(row[4]) > 0)
            print(f"\n  Videos with suspicious segments: {flagged}/{count} ({100*flagged/count:.1f}%)")
        
        return 0
        
    except Exception as e:
        print(f"[aggregate] ERROR writing output: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

