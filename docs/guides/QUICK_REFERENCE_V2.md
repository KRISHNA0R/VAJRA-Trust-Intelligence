# 🎯 DeepfakeBench V2.0 Quick Reference

## 🚀 One-Line Commands to Get Started

### Single Video (with Complete Visualization)
```bash
python tools/predict_frames.py --input video.mp4 --model xception --fps 3 --save-vis
```

### Batch Processing (2 workers in parallel)
```bash
python tools/batch_predict.py --input-dir data/videos --model xception --workers 2
```

### Generate Summary Report
```bash
python tools/aggregate_runs.py
```

## 📁 Output Files Overview

```
runs/image_infer/<model>/<video>/
├── scores.csv       # Frame-by-frame scores
├── timeline.json    # Suspicious segments
├── plot.png        # 📊 Probability chart
├── segments.srt    # 📝 SRT subtitles
├── vis.mp4        # 🎬 Visualization video
└── meta.txt       # 📄 Metadata
```

## 🎬 Visualization Video Explanation

### Screen Layout
```
┌─────────────────────────────────────┐
│ p_fake=0.xxx  t=mm:ss    MODEL  0.6 │ ← Text info
│                                     │
│         Original video (960×540)     │
│                                     │
├─────────────────────────────────────┤
│ [████████████████░░░░░░░░░░░░░] │ | │ ← Probability bar
│  └── sparkline curve ──┘        ↑   │
└─────────────────────────────────────┘
                                Threshold line
```

### Color Explanation
- **Green**: Low probability (likely authentic)
- **Orange**: Medium probability
- **Red**: High probability (suspicious)
- **Red Border**: Current frame exceeds threshold

## 🔧 Common Command Templates

### Quick Screening (Lightweight Model)
```bash
python tools/batch_predict.py \
  --input-dir data/videos \
  --model meso4 \
  --fps 2 \
  --workers 4
```

### High Accuracy Detection (Powerful Model)
```bash
python tools/batch_predict.py \
  --input-dir data/videos \
  --model xception \
  --fps 5 \
  --threshold 0.6 \
  --workers 2 \
  --save-vis
```

### Multi-GPU Acceleration
```bash
python tools/batch_predict.py \
  --input-dir data/videos \
  --model xception \
  --gpus 0,1,2,3 \
  --workers 8
```

### Resume Processing (Skip Completed)
```bash
python tools/batch_predict.py \
  --input-dir data/videos \
  --model xception \
  --workers 3
  # Automatically skip videos with timeline.json
```

### Force Reprocess
```bash
python tools/batch_predict.py \
  --input-dir data/videos \
  --model xception \
  --workers 3 \
  --overwrite
```

### Pattern Filtering (Only Process Matching Files)
```bash
python tools/batch_predict.py \
  --input-dir data/videos \
  --pattern "suspect" \
  --model xception \
  --workers 2
```

## 📊 Summary Reports

### Basic Usage
```bash
python tools/aggregate_runs.py
# Output: runs/summary.csv
```

### Custom Output Path
```bash
python tools/aggregate_runs.py \
  --root runs/image_infer \
  --out my_report.csv
```

### Verbose Mode
```bash
python tools/aggregate_runs.py --verbose
```

### CSV Column Descriptions
| Column | Description |
|------|------|
| model | Model name |
| video | Video name |
| overall_score | Highest score |
| average_score | Average score |
| segments | Number of suspicious segments |
| flagged_sec | Total flagged duration (seconds) |
| total_frames | Total frames |
| fps | Sampling rate |
| threshold | Detection threshold |
| dir | Output directory |

## 🎯 Typical Workflows

### Workflow 1: Quick Batch Screening
```bash
# 1. Batch processing
python tools/batch_predict.py \
  --input-dir data/videos \
  --model meso4 \
  --workers 4

# 2. Generate summary
python tools/aggregate_runs.py

# 3. View runs/summary.csv
# 4. Filter videos with overall_score > 0.7
# 5. Re-analyze suspicious videos with powerful model
```

### Workflow 2: Multi-Model Comparison
```bash
# 1. Process with multiple models
python tools/batch_predict.py --input-dir data/videos --model xception --workers 2
python tools/batch_predict.py --input-dir data/videos --model f3net --workers 2
python tools/batch_predict.py --input-dir data/videos --model recce --workers 2

# 2. Aggregate all results
python tools/aggregate_runs.py --out runs/multi_model.csv

# 3. Compare single video
python tools/quick_compare.py \
  --results_dir runs/image_infer \
  --video video_name
```

### Workflow 3: High-Quality Complete Analysis
```bash
# 1. High FPS + visualization
python tools/predict_frames.py \
  --input important_video.mp4 \
  --model xception \
  --fps 5 \
  --threshold 0.6 \
  --save-vis

# 2. View output
# - plot.png: View probability curve
# - vis.mp4: Watch visualization video
# - segments.srt: Load into player
# - timeline.json: View detection results
```

## 📝 Using SRT Subtitles

### VLC Player
1. Rename `segments.srt` to match video filename
2. Place in same directory
3. Open video to see subtitles

### MPV Player
```bash
mpv video.mp4 --sub-file=segments.srt
```

### Browser
```html
<video controls>
  <source src="video.mp4" type="video/mp4">
  <track src="segments.srt" kind="subtitles" default>
</video>
```

## 🔍 Results Analysis

### View Single Video Results
```bash
# All files are here
cd runs/image_infer/xception/video_name/

# View metadata
cat meta.txt

# View timeline
cat timeline.json

# View chart
open plot.png  # Mac
start plot.png # Windows

# Watch visualization
vlc vis.mp4
```

### View Batch Summary
```bash
# Open with Excel/LibreOffice
# Or view from command line
cat runs/summary.csv | column -t -s,

# View with Python
python -c "
import pandas as pd
df = pd.read_csv('runs/summary.csv')
print(df.describe())
print(df[df['overall_score'] > 0.7])
"
```

## 🚨 Common Issues Quick Reference

### Issue: Visualization Video Cannot Be Generated
```bash
# Check parameters
--save-vis  # Must add this parameter

# Check OpenCV
python -c "import cv2; print(cv2.__version__)"
```

### Issue: Batch Processing Stuck
```bash
# Reduce workers
--workers 2  # Reduce to 2

# Check GPU memory
nvidia-smi

# Don't generate visualization (save resources)
# Remove --save-vis
```

### Issue: No plot.png
```bash
# Install matplotlib
pip install matplotlib
```

### Issue: All Videos Skipped
```bash
# Use --overwrite to force reprocess
--overwrite
```

## ⚡ Performance Reference

### Single Video Processing Time (Reference)
| Model | CPU (2fps) | GPU (3fps) | GPU (5fps) |
|------|-----------|-----------|-----------|
| meso4 | ~8s | ~3s | ~5s |
| capsule_net | ~10s | ~4s | ~6s |
| f3net | ~15s | ~5s | ~8s |
| xception | ~30s | ~8s | ~12s |
| recce | ~20s | ~6s | ~10s |

### Batch Processing Throughput (100 videos)
| Configuration | Time | Speed |
|------|------|------|
| Serial | ~500s | 1 video/5s |
| 2 workers | ~250s | 1 video/2.5s |
| 4 workers | ~125s | 1 video/1.25s |
| 8 workers (multi-GPU) | ~62s | 1 video/0.6s |

## 📚 More Documentation

- **Quick Start**: `QUICK_START.md`
- **Complete Documentation**: See `tools/README.md`
- **Upgrade Notes**: `UPGRADE_SUMMARY_V2.md`
- **Tool Documentation**: `tools/README.md`

## 💡 Expert Tips

1. **Fast then Slow**: Use lightweight model for quick screening, then powerful model for detailed analysis
2. **Reasonable Parallelism**: Workers should not exceed CPU core count
3. **Resume Support**: For large batch tasks, check periodically - can continue after interruption
4. **Save Visualization**: Important videos should use `--save-vis` for later review
5. **Multi-Model Validation**: Cross-validate suspicious videos with multiple models for higher accuracy

## 🎉 Get Started

```bash
# 1. Test system
test_inference.bat

# 2. Batch process your videos
python tools/batch_predict.py \
  --input-dir your_videos \
  --model xception \
  --workers 2 \
  --save-vis

# 3. View results
python tools/aggregate_runs.py
```

Enjoy! 🚀
