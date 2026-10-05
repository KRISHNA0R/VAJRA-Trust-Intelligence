#!/usr/bin/env python
# tools/batch_predict.py
"""
Batch processing script for running frame-level detection on multiple videos.
Supports multi-GPU, parallel processing, and resume functionality.
"""

import os
import sys
import argparse
import glob
import subprocess
import itertools
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def list_videos(root, pattern=""):
    """List all video files in directory."""
    exts = (".mp4", ".mov", ".avi", ".mkv", ".webm")
    files = []
    for r, _, fs in os.walk(root):
        for f in fs:
            if f.lower().endswith(exts):
                if not pattern or pattern.lower() in f.lower():
                    files.append(os.path.join(r, f))
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(
        description="Batch processing for frame-level deepfake detection"
    )
    parser.add_argument("--input-dir", required=True,
                       help="Directory containing videos")
    parser.add_argument("--model", required=True,
                       help="Model key or weight filename")
    parser.add_argument("--ckpt", default="",
                       help="Optional checkpoint path")
    parser.add_argument("--fps", type=float, default=3,
                       help="Frame extraction rate (default: 3)")
    parser.add_argument("--threshold", type=float, default=0.5,
                       help="Detection threshold (default: 0.5)")
    parser.add_argument("--outdir", default="runs/image_infer",
                       help="Output directory (default: runs/image_infer)")
    parser.add_argument("--workers", type=int, default=2,
                       help="Number of parallel processes (default: 2)")
    parser.add_argument("--gpus", default="",
                       help="GPU IDs to use (e.g., '0,1' for multi-GPU)")
    parser.add_argument("--pattern", default="",
                       help="Only process videos matching this pattern")
    parser.add_argument("--overwrite", action="store_true",
                       help="Overwrite existing results (default: skip)")
    parser.add_argument("--save-vis", action="store_true",
                       help="Save visualization videos")
    
    args = parser.parse_args()
    
    # Find videos
    print(f"[batch] Scanning directory: {args.input_dir}")
    vids = list_videos(args.input_dir, args.pattern)
    
    if not vids:
        print("[batch] ERROR: No videos found")
        return 1
    
    print(f"[batch] Found {len(vids)} video(s)")
    
    # Parse GPU configuration
    gpu_ids = [g.strip() for g in args.gpus.split(",") if g.strip()]
    use_multi_gpu = len(gpu_ids) > 0
    
    if use_multi_gpu:
        print(f"[batch] Using GPUs: {', '.join(gpu_ids)}")
    else:
        print(f"[batch] Using single device (CPU or default GPU)")
    
    # Build base command
    base_cmd = [
        sys.executable, "tools/predict_frames.py",
        "--model", args.model,
        "--fps", str(args.fps),
        "--threshold", str(args.threshold),
        "--outdir", args.outdir,
    ]
    
    if args.ckpt:
        base_cmd += ["--ckpt", args.ckpt]
    
    if args.save_vis:
        base_cmd += ["--save-vis"]
    
    # Filter for resume functionality (skip if timeline.json exists)
    model_key = args.model.split(".pth")[0] if args.model.endswith(".pth") else args.model
    todo = []
    skipped = 0
    
    for v in vids:
        stem = os.path.splitext(os.path.basename(v))[0]
        odir = os.path.join(args.outdir, model_key, stem)
        done_flag = os.path.join(odir, "timeline.json")
        
        if not args.overwrite and os.path.exists(done_flag):
            skipped += 1
            continue
        
        todo.append(v)
    
    print(f"[batch] Videos to process: {len(todo)}")
    if skipped > 0:
        print(f"[batch] Skipped (already done): {skipped}")
    print(f"[batch] Workers: {args.workers}")
    
    if not todo:
        print("[batch] Nothing to do!")
        return 0
    
    # Process videos with parallel workers
    procs = set()
    idx = 0
    completed = 0
    failed = 0
    start_time = time.time()
    
    print(f"\n[batch] Starting batch processing...")
    print(f"{'='*80}\n")
    
    while idx < len(todo) or procs:
        # Launch new processes up to worker limit
        while len(procs) < args.workers and idx < len(todo):
            v = todo[idx]
            idx += 1
            
            cmd = base_cmd + ["--input", v]
            env = os.environ.copy()
            
            if use_multi_gpu:
                # Round-robin GPU assignment
                gpu_idx = (completed + failed) % len(gpu_ids)
                env["CUDA_VISIBLE_DEVICES"] = gpu_ids[gpu_idx]
            
            print(f"[batch] [{completed + failed + 1}/{len(todo)}] Starting: {os.path.basename(v)}")
            if use_multi_gpu:
                print(f"        Using GPU: {gpu_ids[gpu_idx]}")
            
            try:
                p = subprocess.Popen(
                    cmd, 
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                procs.add(p)
            except Exception as e:
                print(f"[batch] ERROR: Failed to start process: {e}")
                failed += 1
        
        # Check for completed processes
        done = set()
        for p in procs:
            if p.poll() is not None:
                done.add(p)
                if p.returncode == 0:
                    completed += 1
                else:
                    failed += 1
        
        procs -= done
        
        # Brief sleep to avoid busy waiting
        if procs:
            time.sleep(0.5)
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"[batch] Batch processing complete!")
    print(f"[batch] Completed: {completed}/{len(todo)}")
    if failed > 0:
        print(f"[batch] Failed: {failed}/{len(todo)}")
    print(f"[batch] Total time: {elapsed:.1f}s")
    print(f"[batch] Average time per video: {elapsed/len(todo):.1f}s")
    print(f"\n[batch] Results saved to: {args.outdir}/{model_key}/")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

