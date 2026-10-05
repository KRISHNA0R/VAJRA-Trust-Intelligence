# tools/fuse_scores.py
"""
Fuse frame-level detection scores with video-level (VideoMAE) scores.
Implements temporal alignment and weighted fusion for improved detection.
"""

import os
import csv
import json
import argparse
import numpy as np
from pathlib import Path


def load_frame_scores(csv_path):
    """
    Load frame-level scores from CSV.
    Returns: List of (frame_idx, timestamp, prob_fake)
    """
    scores = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            frame_idx = int(row["frame_idx"])
            timestamp = float(row["timestamp"])
            prob_fake = float(row["prob_fake"])
            scores.append((frame_idx, timestamp, prob_fake))
    return scores


def load_videomae_scores(csv_path):
    """
    Load VideoMAE clip-level scores from CSV.
    Expected format: clip_start, clip_end, prob_fake (or similar)
    Returns: List of (start_time, end_time, prob_fake)
    """
    scores = []
    
    # Try to auto-detect column names
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        # Detect column names
        start_col = None
        end_col = None
        prob_col = None
        
        for col in fieldnames:
            col_lower = col.lower()
            if "start" in col_lower or "begin" in col_lower:
                start_col = col
            elif "end" in col_lower:
                end_col = col
            elif "prob" in col_lower or "score" in col_lower:
                prob_col = col
        
        if not all([start_col, end_col, prob_col]):
            raise ValueError(f"Cannot identify columns in {csv_path}. Found: {fieldnames}")
        
        # Read data
        for row in reader:
            start_time = float(row[start_col])
            end_time = float(row[end_col])
            prob_fake = float(row[prob_col])
            scores.append((start_time, end_time, prob_fake))
    
    return scores


def align_scores(frame_scores, videomae_scores):
    """
    Align frame-level and video-level scores by timestamp.
    
    For each frame, find the corresponding VideoMAE clip and return both scores.
    Returns: List of (timestamp, frame_prob, videomae_prob)
    """
    aligned = []
    
    for frame_idx, timestamp, frame_prob in frame_scores:
        # Find which VideoMAE clip this frame belongs to
        videomae_prob = None
        
        for start_time, end_time, clip_prob in videomae_scores:
            if start_time <= timestamp < end_time:
                videomae_prob = clip_prob
                break
        
        # If no matching clip, use neutral score (0.5) or skip
        if videomae_prob is None:
            # Use average of all clips as fallback
            videomae_prob = np.mean([prob for _, _, prob in videomae_scores])
        
        aligned.append((timestamp, frame_prob, videomae_prob))
    
    return aligned


def fuse_scores(aligned_scores, alpha=0.6):
    """
    Fuse frame and video scores with weighted average.
    
    Args:
        aligned_scores: List of (timestamp, frame_prob, videomae_prob)
        alpha: Weight for VideoMAE (1-alpha for frame scores)
    
    Returns:
        List of (timestamp, fused_prob)
    """
    fused = []
    
    for timestamp, frame_prob, videomae_prob in aligned_scores:
        fused_prob = alpha * videomae_prob + (1 - alpha) * frame_prob
        fused.append((timestamp, fused_prob))
    
    return fused


def smooth_scores(scores, window_size=5):
    """Apply moving average smoothing."""
    if len(scores) < window_size:
        return scores
    
    timestamps = [ts for ts, _ in scores]
    probs = np.array([prob for _, prob in scores], dtype=np.float32)
    
    kernel = np.ones(window_size) / window_size
    probs_smoothed = np.convolve(probs, kernel, mode='same')
    
    return list(zip(timestamps, probs_smoothed.tolist()))


def find_segments(scores, threshold=0.5, min_duration=1.0):
    """Find suspicious segments above threshold."""
    segments = []
    in_segment = False
    segment_start_idx = 0
    
    for i, (timestamp, prob) in enumerate(scores):
        if not in_segment and prob >= threshold:
            in_segment = True
            segment_start_idx = i
        elif in_segment and prob < threshold:
            in_segment = False
            start_ts = scores[segment_start_idx][0]
            end_ts = scores[i - 1][0]
            duration = end_ts - start_ts
            if duration >= min_duration:
                segments.append([start_ts, end_ts])
    
    # Handle segment extending to end
    if in_segment:
        start_ts = scores[segment_start_idx][0]
        end_ts = scores[-1][0]
        duration = end_ts - start_ts
        if duration >= min_duration:
            segments.append([start_ts, end_ts])
    
    return segments


def main():
    parser = argparse.ArgumentParser(
        description="Fuse frame-level and VideoMAE detection scores"
    )
    parser.add_argument("--frame_csv", required=True,
                       help="Path to frame scores CSV")
    parser.add_argument("--videomae_csv", required=True,
                       help="Path to VideoMAE scores CSV")
    parser.add_argument("--alpha", type=float, default=0.6,
                       help="Weight for VideoMAE scores (default: 0.6)")
    parser.add_argument("--threshold", type=float, default=0.55,
                       help="Threshold for suspicious segments (default: 0.55)")
    parser.add_argument("--out", required=True,
                       help="Output directory")
    parser.add_argument("--smooth-window", type=int, default=5,
                       help="Smoothing window size (default: 5)")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.out, exist_ok=True)
    
    print("[INFO] Loading scores...")
    
    # Load scores
    try:
        frame_scores = load_frame_scores(args.frame_csv)
        print(f"[INFO] Loaded {len(frame_scores)} frame scores")
    except Exception as e:
        print(f"[ERROR] Failed to load frame scores: {e}")
        return
    
    try:
        videomae_scores = load_videomae_scores(args.videomae_csv)
        print(f"[INFO] Loaded {len(videomae_scores)} VideoMAE clip scores")
    except Exception as e:
        print(f"[ERROR] Failed to load VideoMAE scores: {e}")
        return
    
    # Align scores
    print("[INFO] Aligning scores...")
    aligned = align_scores(frame_scores, videomae_scores)
    print(f"[INFO] Aligned {len(aligned)} timestamps")
    
    # Fuse scores
    print(f"[INFO] Fusing scores (alpha={args.alpha})...")
    fused = fuse_scores(aligned, alpha=args.alpha)
    
    # Smooth
    print(f"[INFO] Smoothing scores (window={args.smooth_window})...")
    fused_smooth = smooth_scores(fused, window_size=args.smooth_window)
    
    # Save fused scores to CSV
    fused_csv = os.path.join(args.out, "scores_fused.csv")
    with open(fused_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "prob_fake_fused"])
        for ts, prob in fused_smooth:
            writer.writerow([f"{ts:.3f}", f"{prob:.6f}"])
    
    print(f"[INFO] Fused scores saved to: {fused_csv}")
    
    # Find suspicious segments
    print(f"[INFO] Finding suspicious segments (threshold={args.threshold})...")
    segments = find_segments(fused_smooth, threshold=args.threshold, min_duration=1.0)
    
    # Calculate metrics
    probs = [prob for _, prob in fused_smooth]
    overall_score = float(np.max(probs))
    avg_score = float(np.mean(probs))
    
    # Save timeline
    timeline_data = {
        "fusion_method": "weighted_average",
        "alpha_videomae": args.alpha,
        "alpha_frame": 1 - args.alpha,
        "threshold": args.threshold,
        "overall_score": overall_score,
        "average_score": avg_score,
        "suspicious_segments": segments,
        "num_suspicious_segments": len(segments),
        "frame_scores_file": args.frame_csv,
        "videomae_scores_file": args.videomae_csv
    }
    
    timeline_path = os.path.join(args.out, "timeline_fused.json")
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=2)
    
    print(f"[INFO] Timeline saved to: {timeline_path}")
    print(f"\n[RESULTS]")
    print(f"  Overall score: {overall_score:.4f}")
    print(f"  Average score: {avg_score:.4f}")
    print(f"  Suspicious segments: {len(segments)}")
    
    for i, (start, end) in enumerate(segments, 1):
        print(f"    Segment {i}: {start:.2f}s - {end:.2f}s ({end-start:.2f}s)")
    
    print("\n[INFO] Fusion complete!")


if __name__ == "__main__":
    main()

