# VAJRA Trust Intelligence

## Setup & Readiness Report

Product: **VAJRA Trust Intelligence**
Full form: **Verification & AI-based Judgement for Risk Assessment**
Context: RAKSHAM AI Cybersecurity Hackathon, PS3 (Deepfake Detection for Financial Communications)
Date: 2026-10-05 · Author: setup agent (local Windows preparation) · Scope: **setup only, no new PS3 features**

---

### 1. Executive Summary

**Status: READY WITH LIMITATIONS.**

The prototype runs natively on Windows without Docker. Backend boots and loads
TruFor; all 5 UI pages + Swagger serve HTTP 200; real image inference
(TruFor, `decision: real, integrity: ~0.64`) and real video inference (xception,
20 frames, ~16 s CPU) were executed; history, PDF (`%PDF-`, 1.39 MB) and ZIP
(`PK`, 1.12 MB) downloads verified; all 12 DeepfakeBench models load their
weights. Branding was renamed to VAJRA Trust Intelligence throughout the app.

Limitations: CPU-only inference (slow on large images); Python 3.14 required
two small documented shims; `dlib` unavailable (training-only, stubbed);
Docker path untested; dev JWT secret + seeded admin must be rotated before any
shared use; PS3 financial-communication features are not implemented.

### 2. Environment

| Item | Value |
|---|---|
| OS | Windows 11 Home (10.0.26300), `C:\Users\Krish\OneDrive\Desktop\vajra` |
| RAM | ~7.4 GB total visible |
| Disk free (start) | ~225 GB |
| Python | 3.14.2 (only interpreter installed; repo targeted 3.11) |
| Node / npm | 25.8.1 / 11.14.1 (not required to run; static frontend) |
| Git / Git LFS | 2.53.0.windows.2 / 3.7.1 |
| PyTorch / torchvision | 2.13.0+cpu / 0.28.0+cpu, `cuda: False` |
| GPU | NVIDIA GeForce GTX 1650 Ti 4 GB (present, **unused**) |
| FFmpeg | 9.0.2 (installed via `winget Gyan.FFmpeg` during setup) |
| System deps for OpenCV | OK (no `libGL` issue on Windows) |

### 3. Repository

| Item | Value |
|---|---|
| Source repository | `https://github.com/fsrconsulting/deepfake-detector.git` |
| Original commit | `b4c9e90` — "docs: update GitHub repository URL (migrated to fsrconsulting organization)" (2025-11-07) |
| Branch before reset | `main` (also fetched `origin/report_evidence`; no tags) |
| Pre-flight | Working dir was empty, not a git repo; nothing overwritten; no secrets encountered |
| Layout | `app/` (FastAPI + adapters/auth/history/reports/web), `configs/`, `data/`, `docs/`, `models/`, `scripts/`, `tests/`, `test_data_cycle2/`, `tools/`, `TruFor-main/`, `Dockerfile`, `docker-compose.yml`, `pytest.ini` |
| Backend framework | FastAPI + Uvicorn, 34 routes |
| Frontend | 6 static pages, vanilla JS, DaisyUI/Tailwind CDN, same-origin `/detect` + `/api/…` (no CORS problem) |
| License/attribution files | `docs/handover/LICENSE` (MIT, Univ. of Melbourne) preserved; TruFor `LICENSE*.txt` preserved; third-party model names untouched |

### 4. Dependencies

| Dependency | Required | Installed | Status |
|---|---|---|---|
| fastapi | ≥0.104 | 0.141.1 | ✅ |
| uvicorn[standard] | ≥0.24 | 0.49.0 | ✅ |
| python-dotenv | ≥1.0 | 1.2.2 | ✅ |
| python-multipart | ≥0.0.6 | 0.0.32 | ✅ |
| torch (CPU) | ≥2.0 | 2.13.0+cpu | ✅ |
| torchvision (CPU) | ≥0.15 | 0.28.0+cpu | ✅ |
| opencv-python | ≥4.8 | 4.14.0.94 | ✅ |
| pillow | ≥10 | 12.2.0 | ✅ |
| numpy | ≥1.24,<2.0 | **2.4.6** | ⚠️ newer than pin (1.x has no Py3.14 wheels); works + `np.sctypes` shim |
| tqdm / yacs / timm / scipy / scikit-image / pyyaml / aiofiles / matplotlib | various | all present | ✅ |
| python-jose / passlib / bcrypt | 3.3.0 / 1.7.4 / 3.2.0 | exact pins | ✅ |
| reportlab | 4.0.7 | 4.0.7 | ✅ |
| httpx / pytest / pytest-cov / pytest-asyncio | various | present | ✅ |
| DeepfakeBench set (simplejson, fvcore, iopath, av, sklearn, albumentations, tensorboard, omegaconf, efficientnet-pytorch, lmdb, pretrainedmodels, kornia, loralib, transformers, einops, imgaug) | various | all installed | ✅ |
| dlib | ≥19.24 | **not installed** | ⚠️ cannot build on Py3.14/Win; training-only, stubbed (see §14) |
| torchaudio | — | not required by code | ➖ N/A |
| Node deps | — | none (no frontend build) | ➖ N/A |

### 5. Models

| Model | Purpose | Source | Expected location | Size | Downloaded | Load test | Status |
|---|---|---|---|---|---|---|---|
| TruFor `trufor.pth.tar` | image forgery detect + localize | GDrive `TruFor_weights.zip` | `models/trufor.pth.tar` (copied out of `models/weights/`) | 281,496,429 B, 952 tensors | ✅ | ✅ init + inference | ✅ |
| xception_best.pth | video (299px) | GDrive `vendors.zip` | `models/vendors/DeepfakeBench/training/weights/` | 87,763,531 B | ✅ | ✅ build + weights + infer (p=0.504 on noise) | ✅ |
| meso4_best.pth | video (256px) | same | same | 117,943 B | ✅ | ✅ build + weights | ✅ |
| meso4Incep_best.pth | video (256px) | same | same | 126,419 B | ✅ | ✅ build + weights | ✅ |
| f3net_best.pth | video (256px) | same | same | 90,398,839 B | ✅ | ✅ build + weights | ✅ |
| effnb4_best.pth | video (380px) | same | same | 70,979,261 B | ✅ | ✅ build + weights | ✅ |
| capsule_best.pth | video (128px) | same | same | 15,694,749 B | ✅ | ✅ build + weights | ✅ |
| srm_best.pth | video (256px) | same | same | 222,088,575 B | ✅ | ✅ build + weights | ✅ |
| recce_best.pth | video (224px) | same | same | 191,466,941 B | ✅ | ✅ build + weights | ✅ |
| spsl_best.pth | video (224px) | same | same | 87,764,683 B | ✅ | ✅ build + weights | ✅ |
| ucf_best.pth | video (256px) | same | same | 188,006,161 B | ✅ | ✅ build + weights | ✅ |
| cnnaug_best.pth | video (224px, `multi_attention`) | same | same | 85,285,901 B | ✅ | ✅ build + weights | ✅ |
| core_best.pth | video (256px) | same | same | 87,766,765 B | ✅ | ✅ build + weights | ✅ |
| xception-b5690688.pth | ImageNet backbone (f3net/core/spsl/ucf/srm/capsule configs) | bundled in `vendors.zip` | `models/vendors/DeepfakeBench/training/pretrained/` | 91,674,713 B | ✅ | ✅ consumed at build | ✅ |
| ffd_best.pth | spare (not in registry) | same | weights dir | 87,796,541 B | ✅ | ➖ not wired to UI | ➖ spare |

No fake/placeholder weights were created. Every load test used the real files.

### 6. System Dependencies

| Tool | Required | Installed | Version | Status |
|---|---|---|---|---|
| FFmpeg | yes (test media; decode is OpenCV) | ✅ (via winget) | 9.0.2 | ✅ |
| Git / Git LFS | yes | ✅ | 2.53.0 / 3.7.1 | ✅ |
| Visual C++ runtime/build tools | only if building dlib | ➖ not installed | — | ➖ skipped (dlib stubbed) |
| CUDA/cuDNN | optional | ❌ | — | ⚠️ CPU-only; GPU untested |
| Docker | fallback only | unknown | — | ➖ not used/tested |

### 7. Backend Test

- Startup: `$env:PYTHONIOENCODING="utf-8"; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
- Log: `TruFor adapter initialized successfully` + `Application startup complete`
- `GET /health` → 200 `{"status":"healthy","service":"vajra-trust-intelligence",…}` (after rename; verified post-restart in §18)
- Auth: register (`analyst`) → 200, login → JWT (156 chars), `/api/models/status` → trufor available + 12 deepfakebench models
- Status: **PASS**

### 8. Frontend Test

- Startup: none — served by the same Uvicorn process (static `app/web/`)
- `index_main.html`, `login.html`, `register.html`, `deepfakebench.html`, `history.html`, `/docs` → all **HTTP 200**
- `app.js` → `node --check` clean; all API calls same-origin (`/detect`, `/api/…`) — no CORS/port issue
- Status: **PASS** (HTTP-level; no GUI browser available in this environment — see §18)

### 9. Image Pipeline Test

- Input: `test_data_cycle2/pexels-jess-vide-4321125.jpg` (3,053,723 B, 8192×6554) + 512-px downscale via live API
- Direct adapter: `status: success, decision: real, integrity: 0.6340`, heatmap + confidence + Noiseprint++ maps present, portrait-note heuristic fired, **138.94 s CPU**
- Live `POST /detect`: `status: success, decision: real, integrity: 0.6399`, `job_id` returned, heatmaps written to `data/jobs/<job_id>/`
- Status: **PASS**

### 10. Video Pipeline Test

- Input: synthetic `testsrc` 6 s 320×240@10fps (`test_vid.mp4`, 23,776 B — no private data)
- xception, CPU: `success: True, verdict: FAKE, overall: 0.9782` (expected: synthetic pattern is out-of-distribution), 20 frames, 1 suspicious segment, **15.57 s**
- Status: **PASS**

### 11. Report Generation Test

- `GET /api/history?limit=5` → 200, test job present
- `GET /api/reports/{job}/pdf` → 200, 1,387,389 B, magic `%PDF-`
- `GET /api/reports/{job}/zip` → 200, 1,119,037 B, magic `PK\x03\x04`
- Status: **PASS**

### 12. Native Windows Compatibility

**SUPPORTED** (with documented caveats): full native run — no Docker, no WSL —
backend + UI + inference + reports verified on Windows 11 / Python 3.14 / CPU.
Caveats: `PYTHONIOENCODING=utf-8` needed for console; CPU inference is slow on
large images; GPU path never exercised.

### 13. Docker Requirement

- Works without Docker: **everything verified above.**
- Still requires Docker: **nothing.**
- Docker status: **OPTIONAL, untested fallback** (`Dockerfile` + `docker-compose.yml` preserved as-is).
- Native startup: §7 (backend, serves UI too) → open `http://localhost:8000/web/index_main.html` → Register → Login → upload.

### 14. Known Issues

1. `dlib` cannot be installed (no Py3.14 Windows wheels; source build fails) — mitigated by a stub in `tools/build_dfbench_model.py`; training-time-only code path.
2. NumPy 2.4.6 vs pinned `<2.0` — mitigated by an `np.sctypes` compat shim in the same file; do not downgrade on Python 3.14.
3. Windows console `UnicodeEncodeError` from emoji logs — set `PYTHONIOENCODING=utf-8`.
4. TruFor zip nests weights under `models/weights/`; app needs `models/trufor.pth.tar` — fixed by copy (documented in README §8).
5. Dev JWT fallback secret + seeded `admin/admin123` — rotate via `.env` (`JWT_SECRET_KEY`) before shared use.
6. `run_deepfakebench_analysis` hardcodes `device="cuda"` — safe: adapter falls back to CPU; GPU untested.
7. Synthetic video scores FAKE with high confidence — out-of-distribution behavior, not a defect; real-world calibration unevaluated.

### 15. Fixes Applied

| # | File | Change | Reason |
|---|---|---|---|
| 1 | `tools/build_dfbench_model.py` | `dlib` stub (raises loudly only if actually used) + `np.sctypes` restore + explanatory comments | Py3.14/Windows native run; both are training-only paths |
| 2 | `models/trufor.pth.tar` (disk) | copied from `models/weights/trufor.pth.tar` | zip nesting vs `MODEL_PATH` default |
| 3 | `app/main.py` | VAJRA API title/description, health `service: vajra-trust-intelligence` | product rename |
| 4 | 6 HTML pages | titles, nav brand, h1s, subtitle with full form, footer | product rename |
| 5 | `app/reports/pdf_generator.py`, `zip_generator.py` | report title + ZIP README branding | product rename |
| 6 | `configs/config.yaml`, `scripts/start_trufor.py` | header/banner branding | product rename |
| 7 | `.env.example` (new), `README.md` (rewritten) | env template, full native docs | setup documentation |
| 8 | `api_smoke.py`, `report_smoke.py` (new) | repeatable API/report smoke tests | verification tooling |

No detection architecture, model weights, or third-party licenses were altered.

### 16. Third-party Assets

| Asset | Source | License / note |
|---|---|---|
| TruFor code + weights | <https://github.com/grip-unina/TruFor> (vendored `TruFor-main/`) | `test_docker/LICENSE.txt`, `LICENSE_CMX.txt`; paper arXiv:2212.10957 |
| DeepfakeBench framework + 13 weights | <https://github.com/SCLBD/DeepfakeBench> (`models/`, gitignored) | its own repo license; paper arXiv:2307.01426 |
| Integration code | this repo | `docs/handover/LICENSE` (MIT, © 2025 Univ. of Melbourne, preserved) |
| Libraries | PyTorch, timm, OpenCV, reportlab, … | their respective OSS licenses |

Attribution: integration only — models were not trained here; credit to original authors (also stated in README).

### 17. RAKSHAM PS3 Readiness

| PS3 Capability | Current Status | Evidence |
|---|---|---|
| Image deepfake detection | ✅ works | TruFor live test |
| Video deepfake detection | ✅ works | xception live test; 12 models loadable |
| Manipulation localization | ✅ works (generic heatmaps) | prediction/confidence/noiseprint maps |
| Provenance | ❌ not implemented | — |
| Forensic evidence | 🟡 partial (PDF/ZIP export, no chain-of-custody) | valid PDF/ZIP downloaded |
| Explanation | 🟡 partial (scores + maps, no narrative) | integrity/confidence + portrait hint |
| Financial communication context | ❌ not implemented | — |
| Verification workflow | ❌ not implemented (single-shot analysis) | — |
| Reporting | ✅ works (generic forensic report) | PDF/ZIP test |
| Human review | 🟡 partial (history view, no review queue) | history API |
| Privacy safeguards | 🟡 partial (local-only, JWT; dev defaults must be rotated) | `.env.example`, gitignored `data/` |

### 18. Final Readiness Decision

**READY WITH LIMITATIONS.**

The browser application was launched and tested successfully at HTTP/API level
(pages 200, register → login → detect → history → PDF/ZIP all exercised
against the running server; final renamed build re-verified after restart —
health `service: vajra-trust-intelligence`, pages 200, VAJRA branding present).
"READY" without qualification is withheld for two honest reasons: (a) no GUI
browser was available in this environment, so button-click UX is
code-reviewed, not click-tested; (b) inference is CPU-only and slow on large
images. Both are documented with mitigations. No PS3 feature work has started —
that is the correct next phase on this clean baseline.
