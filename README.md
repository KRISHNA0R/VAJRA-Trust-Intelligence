# 🛡️ VAJRA Trust Intelligence

**Verification & AI-based Judgement for Risk Assessment**

A locally runnable deepfake-detection prototype for the **RAKSHAM AI Cybersecurity
Hackathon PS3 — "Deepfake Detection for Financial Communications"**.

> **Status (Oct 2026):** ✅ Verified working natively on Windows (CPU).
> Backend + browser UI + real image/video inference + PDF/ZIP reporting all
> smoke-tested. See [`VAJRA_SETUP_READINESS_REPORT.md`](VAJRA_SETUP_READINESS_REPORT.md)
> for the full evidence log.

---

## 1. Purpose

VAJRA Trust Intelligence helps analysts verify whether an image or video shows
signs of AI-based manipulation. Upload media in the browser, get a verdict
(REAL/FAKE) with confidence scores, forensic heatmaps (images) or suspicious
segments (video), and export a PDF/ZIP evidence package.

This repository is the **prepared, renamed, runnable baseline**. PS3 financial-
communication features (provenance, verification workflows, human review, …)
are **not yet implemented** — see the readiness report's PS3 matrix.

## 2. Current supported functionality (all verified)

| Capability | Status | Evidence |
|---|---|---|
| Image forgery detection + pixel-level localization (TruFor) | ✅ Working | `decision: real, integrity: 0.64` via live API |
| Anomaly heatmap, confidence map, Noiseprint++ map | ✅ Working | PNGs saved per job in `data/jobs/<job_id>/` |
| Video deepfake detection, 12 selectable models (DeepfakeBench) | ✅ Working | xception: 20 frames, verdict FAKE on synthetic clip, 15.6 s CPU |
| Voice spoof detection, Hindi/English/multilingual (Dhwani) | ✅ Working | 4/4: real EN/HI → REAL, TTS EN/HI → FAKE (API + browser tested) |
| Financial risk level + response playbook on every result | ✅ Working | CRITICAL/HIGH/MEDIUM/LOW + action checklist in UI, history, PDF |
| Suspicious-segment detection + keyframes | ✅ Working | 1 segment found on test clip |
| JWT auth (register/login, analyst/investigator/admin roles) | ✅ Working | register → login → Bearer token flow tested |
| Detection history (per-user, admin sees all) | ✅ Working | `GET /api/history` returned test job |
| PDF report download (valid `%PDF-`, ~1.4 MB) | ✅ Working | `GET /api/reports/{id}/pdf` |
| ZIP evidence package (valid PK zip, ~1.1 MB) | ✅ Working | `GET /api/reports/{id}/zip` |
| Browser UI (home, login, register, image, video, history) | ✅ Working | all pages HTTP 200, same-origin API (no CORS issues) |

## 3. Architecture overview

```
Browser (static HTML/JS served by FastAPI, same origin)
   │  POST /detect (image) · POST /api/deepfakebench/analyze (video)
   ▼
FastAPI (app/main.py) + JWT auth (app/auth) + history (app/history)
   ├── TruForAdapter (app/adapters/trufor_adapter.py) ──► TruFor (TruFor-main/)
   ├── DeepfakeBenchAdapter (app/adapters/deepfakebench_adapter.py) ──► 12 models (models/vendors/…)
   └── Reports (app/reports/) ──► reportlab PDF + ZIP evidence package
Runtime data: data/jobs/<job_id>/ (heatmaps, keyframes, timeline.json, report.pdf/zip)
```

## 4. Technology stack

| Layer | Stack |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | Vanilla HTML/CSS/JS + DaisyUI/Tailwind CDN (no build step, no npm needed) |
| Image AI | TruFor (`detconfcmx`, SegFormer mit_b2 + Noiseprint++), PyTorch CPU |
| Video AI | DeepfakeBench ensemble (12 detectors: Xception, Meso-4, Meso-4-Inception, F3Net, EfficientNet-B4, Capsule, SRM, RECCE, SPSL, UCF, CNN-AUG, CORE) |
| Audio AI | Dhwani spoof detector (XLS-R + AASIST, ONNX Runtime, multilingual en/hi/ta/te/ml) |
| Auth | JWT (`python-jose`), `passlib`/`bcrypt` |
| Reports | `reportlab`, stdlib `zipfile` |
| Video I/O | OpenCV (`cv2`), FFmpeg (test-media generation) |

## 5. System requirements

- **OS:** Windows 10/11 (verified on Windows 11). Linux/macOS should work with the same Python steps.
- **RAM:** 6 GB minimum, 8 GB+ recommended (TruFor).
- **Disk:** ~3 GB free (weights ~1.4 GB + dependencies).
- **GPU:** Not required. CPU inference verified. A 4 GB GTX 1650 Ti is present
  on the reference machine but unused (CPU-only PyTorch); GPU builds are untested.
- **Docker:** **Not required.** Native Windows run is the documented path.
  `Dockerfile`/`docker-compose.yml` remain as an untested fallback.

## 6. Versions

| Component | Verified version |
|---|---|
| Python | 3.14.2 (repo originally targeted 3.11; native run verified on 3.14 — see §12) |
| Node.js / npm | 25.8.1 / 11.14.1 (only used for a JS syntax check; **not required** to run) |
| PyTorch / torchvision | 2.13.0+cpu / 0.28.0+cpu |
| NumPy | 2.4.6 (repo pins `<2.0`, but 1.x has no Python-3.14 wheels — see §12) |
| FFmpeg | 9.0.2 (`winget install Gyan.FFmpeg`) |
| Git / Git LFS | 2.53.0 / 3.7.1 |

## 7. Native Windows setup

```powershell
# 1. (Optional, recommended) create an isolated environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Core runtime dependencies (verified set)
pip install fastapi "uvicorn[standard]" python-dotenv python-multipart `
  torch torchvision opencv-python pillow "numpy>=1.24.0" tqdm yacs timm `
  scipy scikit-image pyyaml aiofiles matplotlib `
  "python-jose[cryptography]==3.3.0" "passlib[bcrypt]==1.7.4" "bcrypt==3.2.0" `
  "reportlab==4.0.7" httpx pytest pytest-cov pytest-asyncio `
  simplejson fvcore iopath av scikit-learn albumentations tensorboard `
  omegaconf efficientnet-pytorch lmdb pretrainedmodels kornia `
  loralib transformers einops imgaug gdown

# 3b. Audio (voice spoof) dependencies
pip install onnxruntime soundfile scipy datasets huggingface_hub
# NOTE: datasets pulls torchcodec, whose DLL may fail to load on some Windows
# machines. It is only needed to fetch FLEURS test clips, not to run the app.

# 3. FFmpeg (for test-media generation; video decode itself uses OpenCV)
winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
# then refresh PATH in new shells
```

> `dlib` (a DeepfakeBench **training-time-only** dependency) has no Python-3.14
> Windows wheels and is intentionally **not** installed. `tools/build_dfbench_model.py`
> contains a documented stub + `np.sctypes` compat shim so inference works
> without it. Do not "fix" this by editing `models/vendors/` (third-party code).

## 8. Model download / setup

Weights are **not** in git (see `.gitignore`). Download the two archives from the
project's Google Drive folder and extract into `models/`:

- `TruFor_weights.zip` (~249 MB) → provides `weights/trufor.pth.tar`
- `vendors.zip` (~1.1 GB) → provides `vendors/DeepfakeBench/…` (framework + weights)

```powershell
pip install gdown
mkdir models_dl
gdown --folder "https://drive.google.com/drive/folders/117IJoriB7kJB9vWQOuj7_S6lNRSOyZ_A" -O models_dl --continue
Expand-Archive -Path "models_dl\TruFor_weights.zip" -DestinationPath "models" -Force
Expand-Archive -Path "models_dl\vendors.zip" -DestinationPath "models" -Force
# The TruFor zip nests the file one level deep; the app expects it at models/ :
Copy-Item models\weights\trufor.pth.tar models\trufor.pth.tar
```

Expected layout after extraction (verified):

```
models/
├── trufor.pth.tar                                   (~268 MB on disk, 952 tensors)
└── vendors/DeepfakeBench/training/
    ├── weights/  xception_best.pth, meso4_best.pth, meso4Incep_best.pth,
    │              f3net_best.pth, effnb4_best.pth, capsule_best.pth, srm_best.pth,
    │              recce_best.pth, spsl_best.pth, ucf_best.pth, cnnaug_best.pth,
    │              core_best.pth (+ ffd_best.pth spare)
    └── pretrained/xception-b5690688.pth             (ImageNet backbone, 87 MB)
```

Verify: `(Get-ChildItem models\vendors\DeepfakeBench\training\weights\*.pth).Count`
should be **13** (12 registry models + 1 spare `ffd_best.pth`).

### Audio model (Dhwani, ~1.2 GB)

```powershell
python -c "from huggingface_hub import snapshot_download; snapshot_download('ayush2635/Dhwani-Multilingual-Deepfake-Audio-Detection-Model', local_dir='models/audio_dhwani')"
```

Expected: `models/audio_dhwani/best_model.onnx` (~1.26 GB).
MIT license. We did not train it — credit to the original author (HCL Guvi Hackathon "Dhwani").

## 9. Environment variables

Copy `.env.example` to `.env` and set a real secret for anything beyond local testing:

| Variable | Default | Purpose |
|---|---|---|
| `JWT_SECRET_KEY` | `your-secret-key-change-in-production` (dev fallback) | JWT signing — **must** be overridden outside local dev |
| `MODEL_PATH` | `models/trufor.pth.tar` | TruFor weights path |
| `HOST` / `PORT` | `127.0.0.1` / `8000` | Native server bind |
| `PYTHONIOENCODING` | — (set to `utf-8` on Windows) | Prevents console `UnicodeEncodeError` from model logs |

Default seeded admin: `admin` / `admin123` — change immediately after first login.

## 10. Backend startup

```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:MODEL_PATH = "models/trufor.pth.tar"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Health check: `http://127.0.0.1:8000/health` → `{"status":"healthy",…}`.
Interactive API docs: `http://127.0.0.1:8000/docs`.

## 11. Frontend startup

No build step — the FastAPI server serves the UI directly. Open:

**http://localhost:8000/web/index_main.html**

Pages: Home · Register · Login · Images/TruFor (`index.html`) ·
Video/DeepfakeBench (`deepfakebench.html`) · Audio/Voice-Spoof (`audio.html`) ·
History (`history.html`).
First visit: **Register** (password needs 8+ chars with upper/lower/digit),
then **Login**. The frontend calls same-origin `/detect` and `/api/…`, so no
CORS configuration is needed for local use.

## 12. Image testing procedure

```powershell
$env:PYTHONIOENCODING = "utf-8"
# fast smoke test (downscaled copy keeps CPU time low)
ffmpeg -y -i test_data_cycle2/pexels-karina-diniz-1382740-34106777.jpg -vf scale=512:-1 test_small.jpg
python api_smoke.py   # register/login flow is inside; prints decision + job_id
```

Reference result (verified): `status: success, decision: real, integrity: ~0.64`.
A full-resolution 8192×6554 px photo took ~139 s on CPU; 512-px images take
tens of seconds. Heatmaps land in `data/jobs/<job_id>/`.

## 13. Video testing procedure

```powershell
# generate a legal synthetic clip (no private data involved)
ffmpeg -y -f lavfi -i testsrc=duration=6:size=320x240:rate=10 -pix_fmt yuv420p test_vid.mp4
# then in the browser: DeepfakeBench page → select model (e.g. xception) → upload test_vid.mp4
```

Reference result (verified, xception, CPU): 20 frames, verdict FAKE (expected —
a synthetic test pattern is out-of-distribution), 1 suspicious segment, ~16 s.

## 13b. Voice testing procedure

```powershell
python audio_verify.py   # direct adapter check, no server needed (expects 4/4 OK)
# or in the browser: Audio page → upload a WAV/MP3 → verdict + per-window scores
```

Reference results (verified, Dhwani, CPU, live API + browser):

| Clip | Source | Verdict | Fake prob |
|---|---|---|---|
| `test_real_en.wav` | FLEURS English (genuine) | REAL | 0.0004 |
| `test_real_hi.wav` | FLEURS Hindi (genuine) | REAL | 0.0002 |
| `test_fake_en.wav` | MMS-TTS English (synthesized) | FAKE | 0.78 |
| `test_fake_hi.wav` | MMS-TTS Hindi (synthesized) | FAKE | 0.99 |

Rejected alternatives (tested, honestly discarded): a wav2vec2 PA-trained model
missed clean TTS fakes; two AST spoof models saturated or showed English bias;
a wav2vec2-ASVspoof5 checkpoint produced constant outputs.

## 14. Known limitations

1. **CPU-only.** No CUDA PyTorch installed; inference times above are CPU times.
   GPU acceleration is untested.
2. **Python 3.14 vs repo's 3.11.** Works, but requires the two documented
   shims in `tools/build_dfbench_model.py` (dlib stub, `np.sctypes` restore)
   because `dlib` won't build and NumPy 1.x has no 3.14 wheels.
3. **Windows console encoding.** Model code logs Unicode (emoji); without
   `PYTHONIOENCODING=utf-8` (or `python -X utf8`) startup can crash with
   `UnicodeEncodeError: 'charmap' codec…`. This is environmental, not a model bug.
4. **Video `device="cuda"` hardcode** in `run_deepfakebench_analysis` falls back
   to CPU automatically (`torch.cuda.is_available()` check in the adapter) —
   verified working, but GPU has never been exercised.
5. **Docker path untested** natively in this environment; kept as fallback only.
6. **Default JWT secret + seeded admin** are dev conveniences — rotate before
   any shared deployment.
7. PS3 financial-communication features are **not implemented** (see §17 of the
   readiness report).

## 15. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `TruFor model not found`, adapter not initialized | `models/trufor.pth.tar` missing — copy it out of `models/weights/` (§8) |
| `ModuleNotFoundError: No module named 'dlib'` | Expected — the stub in `tools/build_dfbench_model.py` covers this; don't install dlib |
| `np.sctypes was removed in NumPy 2.0` | Covered by the shim in `tools/build_dfbench_model.py`; don't downgrade NumPy on Py3.14 |
| `UnicodeEncodeError: 'charmap' codec…` on startup | `set PYTHONIOENCODING=utf-8` before launching |
| Image `POST /detect` is slow | Normal on CPU; use smaller images; TruFor pads to 512×512 internally |
| Video job stuck at "processing" | Model load takes ~1 min on CPU first time; poll `GET /api/deepfakebench/jobs/{id}` |
| `File too large` | Limits: 10 MB image, 500 MB video (`app/main.py`) |

## 16. Third-party models

VAJRA integrates — but did **not** train and does **not** own — these models.
Technical model names (TruFor, DeepfakeBench, Xception, …) are intentionally
left unchanged throughout the codebase.

- **TruFor** — GRIP, University of Naples Federico II.
  Repo: <https://github.com/grip-unina/TruFor> ·
  Paper: Guillaro et al., arXiv:2212.10957. A vendored copy lives in `TruFor-main/`.
- **DeepfakeBench** — SCLBD. Repo: <https://github.com/SCLBD/DeepfakeBench> ·
  Paper: Yan et al., arXiv:2307.01426. Framework + weights live in
  `models/vendors/DeepfakeBench/` (downloaded, gitignored).
- **Dhwani** — multilingual (en/hi/ta/te/ml) voice-spoof detector (XLS-R + AASIST, ONNX).
  Source: <https://huggingface.co/ayush2635/Dhwani-Multilingual-Deepfake-Audio-Detection-Model>
  (MIT). Weights live in `models/audio_dhwani/` (downloaded, gitignored).

## 17. Third-party licenses & attribution

- This project's own integration code: see `docs/handover/LICENSE`
  (MIT, © 2025 The University of Melbourne — preserved unchanged).
- TruFor: see `TruFor-main/TruFor-main/test_docker/LICENSE.txt` and `LICENSE_CMX.txt`.
- DeepfakeBench: see its license inside `models/vendors/DeepfakeBench/`.
- If you publish research using this system, cite the TruFor and DeepfakeBench
  papers above — credit belongs to the original authors.

## 18. Data / privacy note

- Use only synthetic, public, or properly consented media for testing
  (`test_data_cycle2/`, generated `testsrc` clips). Never commit private or
  confidential financial data.
- Runtime artifacts (`data/jobs/…`, `data/users.json`) are gitignored and stay
  on your machine. Wipe them with `scripts/clean_test_data.ps1` (review it first).
- The app runs on `127.0.0.1` by default; do not expose the dev server publicly.
