# tools/predict_frames.py
"""
Frame-by-frame deepfake detection using DeepfakeBench models.
Processes videos to extract frames, run inference, and generate suspicious segment timelines.
"""

import os
import sys
import cv2
import json
import csv
import argparse
import time
import numpy as np
import torch
from pathlib import Path
from collections import deque

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our registry and model builder
from tools.weight_registry import WEIGHT_REGISTRY
from tools.build_dfbench_model import build_model_and_transforms

DFB_WEIGHTS_DIR = "models/vendors/DeepfakeBench/training/weights"


def load_checkpoint(model: torch.nn.Module, ckpt_path: str):
    """Load model weights from checkpoint file."""
    print(f"[INFO] Loading checkpoint: {ckpt_path}")
    checkpoint = torch.load(ckpt_path, map_location="cpu")
    
    # Handle different checkpoint formats
    if isinstance(checkpoint, dict):
        state_dict = checkpoint.get("state_dict") or checkpoint.get("model") or checkpoint
    else:
        state_dict = checkpoint
    
    # Load state dict
    missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
    
    if missing_keys:
        print(f"[WARN] Missing keys: {len(missing_keys)} keys")
        if len(missing_keys) <= 5:
            for key in missing_keys:
                print(f"  - {key}")
    
    if unexpected_keys:
        print(f"[WARN] Unexpected keys: {len(unexpected_keys)} keys")
        if len(unexpected_keys) <= 5:
            for key in unexpected_keys:
                print(f"  - {key}")
    
    print(f"[INFO] Checkpoint loaded successfully")


def ensure_directory(path):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def extract_frames(video_path, target_fps):
    """
    Extract frames from video at specified FPS.
    Yields: (frame_index, timestamp, rgb_frame)
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")
    
    source_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_step = max(int(round(source_fps / target_fps)), 1)
    
    frame_idx = 0
    output_idx = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_idx % frame_step == 0:
            timestamp = output_idx / target_fps
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            yield output_idx, timestamp, rgb_frame
            output_idx += 1
        
        frame_idx += 1
    
    cap.release()


def preprocess_frame(frame, input_size, transform_fn=None):
    """
    Preprocess a frame for model input.
    
    Args:
        frame: RGB numpy array
        input_size: Target size for the model
        transform_fn: Optional custom transform function
    
    Returns:
        PyTorch tensor ready for model input [1, C, H, W]
    """
    if transform_fn is not None:
        return transform_fn(frame)
    
    # Default preprocessing
    from torchvision import transforms
    
    default_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((input_size, input_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    tensor = default_transform(frame)
    return tensor.unsqueeze(0)  # Add batch dimension


def run_inference(model, frame_tensor, device):
    """
    Run model inference on a single frame.
    
    Returns:
        Probability of being fake (float between 0 and 1)
    """
    frame_tensor = frame_tensor.to(device)
    
    with torch.no_grad():
        # DeepfakeBench models expect dict input
        data_dict = {"image": frame_tensor}
        
        try:
            output = model(data_dict, inference=True)
        except TypeError:
            # Some models don't support inference flag
            try:
                output = model(data_dict)
            except (TypeError, KeyError):
                # Fallback: try direct tensor input
                output = model(frame_tensor)
        
        # Handle different output formats
        if isinstance(output, dict):
            # DeepfakeBench models return dict with 'prob' or 'cls' key
            logits = output.get("prob") or output.get("cls") or output.get("logits") or output.get("pred")
            if logits is None:
                # If no recognized key, try getting any tensor value
                for key, value in output.items():
                    if isinstance(value, torch.Tensor):
                        logits = value
                        break
        else:
            logits = output
        
        # Convert to probability
        if logits.dim() == 1:
            # Single sample: [2] or [1]
            if len(logits) == 2:
                prob = torch.softmax(logits, dim=0)[1].item()
            else:
                prob = torch.sigmoid(logits[0]).item()
        elif logits.shape[-1] == 2:
            # Binary classification: [batch, 2]
            prob = torch.softmax(logits, dim=1)[0, 1].item()
        elif logits.shape[-1] == 1:
            # Single output: [batch, 1]
            prob = torch.sigmoid(logits[0, 0]).item()
        else:
            # Multi-class: use last class as "fake"
            prob = torch.softmax(logits, dim=1)[0, -1].item()
        
        return prob


def smooth_scores(scores, window_size=5):
    """Apply moving average smoothing to scores."""
    if len(scores) < window_size:
        return scores
    
    scores_array = np.array(scores, dtype=np.float32)
    kernel = np.ones(window_size) / window_size
    smoothed = np.convolve(scores_array, kernel, mode='same')
    
    return smoothed.tolist()


def find_suspicious_segments(scores, timestamps, threshold=0.5, min_duration=1.0):
    """
    Find continuous segments where score exceeds threshold.
    
    Args:
        scores: List of fake probabilities
        timestamps: List of corresponding timestamps
        threshold: Minimum score to be considered suspicious
        min_duration: Minimum segment duration in seconds
    
    Returns:
        List of [start_time, end_time] segments
    """
    segments = []
    in_segment = False
    segment_start = 0
    
    for i, (score, ts) in enumerate(zip(scores, timestamps)):
        if not in_segment and score >= threshold:
            # Start new segment
            in_segment = True
            segment_start = i
        elif in_segment and score < threshold:
            # End current segment
            in_segment = False
            duration = timestamps[i-1] - timestamps[segment_start]
            if duration >= min_duration:
                segments.append([timestamps[segment_start], timestamps[i-1]])
    
    # Handle segment that extends to end of video
    if in_segment:
        duration = timestamps[-1] - timestamps[segment_start]
        if duration >= min_duration:
            segments.append([timestamps[segment_start], timestamps[-1]])
    
    return segments


def create_visualization_frame(rgb_frame, prob, timestamp, history, threshold, model_name, vis_w, vis_h):
    """
    Create a visualization frame with probability bar and sparkline.
    
    Args:
        rgb_frame: RGB frame from video
        prob: Current probability
        timestamp: Current timestamp
        history: Deque of recent probabilities
        threshold: Detection threshold
        model_name: Model name for display
        vis_w: Output width
        vis_h: Output height (including bar)
    
    Returns:
        BGR frame ready for video writer
    """
    bar_h = 48
    frame_h = vis_h - bar_h
    
    # Convert RGB to BGR and resize
    frm = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
    frm = cv2.resize(frm, (vis_w, frame_h))
    
    # Create canvas
    canvas = np.zeros((vis_h, vis_w, 3), dtype=np.uint8)
    canvas[:frame_h] = frm
    
    # Create probability bar at bottom
    bar = canvas[frame_h:vis_h]
    bar[:] = (30, 30, 30)  # Dark gray background
    
    # Draw probability-filled rectangle
    pw = int(prob * vis_w)
    # Color interpolation: green (low) -> red (high)
    c_low = np.array([60, 180, 60], dtype=np.float32)
    c_high = np.array([60, 60, 220], dtype=np.float32)
    color = (c_low + (c_high - c_low) * prob).astype(np.int32).tolist()
    cv2.rectangle(bar, (0, 4), (pw, bar_h - 4), color, -1)
    
    # Draw threshold line
    tx = int(threshold * vis_w)
    cv2.line(bar, (tx, 4), (tx, bar_h - 4), (200, 200, 200), 2)
    
    # Draw sparkline (recent probability history)
    if len(history) > 1:
        pts = []
        hh = bar_h - 10
        for j, p in enumerate(history):
            x = int(j / (len(history) - 1) * (vis_w - 1))
            y = int((1.0 - p) * (hh - 1)) + 5
            pts.append((x, y + frame_h))
        cv2.polylines(canvas, [np.array(pts, dtype=np.int32)], False, (235, 235, 235), 1, cv2.LINE_AA)
    
    # Add text overlays
    # Left: probability and timestamp
    mins = int(timestamp // 60)
    secs = int(timestamp % 60)
    cv2.putText(canvas, f"p_fake={prob:.3f}  t={mins:02d}:{secs:02d}",
                (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Right: model name and threshold
    cv2.putText(canvas, f"{model_name}  thr={threshold:.2f}",
                (vis_w - 320, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Draw red border if above threshold
    if prob >= threshold:
        cv2.rectangle(canvas, (6, 6), (vis_w - 6, frame_h - 6), (0, 0, 255), 2)
    
    return canvas


def to_srt_time(seconds):
    """Convert seconds to SRT timestamp format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_plot(scores_data, segments, threshold, output_path):
    """Generate probability vs time plot."""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        
        ts_arr = np.array([ts for _, ts, _ in scores_data], dtype=float)
        p_arr = np.array([p for _, _, p in scores_data], dtype=float)
        
        plt.figure(figsize=(10, 3))
        plt.plot(ts_arr, p_arr, label="Frame Probability", linewidth=1.5)
        plt.axhline(threshold, color='red', linestyle="--", label="Threshold", linewidth=1)
        
        # Shade suspicious segments
        for s, e in segments:
            plt.axvspan(s, e, alpha=0.15, color='red')
        
        plt.xlabel("Time (s)")
        plt.ylabel("P(fake)")
        plt.legend(loc="upper right")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        return True
    except Exception as e:
        print(f"[WARN] Failed to generate plot: {e}")
        return False


def generate_srt(segments, output_path):
    """Generate SRT subtitle file for suspicious segments."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            for idx, (start, end) in enumerate(segments, start=1):
                f.write(f"{idx}\n")
                f.write(f"{to_srt_time(start)} --> {to_srt_time(end)}\n")
                f.write("SUSPECT\n\n")
        return True
    except Exception as e:
        print(f"[WARN] Failed to generate SRT: {e}")
        return False


def generate_meta(output_path, model_key, checkpoint_path, input_size, fps, threshold, num_frames, elapsed, device):
    """Generate metadata file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"model={model_key}\n")
            f.write(f"ckpt={checkpoint_path}\n")
            f.write(f"input_size={input_size}\n")
            f.write(f"fps={fps}\n")
            f.write(f"threshold={threshold}\n")
            f.write(f"frames={num_frames}\n")
            f.write(f"device={device}\n")
            f.write(f"processing_time={elapsed:.2f}s\n")
        return True
    except Exception as e:
        print(f"[WARN] Failed to generate meta: {e}")
        return False


def process_video(video_path, model, input_size, transform_fn, args, device, model_name_pretty, checkpoint_path):
    """Process a single video and generate results."""
    video_name = Path(video_path).stem
    output_dir = os.path.join(args.outdir, args.model_name, video_name)
    ensure_directory(output_dir)
    
    csv_path = os.path.join(output_dir, "scores.csv")
    timeline_path = os.path.join(output_dir, "timeline.json")
    
    print(f"\n[INFO] Processing: {video_path}")
    print(f"[INFO] Output directory: {output_dir}")
    
    # Initialize visualization writer if needed
    vis_writer = None
    history = deque(maxlen=int(args.fps * 5))  # Keep last ~5 seconds of probabilities
    
    if args.save_vis:
        print(f"[INFO] Visualization enabled, will create vis.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        vis_w = 960
        vis_h = 540 + 48  # 48px for probability bar
        vis_path = os.path.join(output_dir, "vis.mp4")
        vis_writer = cv2.VideoWriter(vis_path, fourcc, args.fps, (vis_w, vis_h))
        
        if not vis_writer.isOpened():
            print(f"[WARN] Failed to open video writer, disabling visualization")
            vis_writer = None
    
    # Extract frames and run inference
    scores_data = []
    start_time = time.time()
    
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["frame_idx", "timestamp", "prob_fake"])
        
        for frame_idx, timestamp, rgb_frame in extract_frames(video_path, args.fps):
            # Preprocess
            frame_tensor = preprocess_frame(rgb_frame, input_size, transform_fn)
            
            # Inference
            prob_fake = run_inference(model, frame_tensor, device)
            
            # Save
            scores_data.append((frame_idx, timestamp, prob_fake))
            writer.writerow([frame_idx, f"{timestamp:.3f}", f"{prob_fake:.6f}"])
            
            # Update history for sparkline
            history.append(prob_fake)
            
            # Generate visualization frame if enabled
            if vis_writer is not None:
                vis_frame = create_visualization_frame(
                    rgb_frame, prob_fake, timestamp, history,
                    args.threshold, model_name_pretty, vis_w, vis_h
                )
                vis_writer.write(vis_frame)
            
            # Progress
            if (frame_idx + 1) % 10 == 0:
                print(f"  Processed {frame_idx + 1} frames...", end="\r")
    
    # Release video writer
    if vis_writer is not None:
        vis_writer.release()
        print(f"\n[INFO] Visualization saved to: {os.path.join(output_dir, 'vis.mp4')}")
    
    elapsed = time.time() - start_time
    print(f"\n[INFO] Completed: {len(scores_data)} frames in {elapsed:.1f}s")
    print(f"[INFO] Scores saved to: {csv_path}")
    
    # Generate timeline
    if len(scores_data) == 0:
        print("[WARN] No frames processed")
        return
    
    timestamps = [ts for _, ts, _ in scores_data]
    scores = [prob for _, _, prob in scores_data]
    
    # Smooth scores
    scores_smoothed = smooth_scores(scores, window_size=5)
    
    # Find suspicious segments
    segments = find_suspicious_segments(scores_smoothed, timestamps, 
                                       threshold=args.threshold, 
                                       min_duration=1.0)
    
    # Calculate overall metrics
    overall_score = float(np.max(scores_smoothed))
    avg_score = float(np.mean(scores))
    
    # Save timeline
    timeline_data = {
        "video": video_name,
        "model": args.model_name,
        "threshold": args.threshold,
        "total_frames": len(scores_data),
        "fps": args.fps,
        "overall_score": overall_score,
        "average_score": avg_score,
        "suspicious_segments": segments,
        "segments_sec": segments,  # Alias for compatibility
        "num_suspicious_segments": len(segments)
    }
    
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline_data, f, indent=2)
    
    print(f"[INFO] Timeline saved to: {timeline_path}")
    print(f"[INFO] Overall score: {overall_score:.4f}")
    print(f"[INFO] Found {len(segments)} suspicious segment(s)")
    
    for i, (start, end) in enumerate(segments, 1):
        print(f"  Segment {i}: {start:.2f}s - {end:.2f}s ({end-start:.2f}s)")
    
    # Generate additional outputs
    print(f"[INFO] Generating additional output files...")
    
    # 1. Plot
    plot_path = os.path.join(output_dir, "plot.png")
    if generate_plot(scores_data, segments, args.threshold, plot_path):
        print(f"[INFO] Plot saved to: {plot_path}")
    
    # 2. SRT subtitles
    srt_path = os.path.join(output_dir, "segments.srt")
    if generate_srt(segments, srt_path):
        print(f"[INFO] SRT subtitles saved to: {srt_path}")
    
    # 3. Metadata
    meta_path = os.path.join(output_dir, "meta.txt")
    if generate_meta(meta_path, args.model_name, checkpoint_path, input_size, 
                     args.fps, args.threshold, len(scores_data), elapsed, device):
        print(f"[INFO] Metadata saved to: {meta_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Frame-by-frame deepfake detection using DeepfakeBench models"
    )
    parser.add_argument("--input", required=True, 
                       help="Input video file or directory")
    parser.add_argument("--model", required=True,
                       help="Model key (e.g., 'xception') or weight filename (e.g., 'xception_best.pth')")
    parser.add_argument("--ckpt", default="",
                       help="Optional checkpoint path (overrides default)")
    parser.add_argument("--fps", type=float, default=3.0,
                       help="Frame extraction rate (default: 3)")
    parser.add_argument("--threshold", type=float, default=0.5,
                       help="Threshold for suspicious segments (default: 0.5)")
    parser.add_argument("--outdir", default="runs/image_infer",
                       help="Output directory (default: runs/image_infer)")
    parser.add_argument("--device", default="cuda",
                       help="Device to use (cuda/cpu, default: cuda)")
    parser.add_argument("--save-vis", "--save_vis", action="store_true", dest="save_vis",
                       help="Save visualization video with probability bar and sparkline")
    
    args = parser.parse_args()
    
    # Parse model and checkpoint
    if args.model.endswith(".pth"):
        # Model specified by weight filename
        weight_filename = os.path.basename(args.model)
        
        if weight_filename not in WEIGHT_REGISTRY:
            print(f"[ERROR] Unknown weight filename: {weight_filename}")
            print(f"[ERROR] Available weights: {list(WEIGHT_REGISTRY.keys())}")
            return
        
        meta = WEIGHT_REGISTRY[weight_filename]
        model_key = meta["model_key"]
        input_size = meta["input_size"]
        
        if os.path.isabs(args.model):
            checkpoint_path = args.model
        else:
            checkpoint_path = os.path.join(DFB_WEIGHTS_DIR, weight_filename)
    else:
        # Model specified by key
        model_key = args.model.lower()
        
        # Find corresponding weight file
        weight_filename = None
        for wf, meta in WEIGHT_REGISTRY.items():
            if meta["model_key"].lower() == model_key:
                weight_filename = wf
                input_size = meta["input_size"]
                break
        
        if not weight_filename:
            print(f"[ERROR] Unknown model key: {model_key}")
            print(f"[ERROR] Available models: {set(m['model_key'] for m in WEIGHT_REGISTRY.values())}")
            return
        
        checkpoint_path = args.ckpt or os.path.join(DFB_WEIGHTS_DIR, weight_filename)
    
    # Check if checkpoint exists
    if not os.path.exists(checkpoint_path):
        print(f"[ERROR] Checkpoint not found: {checkpoint_path}")
        return
    
    # Set device
    device = args.device if torch.cuda.is_available() and args.device == "cuda" else "cpu"
    print(f"[INFO] Using device: {device}")
    
    # Store model name for output organization
    args.model_name = model_key
    model_name_pretty = model_key.upper()
    
    # Build model
    print(f"[INFO] Building model: {model_key}")
    print(f"[INFO] Input size: {input_size}x{input_size}")
    
    try:
        model, transform_fn = build_model_and_transforms(model_key)
    except Exception as e:
        print(f"[ERROR] Failed to build model: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Load checkpoint
    try:
        load_checkpoint(model, checkpoint_path)
    except Exception as e:
        print(f"[ERROR] Failed to load checkpoint: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Move to device and set eval mode
    model.to(device)
    model.eval()
    print(f"[INFO] Model ready for inference")
    
    # Collect video files
    video_files = []
    if os.path.isdir(args.input):
        print(f"[INFO] Scanning directory: {args.input}")
        for root, _, files in os.walk(args.input):
            for filename in files:
                if filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".webm")):
                    video_files.append(os.path.join(root, filename))
    else:
        if not os.path.exists(args.input):
            print(f"[ERROR] Input file not found: {args.input}")
            return
        video_files = [args.input]
    
    if not video_files:
        print("[ERROR] No video files found")
        return
    
    print(f"[INFO] Found {len(video_files)} video(s) to process")
    
    # Process each video
    for i, video_path in enumerate(video_files, 1):
        print(f"\n{'='*80}")
        print(f"[INFO] Video {i}/{len(video_files)}")
        try:
            process_video(video_path, model, input_size, transform_fn, args, device, 
                         model_name_pretty, checkpoint_path)
        except Exception as e:
            print(f"[ERROR] Failed to process {video_path}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*80}")
    print("[INFO] All videos processed!")
    print(f"[INFO] Results saved to: {args.outdir}/{args.model_name}/")


if __name__ == "__main__":
    main()

