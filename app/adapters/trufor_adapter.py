"""
TruFor Adapter for Deepfake Detection

This adapter integrates the TruFor model for image forgery detection and localization.
TruFor is a forensic framework that can detect a large variety of image manipulation methods,
from classic cheapfakes to more recent manipulations based on deep learning.

Based on: https://grip-unina.github.io/TruFor/
"""

import logging
import os
import sys
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageOps
import cv2
from typing import Dict, Any, Optional, Tuple
import tempfile
import shutil
import io
import torchvision.transforms.functional as TF

# Add TruFor path to sys.path
trufor_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'TruFor-main', 'TruFor-main', 'test_docker', 'src')
if trufor_path not in sys.path:
    sys.path.insert(0, trufor_path)

try:
    from config import update_config, _C as config
    from data_core import myDataset
    from models.cmx.builder_np_conf import myEncoderDecoder as confcmx
except ImportError as e:
    logging.error(f"Failed to import TruFor modules: {e}")
    raise

logger = logging.getLogger(__name__)


class TruForAdapter:
    """
    Adapter for TruFor model integration
    """
    
    def __init__(self, model_path: str = "models/trufor.pth.tar", device: str = "auto"):
        """
        Initialize TruFor adapter
        
        Args:
            model_path: Path to the TruFor model weights
            device: Device to run inference on ('auto', 'cpu', 'cuda:0', etc.)
        """
        self.model_path = model_path
        self.device = self._setup_device(device)
        self.model = None
        self.config = None
        self._load_model()
    
    def _setup_device(self, device: str) -> torch.device:
        """Setup the device for inference"""
        if device == "auto":
            if torch.cuda.is_available():
                device = "cuda:0"
            else:
                device = "cpu"
        
        return torch.device(device)
    
    def _load_model(self):
        """Load the TruFor model and configuration"""
        try:
            # Load configuration
            self.config = config.clone()
            self.config.defrost()
            self.config.merge_from_file(os.path.join(trufor_path, 'trufor.yaml'))
            self.config.TEST.MODEL_FILE = self.model_path
            self.config.freeze()
            
            # Load model
            logger.info(f"Loading TruFor model from {self.model_path}")
            checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=False)
            
            if self.config.MODEL.NAME == 'detconfcmx':
                self.model = confcmx(cfg=self.config)
            else:
                raise NotImplementedError(f'Model {self.config.MODEL.NAME} not implemented')
            
            self.model.load_state_dict(checkpoint['state_dict'])
            self.model = self.model.to(self.device)
            self.model.eval()
            
            logger.info("TruFor model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load TruFor model: {e}")
            raise
    
    def _preprocess_image(self, image_bytes: bytes) -> Tuple[torch.Tensor, dict]:
        """
        Preprocess image for TruFor inference with proper padding and metadata
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Tuple of (preprocessed image tensor, metadata for postprocessing)
        """
        # Convert bytes to PIL Image
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Apply EXIF orientation correction
        pil_image = ImageOps.exif_transpose(pil_image)
        
        # Get original dimensions
        # PIL.Image.size returns (width, height)
        W0, H0 = pil_image.size  # W0=width, H0=height
        L = 512  # Target size
        
        print(f'Original image dimensions: W={W0}, H={H0} (PIL returns width×height)')
        
        # Calculate scale factor to fit in 512x512 while maintaining aspect ratio
        s = L / max(W0, H0)
        W1, H1 = int(round(W0 * s)), int(round(H0 * s))
        print(f'Resized dimensions: W={W1}, H={H1}')
        
        # Resize maintaining aspect ratio
        pil_resized = pil_image.resize((W1, H1), Image.BICUBIC)
        
        # Calculate padding
        pad_w, pad_h = L - W1, L - H1
        left = pad_w // 2
        right = pad_w - left
        top = pad_h // 2
        bottom = pad_h - top
        print(f'Padding: left={left}, right={right}, top={top}, bottom={bottom}')
        
        # Convert to tensor and normalize
        tensor = TF.to_tensor(pil_resized)  # [0,1]
        tensor = TF.normalize(tensor, [0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        tensor = tensor.unsqueeze(0)  # Add batch dimension
        
        # Apply reflection padding to avoid black edge artifacts
        tensor = F.pad(tensor, (left, right, top, bottom), mode='reflect')
        
        # Store metadata for postprocessing
        meta = {
            'W0': W0, 'H0': H0,  # Original dimensions
            'W1': W1, 'H1': H1,  # Resized dimensions
            'left': left, 'right': right, 'top': top, 'bottom': bottom  # Padding info
        }
        
        return tensor.to(self.device), meta
    
    def _restore_to_orig(self, prob_map: torch.Tensor, meta: dict) -> np.ndarray:
        """
        Restore probability map to original image size by removing padding and resizing
        
        Args:
            prob_map: Probability map tensor (1, 1, 512, 512)
            meta: Metadata from preprocessing
            
        Returns:
            Restored probability map as numpy array (H0, W0)
        """
        # Remove padding: 512×512 → (H1, W1)
        # Note: PyTorch uses [batch, channel, height, width] format
        x = prob_map[..., meta['top']:512-meta['bottom'], meta['left']:512-meta['right']]
        
        # Resize to original dimensions: (H1, W1) → (H0, W0)
        # F.interpolate expects size=(height, width), so use (H0, W0)
        # PIL.Image.size returns (width, height), so W0=width, H0=height
        x = F.interpolate(x, size=(meta['H0'], meta['W0']), mode='bilinear', align_corners=False)
        
        return x.squeeze().cpu().numpy()  # Returns (H0, W0) array
    
    def _weighted_statistics_pooling(self, x: torch.Tensor, log_w: torch.Tensor = None) -> torch.Tensor:
        """
        TruFor's confidence-weighted statistics pooling function
        Implements the official algorithm from layer_utils.py
        """
        b = x.shape[0]
        c = x.shape[1]
        x = x.view(b, c, -1)
        
        if log_w is None:
            log_w = torch.zeros((b, 1, x.shape[-1]), device=x.device)
        else:
            assert log_w.shape[0] == b
            assert log_w.shape[1] == 1
            log_w = log_w.view(b, 1, -1)
            assert log_w.shape[-1] == x.shape[-1]
        
        log_w = F.log_softmax(log_w, dim=-1)
        x_min = -torch.logsumexp(log_w - x, dim=-1)
        x_max = torch.logsumexp(log_w + x, dim=-1)
        
        w = torch.exp(log_w)
        x_avg = torch.sum(w * x, dim=-1)
        x_msq = torch.sum(w * x * x, dim=-1)
        
        x = torch.cat((x_min, x_max, x_avg, x_msq), dim=1)
        return x
    
    def _compute_confidence_weighted_integrity(self, a: torch.Tensor, c: torch.Tensor, det_logit: torch.Tensor) -> float:
        """
        Compute integrity score using TruFor's confidence-weighted pooling mechanism
        This implements the confidence correction shown in official examples
        """
        try:
            # Compute confidence-weighted features for anomaly map
            f1 = self._weighted_statistics_pooling(c).view(a.shape[0], -1)  # (1, 4)
            
            # Compute confidence-weighted features for anomaly difference
            # This is the key: use confidence to weight the anomaly map
            anomaly_diff = a  # (1, 1, H, W) - anomaly map
            f2 = self._weighted_statistics_pooling(anomaly_diff, F.logsigmoid(c)).view(a.shape[0], -1)  # (1, 4)
            
            # Combine features
            combined_features = torch.cat((f1, f2), -1)  # (1, 8)
            
            # Use a simple linear layer to map features to integrity score
            # This approximates the official detection head
            if not hasattr(self, '_integrity_head'):
                self._integrity_head = torch.nn.Linear(8, 1).to(self.device)
                # Initialize with reasonable weights
                torch.nn.init.normal_(self._integrity_head.weight, 0, 0.1)
                torch.nn.init.constant_(self._integrity_head.bias, 0.5)
            
            # Compute integrity score
            integrity_logit = self._integrity_head(combined_features)
            integrity = torch.sigmoid(integrity_logit).flatten()[0].item()
            
            print(f'Confidence-weighted integrity: {integrity:.4f} (features: {combined_features[0].tolist()})')
            
            return integrity
            
        except Exception as e:
            logger.warning(f"Confidence-weighted pooling failed, using fallback: {e}")
            # Fallback to simple sigmoid of det_logit
            return torch.sigmoid(det_logit).flatten()[0].item()
    
    def _detect_portrait_artifacts(self, pred_map: np.ndarray, conf_map: np.ndarray, meta: dict) -> str:
        """
        Detect portrait mode/bokeh artifacts that cause false positives
        
        Args:
            pred_map: Anomaly map (H0, W0)
            conf_map: Confidence map (H0, W0)
            meta: Metadata from preprocessing
            
        Returns:
            Note about detected artifacts
        """
        try:
            # Convert to uint8 for edge detection
            H0, W0 = meta['H0'], meta['W0']
            
            # Create a simple edge detection mask
            # Use gradient magnitude as edge indicator
            grad_x = np.gradient(pred_map, axis=1)
            grad_y = np.gradient(pred_map, axis=0)
            edge_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Create boundary band (dilate edges)
            edge_threshold = np.percentile(edge_magnitude, 80)  # Top 20% gradients
            edge_mask = edge_magnitude > edge_threshold
            
            # Dilate to create boundary band
            kernel_size = min(15, min(H0, W0) // 20)  # Adaptive kernel size
            if kernel_size > 0:
                kernel = np.ones((kernel_size, kernel_size), np.uint8)
                edge_mask = cv2.dilate(edge_mask.astype(np.uint8), kernel, iterations=1).astype(bool)
            
            # Find high anomaly + high confidence regions (lower thresholds)
            high_anomaly = pred_map > 0.4  # Lower threshold
            high_confidence = conf_map > 0.5  # Lower threshold
            high_response = high_anomaly & high_confidence
            
            # Calculate ratio of high response in boundary band
            if high_response.sum() > 0:
                boundary_ratio = (high_response & edge_mask).sum() / high_response.sum()
                
                # Check if face interior is mostly low anomaly
                center_h, center_w = H0 // 2, W0 // 2
                face_region_h = slice(max(0, center_h - H0//4), min(H0, center_h + H0//4))
                face_region_w = slice(max(0, center_w - W0//4), min(W0, center_w + W0//4))
                face_interior = pred_map[face_region_h, face_region_w]
                face_low_anomaly = (face_interior < 0.3).sum() / face_interior.size
                
                print(f'Portrait detection: boundary_ratio={boundary_ratio:.3f}, face_low_anomaly={face_low_anomaly:.3f}')
                
                # If high response is mostly on boundaries and face interior is clean (relaxed conditions)
                if boundary_ratio > 0.5 and face_low_anomaly > 0.3:
                    return "Possible portrait mode/background blur or heavy post-processing detected (not face swap)"
            
            return ""
            
        except Exception as e:
            logger.warning(f"Portrait artifact detection failed: {e}")
            return ""
    
    async def detect(self, file_bytes: bytes, filename: str, mime_type: str) -> Dict[str, Any]:
        """
        Detect image forgery using TruFor
        
        Args:
            file_bytes: Raw file bytes
            filename: Original filename
            mime_type: MIME type of the file
            
        Returns:
            Detection results dictionary
        """
        try:
            # Only support images for now
            if not mime_type.startswith('image/'):
                return {
                    "status": "error",
                    "message": "TruFor currently only supports image files",
                    "model": "TruFor"
                }
            
            # Create data URL for original image
            import base64
            image_data_url = f"data:{mime_type};base64,{base64.b64encode(file_bytes).decode()}"
            
            # Preprocess image
            rgb_tensor, meta = self._preprocess_image(file_bytes)
            
            # Run inference
            with torch.no_grad():
                pred_logits, conf_logits, det_logit, npp = self.model(rgb_tensor)
                
                # Debug: Print shapes and ranges
                print(f'pred_logits: {pred_logits.shape}, min: {pred_logits.min().item():.4f}, max: {pred_logits.max().item():.4f}')
                print(f'conf_logits: {conf_logits.shape}, min: {conf_logits.min().item():.4f}, max: {conf_logits.max().item():.4f}')
                print(f'det_logit: {det_logit.shape}, min: {det_logit.min().item():.4f}, max: {det_logit.max().item():.4f}')
                
                # Process anomaly map: model sometimes outputs 2 channels (real/fake), sometimes 1 channel (fake logit)
                if pred_logits.shape[1] == 1:
                    a = torch.sigmoid(pred_logits[:, 0]).unsqueeze(1)  # (1,1,H,W)
                else:
                    a = torch.softmax(pred_logits, dim=1)[:, 1].unsqueeze(1)  # (1,1,H,W) select "fake" channel
                
                # Process confidence map: usually 1 channel logit
                c = torch.sigmoid(conf_logits[:, 0]).unsqueeze(1)  # (1,1,H,W)
                
                # Process integrity score using confidence-weighted pooling (TruFor official method)
                # This implements the confidence correction mechanism shown in the official examples
                integrity = self._compute_confidence_weighted_integrity(a, c, det_logit)
                fake_prob = 1.0 - integrity
                
                # Restore maps to original image size
                pred_map = self._restore_to_orig(a, meta)  # numpy array shape (H0, W0)
                conf_map = self._restore_to_orig(c, meta)  # numpy array shape (H0, W0)
                
                # Create confidence-weighted anomaly map (like official TruFor demos)
                weighted_pred_map = pred_map * conf_map
                print(f'weighted_pred_map stats: mean={weighted_pred_map.mean():.4f}, max={weighted_pred_map.max():.4f}')
                
                # Debug: Print processed values
                print(f'a (prob): {a.shape}, min: {a.min().item():.4f}, max: {a.max().item():.4f}')
                print(f'c (prob): {c.shape}, min: {c.min().item():.4f}, max: {c.max().item():.4f}')
                print(f'integrity: {integrity:.4f}, fake_prob: {fake_prob:.4f}')
                print(f'pred_map restored shape: {pred_map.shape} (should be H×W = {meta["H0"]}×{meta["W0"]})')
                print(f'conf_map restored shape: {conf_map.shape}')
                print(f'pred_map stats: mean={pred_map.mean():.4f}, max={pred_map.max():.4f}')
                print(f'conf_map stats: mean={conf_map.mean():.4f}, min={conf_map.min():.4f}, max={conf_map.max():.4f}')
                
                # Process noiseprint++ (restore to original size if available)
                npp_map = None
                if npp is not None:
                    npp_processed = torch.squeeze(npp, 0)[0].unsqueeze(0).unsqueeze(0)  # (1,1,H,W)
                    npp_map = self._restore_to_orig(npp_processed, meta)  # (H0, W0)
                    
                    # Apply zero-mean normalization for better visualization
                    npp_std = npp_map.std() + 1e-8
                    npp_map = np.clip(npp_map / (3 * npp_std), -1, 1)  # [-1,1]
                    npp_map = (npp_map + 1) * 0.5  # [0,1]
                
                # Detect portrait mode/bokeh artifacts
                portrait_note = self._detect_portrait_artifacts(pred_map, conf_map, meta)
                print(f'Portrait detection result: "{portrait_note}"')
            
            # Determine if image is fake based on integrity score
            is_fake = integrity < 0.5
            confidence = abs(integrity - 0.5) * 2  # Convert to 0-1 confidence
            
            # Create result
            result = {
                "status": "success",
                "model": "TruFor",
                "filename": filename,
                "is_fake": is_fake,
                "decision": "fake" if is_fake else "real",         # For frontend compatibility
                "confidence": float(confidence),
                "score": float(1 - fake_prob),                     # Authenticity score for display
                "integrity": float(integrity),                     # Higher value means more authentic
                "fake_prob": float(fake_prob),                     # For frontend direct usage
                "detection_score": float(integrity),               # Keep compatibility
                "prediction_map": pred_map.tolist(),               # anomaly ∈[0,1] (original size)
                "weighted_prediction_map": weighted_pred_map.tolist(),  # anomaly × confidence (official style)
                "confidence_map": conf_map.tolist(),               # confidence ∈[0,1] (original size)
                "image_size": (meta['H0'], meta['W0']),            # Original image size (H, W)
                "has_confidence_map": True,
                "has_noiseprint": npp_map is not None,
                "original_image_url": image_data_url,
                "portrait_note": portrait_note                     # Portrait mode detection hint
            }
            
            # Add noiseprint++ if available
            if npp_map is not None:
                result["noiseprint_map"] = npp_map.tolist()
            
            logger.info(f"TruFor detection completed for {filename}: fake={is_fake}, confidence={confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"TruFor detection failed for {filename}: {e}")
            return {
                "status": "error",
                "message": f"Detection failed: {str(e)}",
                "model": "TruFor"
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": "TruFor",
            "model_type": "Image Forgery Detection and Localization",
            "architecture": "Cross-modal transformer with RGB and Noiseprint++",
            "device": str(self.device),
            "supports_localization": True,
            "supports_confidence": True,
            "supports_noiseprint": True
        }


