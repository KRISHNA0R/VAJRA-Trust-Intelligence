"""Audio spoof (voice deepfake) detection adapter.

Uses the Dhwani multilingual spoof detector
(ayush2635/Dhwani-Multilingual-Deepfake-Audio-Detection-Model, MIT license,
vendored ONNX weights in models/audio_dhwani/):
  frontend XLS-R + AASIST backend, ONNX Runtime, 16 kHz mono input,
  scored in 3 s windows with per-window mean/variance normalization.

Output: index 0 = real (bonafide), 1 = fake (spoof).

We did NOT train this model; we only integrate it. Credit to the original author.
Validated 4/4 on real Hindi/English (FLEURS) vs TTS-synthesized Hindi/English
(MMS-TTS) — see audio_verify.py.
"""

import io
import logging
import os
import subprocess
import tempfile
from typing import Any, Dict, List

import numpy as np
import onnxruntime as ort
import soundfile as sf
from scipy.signal import resample_poly

logger = logging.getLogger(__name__)

TARGET_SR = 16000
WINDOW_SAMPLES = 48000  # 3 s windows, per model spec


class AudioSpoofAdapter:
    """Adapter for Dhwani voice spoof detection (ONNX, CPU)."""

    MODEL_NAME = "dhwani-spoof"

    def __init__(self, model_dir: str = "models/audio_dhwani"):
        self.model_dir = model_dir
        self.session = None
        self.input_name = None
        self._load_model()

    def _load_model(self):
        weights = os.path.join(self.model_dir, "best_model.onnx")
        if not os.path.isfile(weights):
            raise FileNotFoundError(
                f"Audio spoof model not found at {weights}. "
                "See README for download instructions."
            )
        logger.info(f"Loading audio spoof model from {weights}")
        self.session = ort.InferenceSession(
            weights, providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name
        logger.info("Audio spoof model loaded successfully")

    @staticmethod
    def _decode_audio(file_bytes: bytes, filename: str) -> tuple:
        """Decode arbitrary audio bytes to (mono float32 @16kHz, duration_sec)."""
        data, sr = None, None
        try:
            data, sr = sf.read(io.BytesIO(file_bytes), dtype="float32")
        except Exception:
            # Fallback: let FFmpeg handle containers soundfile can't (m4a/webm/...)
            with tempfile.NamedTemporaryFile(
                suffix=os.path.splitext(filename or "audio.bin")[1] or ".bin",
                delete=False,
            ) as src:
                src.write(file_bytes)
                src_path = src.name
            wav_path = src_path + ".wav"
            try:
                subprocess.run(
                    ["ffmpeg", "-y", "-i", src_path, "-ar", "16000",
                     "-ac", "1", wav_path],
                    check=True, capture_output=True,
                )
                data, sr = sf.read(wav_path, dtype="float32")
            finally:
                for p in (src_path, wav_path):
                    try:
                        os.remove(p)
                    except OSError:
                        pass
        if data is None:
            raise ValueError("Could not decode audio file")
        if data.ndim > 1:
            data = data.mean(axis=1).astype(np.float32)
        if sr != TARGET_SR:
            data = resample_poly(data, TARGET_SR, sr).astype(np.float32)
            sr = TARGET_SR
        return data, len(data) / sr

    def _score_window(self, segment: np.ndarray) -> float:
        """Return P(fake) for one 3 s window (model-spec preprocessing)."""
        if len(segment) < WINDOW_SAMPLES:
            segment = np.pad(segment, (0, WINDOW_SAMPLES - len(segment)))
        else:
            segment = segment[:WINDOW_SAMPLES]
        segment = (segment - segment.mean()) / np.sqrt(segment.var() + 1e-5)
        logits = self.session.run(
            None, {self.input_name: segment.astype(np.float32).reshape(1, -1)}
        )[0]
        shifted = logits - logits.max(axis=1, keepdims=True)
        exp = np.exp(shifted)
        return float((exp / exp.sum(axis=1, keepdims=True))[0][1])

    def analyze(self, file_bytes: bytes, filename: str,
                progress_callback=None) -> Dict[str, Any]:
        """Analyze an audio clip; returns verdict + per-window fake probabilities."""
        try:
            waveform, duration = self._decode_audio(file_bytes, filename)
        except Exception as e:
            return {"success": False, "model": self.MODEL_NAME,
                    "error": f"Audio decode failed: {e}"}
        if duration < 0.5:
            return {"success": False, "model": self.MODEL_NAME,
                    "error": "Audio too short (minimum 0.5 s)"}

        chunks: List[Dict[str, float]] = []
        idx = 0
        for start in range(0, len(waveform), WINDOW_SAMPLES):
            prob = self._score_window(waveform[start:start + WINDOW_SAMPLES])
            chunks.append({
                "chunk": idx,
                "start": round(start / TARGET_SR, 2),
                "end": round(min(start + WINDOW_SAMPLES,
                                 len(waveform)) / TARGET_SR, 2),
                "fake_prob": round(prob, 4),
            })
            idx += 1
            if progress_callback:
                progress_callback(
                    int(100 * min(start + WINDOW_SAMPLES, len(waveform))
                        / len(waveform)),
                    "Analyzing audio...", f"Scored window {idx}",
                )

        probs = [c["fake_prob"] for c in chunks]
        overall = float(np.mean(probs))
        verdict = "FAKE" if overall >= 0.5 else "REAL"
        return {
            "success": True,
            "model": self.MODEL_NAME,
            "model_name": "Dhwani Spoof Detector",
            "verdict": verdict,
            "fake_prob": round(overall, 4),
            "score": round(overall, 4),
            "confidence": round(abs(overall - 0.5) * 2, 4),
            "duration_sec": round(duration, 2),
            "num_chunks": len(chunks),
            "chunks": chunks,
        }

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": "Dhwani Spoof Detector",
            "model_type": "Voice spoof / audio deepfake detection (multilingual)",
            "architecture": "XLS-R frontend + AASIST backend (ONNX)",
            "device": "cpu",
            "labels": {"0": "real", "1": "fake"},
            "sample_rate": TARGET_SR,
            "languages": ["en", "hi", "ta", "te", "ml"],
        }
