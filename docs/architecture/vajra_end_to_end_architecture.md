# VAJRA Trust Intelligence — End-to-End System Architecture

**Status:** as-built, October 2026. Single-machine native run (Windows 11, Python 3.14, CPU-only).
`Verification & AI-based Judgement for Risk Assessment` · RAKSHAM PS3.

```mermaid
flowchart TB
    subgraph USER["Analyst Browser (http://localhost:8000)"]
        HOME["Home<br/>index_main.html<br/>3 engines + trust strip"]
        LOGIN["Login / Register<br/>JWT in localStorage"]
        IMG["Images (TruFor)<br/>index.html<br/>upload + heatmaps"]
        VID["Video (DeepfakeBench)<br/>deepfakebench.html<br/>12 models + timeline"]
        AUD["Audio (Voice Spoof)<br/>audio.html<br/>upload + window scores"]
        HIST["History<br/>history.html<br/>stats + Risk column + PDF/ZIP"]
    end

    subgraph SERVER["FastAPI + Uvicorn :8000 (app/main.py, 34 routes)"]
        direction TB
        STATIC["Static server<br/>GET /web/*.html<br/>GET /web/css/vajra-theme.css"]
        AUTH["Auth<br/>POST /api/auth/register<br/>POST /api/auth/login<br/>roles: analyst/investigator/admin<br/>data/users.json + data/sessions/"]
        DETECT["POST /detect<br/>image ≤10 MB"]
        DFB["POST /api/deepfakebench/analyze<br/>video ≤500 MB<br/>async job + polling"]
        AAUD["POST /api/audio/analyze<br/>audio ≤50 MB<br/>inline inference"]
        STATUS["GET /health<br/>GET /api/models/status<br/>GET /api/audio/models"]
        REPO["GET /api/reports/{id}/pdf<br/>GET /api/reports/{id}/zip<br/>GET /api/history"]
    end

    subgraph PIPE["Detection pipelines"]
        direction TB
        TRUFOR["TruForAdapter<br/>detconfcmx (SegFormer-B2 + Noiseprint++)<br/>512px pad → anomaly/confidence maps"]
        BENCH["DeepfakeBenchAdapter<br/>12 detectors (Xception…CORE)<br/>fps sampling → per-frame P(fake)<br/>segments + keyframes"]
        DHWANI["AudioSpoofAdapter (Dhwani)<br/>XLS-R + AASIST, ONNX Runtime<br/>16 kHz mono, 3 s windows → P(fake)"]
        RISK["Risk engine (app/utils/risk.py)<br/>CRITICAL ≥0.8 · HIGH ≥0.5<br/>MEDIUM · LOW ≤0.2<br/>+ response playbook"]
    end

    subgraph STORE["Runtime data (gitignored)"]
        JOBS["data/jobs/{job_id}/<br/>heatmaps · keyframes · timeline.json<br/>audio_scores.json · report.pdf/.zip"]
        HIST2["history metadata<br/>(verdict, score, risk_level)"]
    end

    subgraph MODELS["Model weights on disk (gitignored, never committed)"]
        W1["models/trufor.pth.tar<br/>~268 MB, 952 tensors"]
        W2["models/vendors/DeepfakeBench/<br/>training/weights/ (13 × .pth)<br/>+ pretrained xception backbone"]
        W3["models/audio_dhwani/best_model.onnx<br/>~1.26 GB (MIT)"]
    end

    subgraph REPORTS["Evidence generation"]
        PDF["reportlab PDF<br/>verdict + scores + Risk Assessment<br/>+ recommended actions + visuals"]
        ZIP["ZIP package<br/>metadata + timeline + report.pdf<br/>+ heatmaps/keyframes"]
    end

    HOME --> LOGIN
    LOGIN --> IMG & VID & AUD
    IMG --> DETECT
    VID --> DFB
    AUD --> AAUD
    IMG & VID & AUD & HIST --> STATUS
    HIST --> REPO

    DETECT --> TRUFOR
    DFB --> BENCH
    AAUD --> DHWANI
    TRUFOR & BENCH & DHWANI --> RISK

    DETECT & DFB & AAUD --> JOBS
    RISK --> HIST2
    HIST2 --> REPO
    REPO --> PDF & ZIP
    PDF & ZIP --> HIST

    TRUFOR -. loads .-> W1
    BENCH -. loads .-> W2
    DHWANI -. loads .-> W3

    style RISK fill:#FDBA74,stroke:#C2410C,stroke-width:2px
    style DHWANI fill:#FFEDD5,stroke:#C2410C
```

## Component map

| Layer | Component | File(s) | Notes |
|---|---|---|---|
| UI | 7 pages, vanilla JS + DaisyUI CDN | `app/web/*.html`, `app/web/css/vajra-theme.css` | Same-origin `fetch` — no CORS; orange theme, black-text fixes |
| API | FastAPI app, 34 routes | `app/main.py` | Serves UI + API on `:8000`; `PYTHONIOENCODING=utf-8` on Windows |
| Auth | JWT, 3 roles, seeded `admin/admin123` | `app/auth/`, `data/users.json` | Rotate `JWT_SECRET_KEY` (see `.env.example`) before shared use |
| Image | TruFor adapter | `app/adapters/trufor_adapter.py`, `TruFor-main/` | Anomaly + confidence + Noiseprint++ maps per job |
| Video | DeepfakeBench adapter | `app/adapters/deepfakebench_adapter.py`, `tools/build_dfbench_model.py` | dlib stub + `np.sctypes` shim for Py3.14 (training-only deps) |
| Audio | Dhwani ONNX adapter | `app/adapters/audio_adapter.py` | FFmpeg fallback decode; validated 4/4 HI+EN |
| Risk | Level + playbook | `app/utils/risk.py` | Attached in API, history, PDF, and all 3 result UIs |
| Reports | PDF + ZIP | `app/reports/` | Risk section included; `%PDF-`/`PK` verified |
| Data | Jobs + history JSON | `data/jobs/`, `data/*.json` | Gitignored; wipe via `scripts/clean_test_data.ps1` (review first) |
| Tests | Smoke + fixtures | `api_smoke.py`, `report_smoke.py`, `audio_e2e.py`, `audio_verify.py`, `test_*.wav` | Rerunnable verification |

## Key request flows

1. **Image:** Browser → `POST /detect` → TruForAdapter → heatmaps to `data/jobs/{id}/` → risk attach → JSON (verdict, maps, risk, actions) → history + UI render.
2. **Video:** Browser → `POST /api/deepfakebench/analyze` → `{job_id}` immediately → ThreadPool worker (model load ~1 min first time) → progress via `progress.json` polling → segments/keyframes/`timeline.json` → risk attach → UI timeline + History.
3. **Audio:** Browser → `POST /api/audio/analyze` → Dhwani ONNX (seconds, CPU) → window scores → risk attach → UI verdict + actions + History.
4. **Evidence:** History → `GET /api/reports/{id}/pdf|zip` → generated on first request, then served.

## Verified numbers (this build)

- Image: REAL 0.64 integrity (live API) · Video: 20 frames / 15.6 s CPU · Audio matrix 4/4 (REAL 0.0002–0.0004, FAKE 0.78–0.99) · PDF 1.39 MB · ZIP 1.12 MB · all pages HTTP 200.
