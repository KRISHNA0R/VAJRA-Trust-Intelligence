# Model Weights Download Guide

## 🚀 Quick Reference (TL;DR)

For users who just want to get started quickly:

```bash
# 1. Clone repository
git clone https://github.com/fsrconsulting/deepfake-detector.git
cd deepfake-detector

# 2. Download from Google Drive (in browser):
#    https://drive.google.com/drive/folders/117IJoriB7kJB9vWQOuj7_S6lNRSOyZ_A?usp=sharing
#    - TruFor_weights.zip (248.8 MB)
#    - vendors.zip (1.1 GB)

# 3. Move files to project directory and extract
# (Adjust path to your Downloads folder)

# Windows:
Move-Item $HOME\Downloads\*.zip .
Expand-Archive TruFor_weights.zip -DestinationPath . -Force
Expand-Archive vendors.zip -DestinationPath . -Force

# Linux/Mac:
mv ~/Downloads/*.zip .
unzip TruFor_weights.zip
unzip vendors.zip

# 4. Verify files
ls -lh models/trufor.pth.tar  # Should show ~249 MB
ls vendors/DeepfakeBench/training/weights/*.pth  # Should show 12 files

# 5. Start Docker
docker compose up -d --build

# 6. Access application
# http://localhost:8000/web/register.html (first time)
# http://localhost:8000/web/login.html (login)
```

**Need details?** Read the full guide below ⬇️

---

## 📥 Download Links

**All model weights are hosted on Google Drive for easy access:**

🔗 **[Download All Models (Google Drive)](https://drive.google.com/drive/folders/117IJoriB7kJB9vWQOuj7_S6lNRSOyZ_A?usp=sharing)**

### Available Files:
1. **TruFor_weights.zip** (248.8 MB)
   - Contains: `trufor.pth.tar` (extract to `models/` directory)
   - For: Image forgery detection and localization

2. **vendors.zip** (1.1 GB)
   - Contains: **Complete DeepfakeBench framework + 12 model weights (already included)**
   - For: Video deepfake detection with multiple models
   - **Note**: All `.pth` weight files are already in `vendors/DeepfakeBench/training/weights/`

**Important:** These files are **NOT** included in `git clone` - they're in `.gitignore` to keep the repository small.

---

## 🤖 Model Information

### 1. TruFor Model

#### About
- **Full Name**: TruFor - Improving Deepfake Detection via Transformer-based Fusion
- **Developed by**: GRIP (Research Group on Image Processing) - University of Naples Federico II
- **Official Repository**: https://github.com/grip-unina/TruFor
- **Paper**: [TruFor: Leveraging All-Round Clues for Trustworthy Image Forgery Detection and Localization](https://arxiv.org/abs/2212.10957)

#### What We Use
- **Pre-trained weights**: `models/trufor.pth.tar`
- **Source**: Provided by original authors
- **License**: Check official repository
- **Our Role**: **Integration only** - we did not train this model

#### Capabilities
- Pixel-level forgery localization
- Confidence mapping
- Noiseprint++ analysis
- Works on images (JPG, PNG)

---

### 2. DeepfakeBench Models

#### About
- **Project**: DeepfakeBench - A Comprehensive Benchmark for Deepfake Detection
- **Developed by**: SCLBD (Shenzhen Campus of  Learning and Big Data)
- **Official Repository**: https://github.com/SCLBD/DeepfakeBench
- **Paper**: [DeepfakeBench: A Comprehensive Benchmark of Deep Learning Methods for Deepfake Detection](https://arxiv.org/abs/2307.01426)

#### What We Use
- **12 Pre-trained Models** (V3.0):
  1. Xception (299×299)
  2. MesoNet-4 (256×256)
  3. MesoNet-4 Inception (256×256)
  4. F3Net (256×256)
  5. EfficientNet-B4 (380×380)
  6. Capsule Net (128×128)
  7. SRM (256×256)
  8. RECCE (224×224)
  9. SPSL (224×224)
  10. UCF (256×256)
  11. CNN-AUG (224×224)
  12. CORE (256×256)

- **Source**: Provided by DeepfakeBench project
- **License**: Check official repository
- **Our Role**: **Integration only** - we did not train these models

#### Capabilities
- Frame-by-frame video analysis
- Multi-model ensemble predictions
- Suspicious segment detection
- Works on videos (MP4, MOV, AVI)

---

## 📋 Complete Installation Guide

### Understanding the Setup

**Important Notes:**
1. When you `git clone` the repository, model weights are **NOT included** (they're in `.gitignore`)
2. The compressed files contain:
   - `TruFor_weights.zip` → extract to `models/trufor.pth.tar`
   - `vendors.zip` → **entire `vendors/` folder with 12 model weights already inside**
3. Extract these files to `models/` directory before running Docker
4. **No separate weight download needed** - `vendors.zip` already contains all `.pth` files

---

### Step 1: Clone Repository

```bash
# Clone the project
git clone https://github.com/fsrconsulting/deepfake-detector.git

# Navigate to project directory
cd deepfake-detector
```

**Current state:** You have the code, but **NO model weights yet**.

---

### Step 2: Download Model Weights

**Visit Google Drive:**
🔗 https://drive.google.com/drive/folders/117IJoriB7kJB9vWQOuj7_S6lNRSOyZ_A?usp=sharing

**Download these two files to your Downloads folder:**
- ✅ `TruFor_weights.zip` (248.8 MB)
- ✅ `vendors.zip` (1.1 GB)

**Total download size:** ~1.35 GB  
**Time estimate:** 5-15 minutes depending on internet speed

---

### Step 3: Move Files to Project Directory

Move the downloaded ZIP files into your project directory:

#### Windows (PowerShell):
```powershell
# Navigate to project
cd C:\path\to\deepfake-detector

# Move files from Downloads (adjust path if needed)
Move-Item $HOME\Downloads\TruFor_weights.zip .
Move-Item $HOME\Downloads\vendors.zip .
```

#### Linux/Mac:
```bash
# Navigate to project
cd /path/to/deepfake-detector

# Move files from Downloads
mv ~/Downloads/TruFor_weights.zip .
mv ~/Downloads/vendors.zip .
```

**Now you should have:**
```
deepfake-detector/
├── TruFor_weights.zip    ← Downloaded file
├── vendors.zip           ← Downloaded file
├── app/
├── configs/
├── docker-compose.yml
└── ...
```

---

### Step 4: Extract Files

**⚠️ IMPORTANT: Extract in the PROJECT ROOT directory (where docker-compose.yml is)**

#### Windows (PowerShell):

```powershell
# Make sure you're in project root
cd C:\path\to\deepfake-detector

# Extract TruFor weights to models/ directory
Expand-Archive -Path "TruFor_weights.zip" -DestinationPath "models" -Force
# This creates: models/trufor.pth.tar

# Extract vendors folder to models/ directory
Expand-Archive -Path "vendors.zip" -DestinationPath "models" -Force
# This creates: models/vendors/ folder

# Optional: Delete ZIP files after extraction
Remove-Item TruFor_weights.zip
Remove-Item vendors.zip
```

#### Linux/Mac:

```bash
# Make sure you're in project root
cd /path/to/deepfake-detector

# Create models directory if it doesn't exist
mkdir -p models

# Extract TruFor weights to models/ directory
unzip TruFor_weights.zip -d models
# This creates: models/trufor.pth.tar

# Extract vendors folder to models/ directory
unzip vendors.zip -d models
# This creates: models/vendors/ folder

# Optional: Delete ZIP files after extraction
rm TruFor_weights.zip vendors.zip
```

---

### Step 5: Verify Directory Structure

**After extraction, your directory should look like this:**

```
deepfake-detector/
├── models/                     ← Model weights directory ✅
│   ├── trufor.pth.tar         ← TruFor model (249 MB) ✅
│   └── vendors/               ← DeepfakeBench folder ✅
│       └── DeepfakeBench/
│           ├── analysis/
│       ├── preprocessing/
│       ├── tools/
│       └── training/
│           ├── config/
│           ├── dataset/
│           ├── detectors/
│           ├── networks/
│           └── weights/        ← Model weights here ✅
│               ├── xception_best.pth
│               ├── meso4_best.pth
│               ├── meso4Incep_best.pth
│               ├── f3net_best.pth
│               ├── effnb4_best.pth
│               ├── capsule_best.pth
│               ├── srm_best.pth
│               ├── recce_best.pth
│               ├── spsl_best.pth
│               ├── ucf_best.pth
│               ├── cnnaug_best.pth
│               └── core_best.pth
├── app/
├── configs/
├── data/
├── docker-compose.yml
├── Dockerfile
├── README.md
└── ...
```

**✅ Verification Checklist:**
- [ ] `models/trufor.pth.tar` exists (249 MB)
- [ ] `models/vendors/DeepfakeBench/` directory exists
- [ ] 12 `.pth` files in `models/vendors/DeepfakeBench/training/weights/`

**Run verification commands:**

#### Windows (PowerShell):
```powershell
# Check TruFor exists
Get-Item models\trufor.pth.tar
# Should show: ~249 MB

# Count DeepfakeBench weights
(Get-ChildItem vendors\DeepfakeBench\training\weights\*.pth).Count
# Should show: 12
```

#### Linux/Mac:
```bash
# Check TruFor exists
ls -lh models/trufor.pth.tar
# Should show: ~249 MB

# Count DeepfakeBench weights
ls models/vendors/DeepfakeBench/training/weights/*.pth | wc -l
# Should show: 12
```

✅ **If both checks pass, you're ready for Docker!**

---

### Step 6: Start with Docker

#### First Time Setup:

```bash
# Build and start container
docker compose up -d --build
```

**What happens:**
1. Docker builds the image (~5-10 minutes first time)
2. Copies `models/` directory (with trufor.pth.tar and vendors/) into container
3. Installs all Python dependencies
5. Starts FastAPI server on port 8000

**Wait for startup:**
```bash
# Monitor startup progress
docker compose logs -f

# Look for this message:
# "INFO:     Application startup complete."
# "INFO:     Uvicorn running on http://0.0.0.0:8000"
```

Press `Ctrl+C` to stop viewing logs (container keeps running)

---

### Step 7: Access the Application

**Open your browser:**

1. **First-time users - Register:**
   ```
   http://localhost:8000/web/register.html
   ```
   - Create username and password
   - Click "Register"

2. **Login:**
   ```
   http://localhost:8000/web/login.html
   ```
   - Enter your credentials
   - Session valid for 24 hours

3. **Start detecting:**
   - Main Page: `http://localhost:8000/web/index_main.html`
   - DeepfakeBench: `http://localhost:8000/web/deepfakebench.html`
   - History: `http://localhost:8000/web/history.html`

---

### Step 8: Stop Docker (When Done)

```bash
# Stop container (preserves data)
docker compose down

# Stop and remove all data
docker compose down -v
```

---

### Step 9: Restart Docker (Next Time)

```bash
# Just start (no rebuild needed if no code changes)
docker compose up -d

# Rebuild if you updated code
docker compose up -d --build
```

---

## 🐳 Docker Usage Details

### Understanding Docker Commands

**First Time (or after code changes):**
```bash
docker compose up -d --build
```
- `up`: Start the container
- `-d`: Run in background (detached mode)
- `--build`: Rebuild the image (includes new code/weights)

**Regular Start (weights/code unchanged):**
```bash
docker compose up -d
```
- Faster, uses existing image

**View Logs:**
```bash
# Follow logs in real-time
docker compose logs -f

# View last 100 lines
docker compose logs --tail 100

# View specific service logs
docker compose logs -f deepfake-detector
```

**Stop Container:**
```bash
# Stop but keep data
docker compose down

# Stop and remove volumes (clears all data)
docker compose down -v
```

**Rebuild from Scratch:**
```bash
# Remove old images and rebuild
docker compose down
docker system prune -f
docker compose up -d --build
```

### LAN Access (Access from Other Devices)

The container is configured for LAN access by default:

**In `docker-compose.yml`:**
```yaml
ports:
  - "8000:8000"  # Exposes to all network interfaces
environment:
  - HOST=0.0.0.0  # Listens on all IPs
```

**Access from other devices:**
1. Find your computer's IP:
   ```bash
   # Windows
   ipconfig
   # Look for "IPv4 Address"
   
   # Linux/Mac
   ifconfig
   # Look for "inet" address
   ```

2. On other device (phone/tablet/another computer):
   ```
   http://YOUR_IP:8000/web/login.html
   ```
   Example: `http://192.168.1.100:8000/web/login.html`

**Firewall Note:** Make sure port 8000 is allowed in your firewall.

### Docker Troubleshooting

**Container won't start:**
```bash
# Check container status
docker compose ps

# Check detailed logs
docker compose logs

# Restart container
docker compose restart
```

**Models not loading:**
```bash
# Check if files exist IN container
docker compose exec deepfake-detector ls -lh /app/models/trufor.pth.tar
docker compose exec deepfake-detector ls /app/models/vendors/DeepfakeBench/training/weights/

# If missing, files weren't copied during build
# Solution: Make sure files exist on host, then rebuild
docker compose down
docker compose up -d --build
```

**Out of disk space:**
```bash
# Clean up old Docker data
docker system prune -a

# Remove unused images
docker image prune -a
```

**Note**: The `.dockerignore` file is configured to **NOT** ignore model files during build, so they will be copied into the container.

---

## 🔍 Model Weight Details

### TruFor Model File

| Property | Value |
|----------|-------|
| Filename | `models/trufor.pth.tar` |
| Size | ~249 MB |
| Format | PyTorch checkpoint |
| Location | Project root |
| Required for | Image detection |

### DeepfakeBench Weight Files

| Model | Filename | Size | Input Size |
|-------|----------|------|------------|
| Xception | `xception_best.pth` | ~85 MB | 299×299 |
| MesoNet-4 | `meso4_best.pth` | ~2 MB | 256×256 |
| MesoNet-4 Inception | `meso4Incep_best.pth` | ~3 MB | 256×256 |
| F3Net | `f3net_best.pth` | ~90 MB | 256×256 |
| EfficientNet-B4 | `effnb4_best.pth` | ~70 MB | 380×380 |
| Capsule Net | `capsule_best.pth` | ~10 MB | 128×128 |
| SRM | `srm_best.pth` | ~90 MB | 256×256 |
| RECCE | `recce_best.pth` | ~85 MB | 224×224 |
| SPSL | `spsl_best.pth` | ~85 MB | 224×224 |
| UCF | `ucf_best.pth` | ~90 MB | 256×256 |
| CNN-AUG | `cnnaug_best.pth` | ~85 MB | 224×224 |
| CORE | `core_best.pth` | ~85 MB | 256×256 |

**Total DeepfakeBench weights**: ~780 MB

---

## ⚠️ Important Notes

### License and Usage

1. **TruFor Model**
   - Developed by GRIP-UNINA
   - Check license at: https://github.com/grip-unina/TruFor
   - Cite the original paper if using in research

2. **DeepfakeBench Models**
   - Developed by SCLBD
   - Check license at: https://github.com/SCLBD/DeepfakeBench
   - Cite the original paper if using in research

### Our Integration

**We only integrated these models into our system. We did NOT:**
- Train any of these models
- Modify the model architectures
- Create the training datasets
- Claim ownership of the models

**All credit goes to the original authors and research teams.**

### Citations

If you use this system in your research, please cite:

**TruFor:**
```bibtex
@article{guillaro2023trufor,
  title={TruFor: Leveraging All-Round Clues for Trustworthy Image Forgery Detection and Localization},
  author={Guillaro, Fabrizio and Cozzolino, Davide and Sud, Avneesh and Dufour, Nicholas and Verdoliva, Luisa},
  journal={arXiv preprint arXiv:2212.10957},
  year={2023}
}
```

**DeepfakeBench:**
```bibtex
@article{yan2023deepfakebench,
  title={DeepfakeBench: A Comprehensive Benchmark of Deep Learning Methods for Deepfake Detection},
  author={Yan, Zhiyuan and Zhang, Yong and Fan, Yanbo and Wu, Baoyuan},
  journal={arXiv preprint arXiv:2307.01426},
  year={2023}
}
```

---

## 🆘 Troubleshooting

### Problem: Download fails from Google Drive

**Solution**:
- Google Drive may have download limits
- Try downloading at a different time
- Use "Download All" and extract locally

### Problem: "Model not found" error

**Checklist**:
- [ ] TruFor: Check `models/trufor.pth.tar` exists
- [ ] DeepfakeBench: Check `models/vendors/DeepfakeBench/training/weights/*.pth` exist
- [ ] Verify file names match exactly (case-sensitive)
- [ ] Check file sizes match expected values

### Problem: Docker build doesn't include weights

**Solution**:
```bash
# Make sure files exist before building
ls -lh models/trufor.pth.tar
ls models/vendors/DeepfakeBench/training/weights/

# Rebuild with --no-cache
docker compose build --no-cache
docker compose up -d
```

### Problem: Out of disk space

**Requirements**:
- TruFor: 250 MB
- DeepfakeBench: 1.1 GB (compressed), ~800 MB (extracted weights)
- **Total**: ~1.5 GB minimum

---

## 📞 Need Help?

1. **Check the official repositories:**
   - TruFor: https://github.com/grip-unina/TruFor
   - DeepfakeBench: https://github.com/SCLBD/DeepfakeBench

2. **Read our documentation:**
   - [README.md](../../README.md) - Project overview
   - [TRUFOR_TECHNICAL_GUIDE.md](TRUFOR_TECHNICAL_GUIDE.md) - TruFor technical details
   - See `tools/README.md` for CLI usage (advanced users)

3. **Contact:**
   - Project Maintainer: Xiyu Guan (xiyug@student.unimelb.edu.au)

---

**Last Updated**: November 5, 2025  
**Document Version**: 3.1  
**Download Link**: https://drive.google.com/drive/folders/117IJoriB7kJB9vWQOuj7_S6lNRSOyZ_A?usp=sharing
