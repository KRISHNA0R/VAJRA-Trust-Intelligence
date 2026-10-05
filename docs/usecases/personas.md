# Forensic Deepfake Detector — Personas 

## Overview

| Persona | Primary Goals | Key Tasks | Mapped Use Cases |
|---|---|---|---|
| **Alex Chen (Investigator)** | Fast triage, clear visual evidence, offline usability | Upload, track job status, review heatmaps and timeline, download report | UC1, UC2, UC3, UC4, UC5, UC6, UC9 |
| **Priya Singh (Forensic Analyst / Technical)** | Reproducibility and threshold tuning | Adjust analysis settings, re-run, generate metadata | UC1, UC4, UC7, UC8 |
| **Michael Nguyen (Admin / IT)** | Local/offline basics, logging and health visibility | View logs and system health | UC1, UC10 |

---

## Persona — Alex Chen (Digital Investigator)

**Goals**
- Triage large volumes quickly  
- Identify deepfake cues with clear visuals (heatmaps and timeline)  
- Export defensible reports; work offline

**Key Tasks**
- Upload media; track job status  
- Review heatmaps and timeline peaks  
- Download report

**Pain Points**
- Time pressure; unclear scores; fragmented tools

**Success Metrics**
- Lower review time; audit trail present; fewer reworks

**Primary Scenario**
1) Login  
2) Upload file and start analysis  
3) Watch processing status  
4) Open results  
5) Inspect timeline peaks and heatmaps  
6) Download PDF report

---

## Persona — Priya Singh (Forensic Analyst / Technical)

**Goals**
- Tune thresholds; reproduce runs

**Key Tasks**
- Adjust analysis settings (model and thresholds)  
- Re-run analysis with fixed settings  
- Generate metadata package (configuration, logs, checksums)

**Pain Points**
- Black-box models; scattered settings

**Success Metrics**
- Consistent scores across runs; documented settings

**Primary Scenario**
1) Login  
2) Open existing task  
3) Adjust settings  
4) Re-run analysis with fixed settings  
5) Generate metadata package

---

## Persona — Michael Nguyen (Admin / IT)

**Goals**
- Offline/local operation basics; logging and health visibility

**Key Tasks**
- View logs and system health dashboards

**Pain Points**
- Limited on-prem resources; security reviews

**Success Metrics**
- One-command local start; logs and basic metrics available

**Primary Scenario**
1) Login (Admin)  
2) Open system health page  
3) Review error logs and metrics

---

## Minimal Use-Case List (Sequential)

- **UC1 Authenticate** — User signs in (Investigator, Analyst, or Admin).  
- **UC2 Upload Media** — Validate file, start a job, return a task ID.  
- **UC3 Track Job Status** — Show progress and handle failures.  
- **UC4 View Results** — Display image/video outputs and overlays.  
- **UC5 Explore Timeline and Frames** — Navigate peaks and open key frames.  
- **UC6 Generate and Download Report** — Export HTML/PDF with metadata and visuals.  
- **UC7 Generate Metadata** — Produce a metadata package (configuration, logs, checksums) for traceability.  
- **UC8 Re-run Analysis with Fixed Settings** — Reprocess using saved settings (no changes during the run).  
- **UC9 Inspect Heatmaps (Investigator)** — Open heatmap overlays for selected frames, adjust intensity/threshold view, save a representative heatmap snapshot to the report.  
- **UC10 View Logs and System Health** — Inspect structured logs and basic health metrics (errors, CPU/memory, queue length).

---

## Traceability

| Epic | Related Use Cases |
|---|---|
| Prototype and Information Architecture | UC2, UC4, UC5, UC6, UC9 |
| Ingestion and Preprocessing | UC2, UC3 |
| Detection Engine (MVP) | UC4, UC5, UC8 |
| Visualization | UC4, UC5, UC9 |
| Reporting and Export | UC6, UC7 |
| Offline and Operations | UC10 |
