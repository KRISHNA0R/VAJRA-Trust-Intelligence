"""
DeepfakeBench Adapter for Web API
Provides unified interface for 12 DeepfakeBench models
"""

import os
import sys
import logging
import cv2
import json
import numpy as np
import torch
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import deque

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tools.weight_registry import WEIGHT_REGISTRY
from tools.build_dfbench_model import build_model_and_transforms

logger = logging.getLogger(__name__)


class DeepfakeBenchAdapter:
    """Adapter for DeepfakeBench models with video analysis and visualization."""
    
    # Available models
    AVAILABLE_MODELS = {
        "xception": {"name": "Xception", "speed": "Medium", "accuracy": "High"},
        "meso4": {"name": "MesoNet-4", "speed": "Fast", "accuracy": "Medium"},
        "f3net": {"name": "F3Net", "speed": "Medium", "accuracy": "High"},
        "efficientnetb4": {"name": "EfficientNet-B4", "speed": "Medium", "accuracy": "High"},
        "capsule_net": {"name": "Capsule Net", "speed": "Very Fast", "accuracy": "Medium"},
        "recce": {"name": "RECCE", "speed": "Medium", "accuracy": "High"},
        "spsl": {"name": "SPSL", "speed": "Medium", "accuracy": "High"},
        "ucf": {"name": "UCF", "speed": "Medium", "accuracy": "High"},
        "multi_attention": {"name": "CNN-AUG", "speed": "Medium", "accuracy": "High"},
        "core": {"name": "CORE", "speed": "Medium", "accuracy": "High"},
        "srm": {"name": "SRM", "speed": "Medium", "accuracy": "High"},
        "meso4Inception": {"name": "MesoNet-4 Inception", "speed": "Fast", "accuracy": "Medium"},
    }
    
    def __init__(self, model_key: str = "xception", device: str = "cuda"):
        """
        Initialize DeepfakeBench adapter.
        
        Args:
            model_key: Model identifier (e.g., 'xception', 'meso4')
            device: Device to use ('cuda' or 'cpu')
        """
        self.model_key = model_key
        self.device = device if torch.cuda.is_available() and device == "cuda" else "cpu"
        self.model = None
        self.transform_fn = None
        self.input_size = None
        self.weights_dir = "models/vendors/DeepfakeBench/training/weights"
        
        logger.info(f"Initializing DeepfakeBench adapter with model: {model_key}, device: {self.device}")
        self._load_model()
    
    def _load_model(self):
        """Load the specified DeepfakeBench model."""
        try:
            # Find weight file and input size
            weight_filename = None
            for wf, meta in WEIGHT_REGISTRY.items():
                if meta["model_key"] == self.model_key:
                    weight_filename = wf
                    self.input_size = meta["input_size"]
                    break
            
            if not weight_filename:
                raise ValueError(f"Unknown model key: {self.model_key}")
            
            weight_path = os.path.join(self.weights_dir, weight_filename)
            
            if not os.path.exists(weight_path):
                raise FileNotFoundError(f"Model weights not found: {weight_path}")
            
            # Build model
            logger.warning(f"🏗️ Building model: {self.model_key} (from weight file: {weight_filename})")
            self.model, self.transform_fn = build_model_and_transforms(self.model_key)
            
            # Load weights
            logger.warning(f"📦 Loading weights from: {weight_path}")
            checkpoint = torch.load(weight_path, map_location="cpu")
            
            if isinstance(checkpoint, dict):
                state_dict = checkpoint.get("state_dict") or checkpoint.get("model") or checkpoint
            else:
                state_dict = checkpoint
            
            self.model.load_state_dict(state_dict, strict=False)
            
            # Move to device and set eval mode
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Model {self.model_key} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _is_black_or_low_contrast(self, frame: np.ndarray) -> bool:
        """
        Detect if a frame is black or has very low contrast.
        These frames often cause false positives in deepfake detection.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Check mean brightness (black screen check)
        mean_brightness = np.mean(gray)
        if mean_brightness < 15:  # Very dark frame
            return True
        
        # Check contrast (std deviation of pixel values)
        contrast = np.std(gray)
        if contrast < 10:  # Very low contrast (uniform color)
            return True
        
        return False
    
    def _preprocess_frame(self, frame: np.ndarray) -> torch.Tensor:
        """Preprocess a single frame for inference."""
        if self.transform_fn is not None:
            return self.transform_fn(frame)
        
        # Default preprocessing
        from torchvision import transforms
        
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((self.input_size, self.input_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        tensor = transform(frame)
        return tensor.unsqueeze(0)
    
    # Add frame counter for debugging
    _frame_count = 0
    
    def _run_inference(self, frame_tensor: torch.Tensor) -> float:
        """Run inference on a single frame."""
        frame_tensor = frame_tensor.to(self.device)
        
        with torch.no_grad():
            # Some models (like UCF) require a label field during inference
            # Provide a dummy label (0 = real) for inference
            data_dict = {
                "image": frame_tensor,
                "label": torch.tensor([0], dtype=torch.long).to(self.device)
            }
            
            try:
                output = self.model(data_dict, inference=True)
            except TypeError:
                try:
                    output = self.model(data_dict)
                except (TypeError, KeyError):
                    output = self.model(frame_tensor)
            
            # Handle different output formats
            if isinstance(output, dict):
                # DEBUG: Print first frame output structure
                if DeepfakeBenchAdapter._frame_count == 0:
                    logger.warning(f"🔍 Model output keys: {output.keys()}")
                    for k, v in output.items():
                        if isinstance(v, torch.Tensor):
                            logger.warning(f"🔍   {k}: shape={v.shape}, value={v.cpu().numpy()}")
                
                # Try to get logits from known output keys (avoid using 'or' with tensors)
                logits = None
                for key in ["prob", "cls", "logits", "pred"]:
                    if key in output:
                        logits = output[key]
                        break
                
                # If still None, take the first tensor found
                if logits is None:
                    for key, value in output.items():
                        if isinstance(value, torch.Tensor):
                            logits = value
                            break
            else:
                logits = output
            
            # Increment frame count
            DeepfakeBenchAdapter._frame_count += 1
            
            # Convert to probability
            # Check if logits is already a probability (from xception's 'prob' output)
            if isinstance(output, dict) and 'prob' in output and 'cls' in output:
                # xception model returns: {'cls': logits, 'prob': fake_prob, 'feat': features}
                # where prob is already softmax(cls, dim=1)[:, 1] (i.e., Fake probability)
                prob = logits.item() if logits.dim() == 0 or (logits.dim() == 1 and len(logits) == 1) else logits[0].item()
                
                # DEBUG: Print first 10 frames with raw cls logits, and any frame > 80%
                if DeepfakeBenchAdapter._frame_count <= 10 or prob > 0.8:
                    raw_logits = output['cls'][0].cpu().numpy()
                    probs = torch.softmax(output['cls'], dim=1)[0]
                    logger.warning(f"🔍 Frame {DeepfakeBenchAdapter._frame_count} - Raw logits: {raw_logits}, Probs: [Real={probs[0]:.4f}, Fake={probs[1]:.4f}], Final prob={prob:.4f}")
            elif logits.dim() == 1:
                if len(logits) == 2:
                    probs = torch.softmax(logits, dim=0)
                    prob = probs[1].item()  # Probability of class 1 (fake)
                    # DEBUG: Print first 10 frames
                    if DeepfakeBenchAdapter._frame_count <= 10:
                        logger.warning(f"🔍 Frame {DeepfakeBenchAdapter._frame_count} - Logits: {logits.cpu().numpy()}, Probs: [Real={probs[0]:.4f}, Fake={probs[1]:.4f}]")
                else:
                    prob = torch.sigmoid(logits[0]).item()
            elif logits.shape[-1] == 2:
                probs = torch.softmax(logits, dim=1)[0]
                prob = probs[1].item()  # Probability of class 1 (fake)
                # DEBUG: Print first 10 frames
                if DeepfakeBenchAdapter._frame_count <= 10:
                    logger.warning(f"🔍 Frame {DeepfakeBenchAdapter._frame_count} - Raw logits: {logits[0].cpu().numpy()}, Probs: [Real={probs[0]:.4f}, Fake={probs[1]:.4f}]")
            elif logits.shape[-1] == 1:
                prob = torch.sigmoid(logits[0, 0]).item()
            else:
                prob = torch.softmax(logits, dim=1)[0, -1].item()
            
            return prob
    
    def analyze_video(self, video_path: str, fps: float = 3.0, threshold: float = 0.5, progress_callback=None) -> Dict:
        """
        Analyze a video and return detection results.
        
        Args:
            video_path: Path to video file
            fps: Frame sampling rate
            threshold: Detection threshold
            progress_callback: Optional callback function(progress, stage, message) for progress updates
        
        Returns:
            Dictionary with analysis results
        """
        logger.warning(f"🎬 STARTING VIDEO ANALYSIS WITH MODEL: {self.model_key.upper()}")
        logger.info(f"Analyzing video: {video_path}")
        
        # Reset frame counter for debugging
        DeepfakeBenchAdapter._frame_count = 0
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")
        
        source_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_step = max(int(round(source_fps / fps)), 1)
        
        scores = []
        frames_data = []  # Store frames for keyframe extraction
        frame_idx = 0
        output_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_step == 0:
                timestamp = output_idx / fps
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Check if frame is black or low contrast (common false positive trigger)
                is_anomalous = self._is_black_or_low_contrast(frame)
                
                # Preprocess and run inference
                frame_tensor = self._preprocess_frame(rgb_frame)
                prob = self._run_inference(frame_tensor)
                
                # Log if high-score frame is actually a black/low-contrast frame
                if is_anomalous and prob > 0.7:
                    logger.warning(f"🚫 Frame {output_idx} at {timestamp:.2f}s: Black/low-contrast frame with high score {prob:.4f} - will be excluded from overall score")
                
                scores.append({
                    "frame": output_idx,
                    "timestamp": timestamp,
                    "probability": prob,
                    "is_anomalous": is_anomalous  # Mark anomalous frames
                })
                
                # Store frame data for keyframe extraction
                frames_data.append({
                    "frame_bgr": frame.copy(),
                    "timestamp": timestamp,
                    "probability": prob,
                    "frame_idx": output_idx
                })
                
                output_idx += 1
                
                # Update progress every frame for short videos, every 3 frames for longer ones
                update_frequency = 1 if output_idx < 30 else 3
                if progress_callback and output_idx % update_frequency == 0:
                    # Progress from 30% to 80% during frame analysis
                    progress = 30 + int((frame_idx / total_frames) * 50)
                    progress_callback(progress, "Analyzing video...", f"Processed {output_idx} frames")
                    logger.debug(f"Progress update: {progress}% - Frame {output_idx}/{total_frames}")
            
            frame_idx += 1
        
        cap.release()
        
        # Update progress - frame analysis complete
        if progress_callback:
            progress_callback(80, "Analyzing results...", "Processing detection scores")
        
        # Analyze results
        if not scores:
            return {
                "success": False,
                "error": "No frames processed"
            }
        
        # Calculate metrics - exclude anomalous frames (black/low-contrast)
        valid_scores = [s for s in scores if not s.get("is_anomalous", False)]
        all_probs = [s["probability"] for s in scores]
        
        if len(valid_scores) > 0:
            valid_probs = [s["probability"] for s in valid_scores]
            overall_score = float(np.mean(valid_probs))  # Use average of valid frames only
            average_score = float(np.mean(valid_probs))
        else:
            # If all frames are anomalous (unlikely), fall back to all frames
            valid_probs = all_probs
            overall_score = float(np.mean(all_probs))
            average_score = float(np.mean(all_probs))
        
        max_score = float(np.max(all_probs))  # Keep max for debugging
        anomalous_count = len(scores) - len(valid_scores)
        
        # DEBUG: Print score statistics
        logger.warning(f"🔍 SCORE STATS - Total frames: {len(scores)}, Valid frames: {len(valid_scores)}, Anomalous: {anomalous_count}")
        logger.warning(f"🔍 SCORE STATS - Min: {np.min(all_probs):.4f}, Max: {max_score:.4f}, Mean (all): {np.mean(all_probs):.4f}")
        logger.warning(f"🔍 Overall Score (Valid frames avg): {overall_score:.4f} ({overall_score*100:.2f}%)")
        logger.warning(f"🔍 Max Score (single frame): {max_score:.4f} ({max_score*100:.2f}%)")
        
        # Find the frame with max score (for debugging)
        max_idx = np.argmax(all_probs)
        max_frame_info = scores[max_idx]
        logger.warning(f"🔍 MAX SCORE FRAME: Frame #{max_frame_info['frame']} at {max_frame_info['timestamp']:.2f}s = {max_frame_info['probability']:.4f} (Anomalous: {max_frame_info.get('is_anomalous', False)})")
        
        # Smooth scores (use all probabilities for timeline display)
        window = 5
        if len(all_probs) >= window:
            smoothed = np.convolve(all_probs, np.ones(window)/window, mode='same')
        else:
            smoothed = np.array(all_probs)
        
        # Update progress - finding segments
        if progress_callback:
            progress_callback(85, "Finding suspicious segments...", "Detecting anomalies")
        
        # Find suspicious segments
        segments = []
        in_segment = False
        segment_start = 0
        
        for i, prob in enumerate(smoothed):
            if not in_segment and prob >= threshold:
                in_segment = True
                segment_start = i
            elif in_segment and prob < threshold:
                in_segment = False
                start_ts = scores[segment_start]["timestamp"]
                end_ts = scores[i-1]["timestamp"]
                if end_ts - start_ts >= 1.0:  # Minimum 1 second
                    # Find peak frame in this segment
                    segment_probs = [scores[j]["probability"] for j in range(segment_start, i)]
                    peak_idx = segment_start + int(np.argmax(segment_probs))
                    
                    segments.append({
                        "start": start_ts,
                        "end": end_ts,
                        "duration": end_ts - start_ts,
                        "peak_score": float(smoothed[peak_idx]),
                        "peak_time": scores[peak_idx]["timestamp"],
                        "keyframe_idx": peak_idx
                    })
        
        if in_segment:
            start_ts = scores[segment_start]["timestamp"]
            end_ts = scores[-1]["timestamp"]
            if end_ts - start_ts >= 1.0:
                segment_probs = [scores[j]["probability"] for j in range(segment_start, len(scores))]
                peak_idx = segment_start + int(np.argmax(segment_probs))
                
                segments.append({
                    "start": start_ts,
                    "end": end_ts,
                    "duration": end_ts - start_ts,
                    "peak_score": float(smoothed[peak_idx]),
                    "peak_time": scores[peak_idx]["timestamp"],
                    "keyframe_idx": peak_idx
                })
        
        # Update progress - extracting keyframes
        if progress_callback:
            progress_callback(90, "Extracting keyframes...", f"Found {len(segments)} suspicious segments")
        
        # Save keyframes for suspicious segments
        keyframe_dir = os.path.join(os.path.dirname(video_path), "keyframes")
        os.makedirs(keyframe_dir, exist_ok=True)
        
        for i, segment in enumerate(segments):
            keyframe_idx = segment["keyframe_idx"]
            if keyframe_idx < len(frames_data):
                frame_bgr = frames_data[keyframe_idx]["frame_bgr"]
                keyframe_path = os.path.join(keyframe_dir, f"segment_{i+1}_keyframe.jpg")
                cv2.imwrite(keyframe_path, frame_bgr)
                segment["keyframe_path"] = f"keyframes/segment_{i+1}_keyframe.jpg"
                logger.info(f"Saved keyframe for segment {i+1} at {keyframe_path}")
        
        return {
            "success": True,
            "model": self.model_key,
            "model_name": self.AVAILABLE_MODELS.get(self.model_key, {}).get("name", self.model_key),
            "overall_score": overall_score,
            "average_score": average_score,
            "threshold": threshold,
            "total_frames": len(scores),
            "fps": fps,
            "suspicious_segments": segments,
            "frame_scores": scores,  # Return all scores for threshold adjustment
            "verdict": "FAKE" if overall_score >= threshold else "REAL",
            "confidence": overall_score
        }
    
    @classmethod
    def get_available_models(cls) -> List[Dict]:
        """Get list of available models with metadata."""
        models = []
        for key, info in cls.AVAILABLE_MODELS.items():
            # Check if weights exist
            weight_file = None
            for wf, meta in WEIGHT_REGISTRY.items():
                if meta["model_key"] == key:
                    weight_file = wf
                    break
            
            if weight_file:
                weight_path = os.path.join("models/vendors/DeepfakeBench/training/weights", weight_file)
                available = os.path.exists(weight_path)
            else:
                available = False
            
            models.append({
                "key": key,
                "name": info["name"],
                "speed": info["speed"],
                "accuracy": info["accuracy"],
                "available": available
            })
        
        return models

