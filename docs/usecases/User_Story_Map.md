# User Story Map — Deepfake Investigation Tool
Generated: 2025-09-27 05:33

## Backbone (Activities)
1) Setup & Constraints → 2) Ingest Media → 3) Analyze → 4) Review Results → 5) Report & Share → 6) Manage & Scale

### Setup & Constraints
- **US-04** Offline-only (Must) — **V1 Done**
- **US-11** Modest hardware (Should) — Next

### Ingest Media
- **US-01** Upload image → Heatmap/Confidence/Score (Must) — **V2 Done**
- **US-08** Upload short video (Should) — Next
- **US-09** Object persistence checks (Could) — Next

### Analyze
- **US-13** Model switching (TruFor/ResNet) (Should) — **V2 Done**

### Review Results
- **US-02** Heatmap overlay + legend/threshold (Must) — **V2 Done**
- **US-03** Confidence map (Should) — **V2 Done**
- **US-07** Metadata view (Should) — In Progress (Next)

### Report & Share
- **US-06** Export report (Should) — In Progress (Next)
- **US-05** Secure sharing (Should) — Planned (Next)

### Manage & Scale
- **US-14** Project-scoped storage (Should) — Planned (Next)
- **US-12** Batch processing (Could) — Planned (Next)
- **US-10** Large-file UX (Should) — In Progress (Next)

## Mermaid View
```mermaid
flowchart TB
  subgraph Setup & Constraints
    US04["US-04 Offline-only (Must) ✅ V1"]
    US11["US-11 Modest hardware (Should) ⏳ Next"]
  end
  subgraph Ingest Media
    US01["US-01 Upload image → Heatmap/Conf/Score (Must) ✅ V2"]
    US08["US-08 Upload short video (Should) 🗓 Next"]
    US09["US-09 Object persistence (Could) 🗓 Next"]
  end
  subgraph Analyze
    US13["US-13 Model switching (Should) ✅ V2"]
  end
  subgraph Review Results
    US02["US-02 Heatmap overlay+legend (Must) ✅ V2"]
    US03["US-03 Confidence map (Should) ✅ V2"]
    US07["US-07 Metadata (Should) ⏳ Next"]
  end
  subgraph Report & Share
    US06["US-06 Export report (Should) ⏳ Next"]
    US05["US-05 Secure sharing (Should) 🗓 Next"]
  end
  subgraph Manage & Scale
    US14["US-14 Projects (Should) 🗓 Next"]
    US12["US-12 Batch (Could) 🗓 Next"]
    US10["US-10 Large-file UX (Should) ⏳ Next"]
  end

  US04 --> US01 --> US02 --> US03 --> US06
  US01 --> US13
  US08 --> US09
```
