# DeepfakeBench Frame-Level Detection Tools

This toolset allows you to perform frame-by-frame deepfake detection on videos using multiple DeepfakeBench models.

## 📁 File Descriptions

- **`weight_registry.py`**: Maps weight files to model configurations
- **`build_dfbench_model.py`**: Factory class for automatically loading and building models
- **`predict_frames.py`**: Main inference script for frame-by-frame video analysis
- **`fuse_scores.py`**: Script for fusing single-frame scores with VideoMAE scores

## 🚀 Quick Start

### 1. Verify Weight Files

Confirm that weight files are placed in the correct location:

```bash
ls models/vendors/DeepfakeBench/training/weights/
```

You should see the following files:
- `xception_best.pth`
- `meso4_best.pth`
- `meso4Incep_best.pth`
- `f3net_best.pth`
- `effnb4_best.pth`
- `capsule_best.pth`
- `srm_best.pth`
- `recce_best.pth`
- `spsl_best.pth`
- `ffd_best.pth`
- `ucf_best.pth`
- `cnnaug_best.pth`
- `core_best.pth`

### 2. Run Single Video Inference

Analyze a video using the Xception model:

```bash
python tools/predict_frames.py \
  --input data/jobs/job_440557d4147f_1760275209/input.mp4 \
  --model xception \
  --fps 3 \
  --threshold 0.6 \
  --device cuda
```

**Parameter Descriptions:**
- `--input`: Path to video file or directory containing videos
- `--model`: Model name (e.g., `xception`) or weight filename (e.g., `xception_best.pth`)
- `--fps`: Frame extraction rate (default: 3fps)
- `--threshold`: Threshold for suspicious segments (default: 0.5)
- `--device`: Device to use (`cuda` or `cpu`)
- `--outdir`: Output directory (default: `runs/image_infer`)

### 3. Batch Process Multiple Videos

```bash
python tools/predict_frames.py \
  --input data/jobs/ \
  --model f3net \
  --fps 2 \
  --threshold 0.55
```

### 4. Try Different Models

#### Xception (High Accuracy, Slower)
```bash
python tools/predict_frames.py --input video.mp4 --model xception
```

#### MesoNet (Fast, Lightweight)
```bash
python tools/predict_frames.py --input video.mp4 --model meso4
```

#### EfficientNet-B4 (Balanced)
```bash
python tools/predict_frames.py --input video.mp4 --model efficientnetb4
```

#### F3Net (Frequency Domain Analysis)
```bash
python tools/predict_frames.py --input video.mp4 --model f3net
```

## 📊 Output Files

Two files are generated for each video:

### `scores.csv`
Frame-by-frame detection scores:
```csv
frame_idx,timestamp,prob_fake
0,0.000,0.234567
1,0.333,0.456789
2,0.667,0.678901
...
```

### `timeline.json`
Summary information and suspicious segments:
```json
{
  "video": "video_name",
  "model": "xception",
  "threshold": 0.6,
  "total_frames": 150,
  "overall_score": 0.8523,
  "average_score": 0.4321,
  "suspicious_segments": [
    [5.2, 12.8],
    [45.6, 58.3]
  ],
  "num_suspicious_segments": 2
}
```

## 🔗 Fusing VideoMAE Scores

If you already have VideoMAE analysis results, you can fuse them together to improve accuracy:

```bash
python tools/fuse_scores.py \
  --frame_csv runs/image_infer/xception/video_name/scores.csv \
  --videomae_csv runs/videomae/video_name/scores.csv \
  --alpha 0.6 \
  --threshold 0.55 \
  --out runs/fused/xception_videomae/video_name
```

**Parameter Descriptions:**
- `--frame_csv`: Frame model scores file
- `--videomae_csv`: VideoMAE scores file
- `--alpha`: VideoMAE weight (0.6 means 60% VideoMAE + 40% frame model)
- `--threshold`: Post-fusion threshold
- `--out`: Output directory

**Output Files:**
- `scores_fused.csv`: Fused frame-by-frame scores
- `timeline_fused.json`: Fused suspicious segments

## 🎯 Supported Models

| Model | model_key | Input Size | Features |
|------|-----------|----------|------|
| Xception | `xception` | 299x299 | High accuracy, deep network |
| MesoNet-4 | `meso4` | 256x256 | Lightweight and fast |
| MesoNet-4 Inception | `meso4Inception` | 256x256 | Improved MesoNet |
| F3Net | `f3net` | 224x224 | Frequency domain analysis |
| EfficientNet-B4 | `efficientnetb4` | 380x380 | Efficient and balanced |
| Capsule Net | `capsule_net` | 128x128 | Capsule network |
| SRM | `srm` | 299x299 | Spatial Rich Model |
| RECCE | `recce` | 224x224 | Relationship-aware |
| SPSL | `spsl` | 224x224 | Self-supervised learning |
| UCF | `ucf` | 256x256 | Unified contrastive learning |
| CNN-AUG | `multi_attention` | 224x224 | Multi-attention mechanism |
| CORE | `core` | 224x224 | Core features |

## 🔧 Advanced Usage

### Specify Custom Weight File

```bash
python tools/predict_frames.py \
  --input video.mp4 \
  --model xception \
  --ckpt /path/to/custom_weights.pth
```

### Adjust FPS and Threshold

```bash
# Higher FPS (more detailed but slower)
python tools/predict_frames.py --input video.mp4 --model xception --fps 5

# Lower threshold (more sensitive detection)
python tools/predict_frames.py --input video.mp4 --model xception --threshold 0.4
```

### CPU Mode (When No GPU Available)

```bash
python tools/predict_frames.py \
  --input video.mp4 \
  --model meso4 \
  --device cpu
```

## 📈 Performance Recommendations

### Speed Optimization
1. Use lower FPS (e.g., 2-3) for initial screening
2. Choose lightweight models (MesoNet, Capsule) for fast processing
3. Use GPU for batch processing

### Accuracy Optimization
1. Use multiple models for ensemble
2. Increase FPS to 5-10 for critical videos
3. Fuse with VideoMAE scores
4. Adjust threshold based on specific scenarios

### Recommended Combinations
- **Quick Screening**: MesoNet-4 @ 2fps
- **Standard Detection**: F3Net @ 3fps
- **High Accuracy**: Xception + VideoMAE fusion @ 5fps
- **Lightweight Deployment**: Capsule Net @ 2fps

## 🐛 Troubleshooting

### Issue: Model Not Found

```
[ERROR] Cannot locate detector builder for model_key='xxx'
```

**Solution:**
1. Check if model name is correct (refer to supported models table)
2. Confirm DeepfakeBench code is complete
3. Check if `models/vendors/DeepfakeBench/training/detectors/` contains corresponding `xxx_detector.py`

### Issue: Weight Loading Failed

```
[ERROR] Failed to load checkpoint
```

**Solution:**
1. Confirm weight file exists and is complete
2. Check if weight file corresponds to correct model
3. Try re-downloading weight file

### Issue: CUDA Out of Memory

```
RuntimeError: CUDA out of memory
```

**Solution:**
1. Reduce FPS
2. Use smaller model (e.g., MesoNet, Capsule)
3. Use CPU mode: `--device cpu`

### Issue: Cannot Open Video

```
[ERROR] Failed to open video
```

**Solution:**
1. Confirm video file is complete and format is supported
2. Try converting video format using ffmpeg
3. Check if file path is correct

## 📝 Example Workflow

### Complete Detection Workflow

```bash
# 1. Initial screening with fast model
python tools/predict_frames.py \
  --input data/jobs/ \
  --model meso4 \
  --fps 2 \
  --threshold 0.5 \
  --outdir runs/quick_scan

# 2. Use high-accuracy model for suspicious videos
python tools/predict_frames.py \
  --input suspicious_video.mp4 \
  --model xception \
  --fps 5 \
  --threshold 0.6 \
  --outdir runs/detailed_scan

# 3. If VideoMAE results available, perform fusion
python tools/fuse_scores.py \
  --frame_csv runs/detailed_scan/xception/video/scores.csv \
  --videomae_csv runs/videomae/video/scores.csv \
  --alpha 0.6 \
  --threshold 0.55 \
  --out runs/final_result/video
```

## 🔗 Related Resources

- [DeepfakeBench GitHub](https://github.com/SCLBD/DeepfakeBench)
- Project Documentation: `../README.md`
- Weight Download Guide: `../docs/guides/WEIGHTS_DOWNLOAD_GUIDE.md`

## 📄 License

Follows the license requirements of DeepfakeBench and this project.
