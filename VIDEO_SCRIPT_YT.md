# 🎬 VAJRA Trust Intelligence — 2-Minute Demo Video Script

**Format:** Screen recording with voiceover, ~130 words/minute ≈ 260 words total.
**Setup before recording:** server running (`python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`),
browser open at `http://localhost:8000/web/login.html`, logged OUT (clear site data once so the
login page shows). Keep two test files on the Desktop: one photo and one short voice clip.
Login credentials for the demo: `admin` / `admin123`.

---

## 0:00–0:15 — Hook + Login (15 sec)

**[Show: login page, slogan rotating in the box]**
> "Every day, fake images, doctored videos and cloned voices scam people and companies.
> Meet **VAJRA Trust Intelligence** — Verification and AI-based Judgement for Risk Assessment —
> our deepfake detector for financial communications. Everything runs on this machine — your
> media never leaves it. Let me log in as admin and show you."

**[Action: type admin/admin123, click Login → lands on Home]**

## 0:15–0:35 — Home: three detection engines (20 sec)

**[Show: home page, scroll slowly across the three cards + trust strip]**
> "The home page offers three forensic engines. **TruFor** for images, with pixel-level
> forgery localization. **DeepfakeBench** — twelve specialised models for video.
> And **Voice Spoof** — our multilingual detector that catches cloned speech in Hindi,
> English, Tamil, Telugu and Malayalam. JWT-secured, on-premise, with court-ready evidence reports."

## 0:35–1:00 — Image detection (25 sec)

**[Action: click TruFor card → Images page → upload a photo → wait for result]**
> "First, image forensics. I upload a photo. TruFor analyses noise patterns and compression
> traces, and returns a verdict — REAL or FAKE — with a confidence score, plus heatmaps showing
> exactly *where* the image was manipulated: the anomaly map, the confidence map, and the
> Noiseprint analysis. Every result is saved to History automatically."

## 1:00–1:25 — Video detection (25 sec)

**[Action: go to Video page → pick the Xception model → upload a short clip → show progress → frame scores + suspicious segments]**
> "Next, video. I pick a model — say Xception — and upload a clip. The engine samples frames,
> scores each one, and flags suspicious time segments with keyframes, so an analyst jumps
> straight to the doctored seconds instead of watching the whole video."

## 1:25–1:45 — Voice spoof detection (20 sec)

**[Action: go to Audio page → upload the Hindi voice clip → result appears]**
> "And the newest engine — voice. I upload a Hindi clip. The Dhwani model scores it in
> three-second windows and declares it REAL at near-zero spoof probability — or FAKE at
> ninety-nine percent for a cloned voice. Critical for fraud calls and fake CEO voice notes."

## 1:45–2:00 — History + reports + close (15 sec)

**[Action: open History → show stats + table → download the PDF → flash the PDF open]**
> "Everything lands in History — stats, verdicts, scores. One click downloads a forensic PDF
> report or a ZIP evidence package with all artefacts. VAJRA Trust Intelligence — don't trust
> the clip, verify it. Links and docs in the description. Thank you!"

---

### Recording checklist
- [ ] 1920×1080, browser zoom 100%, hide bookmarks bar for a clean frame
- [ ] Log out first so the video starts at the login page with a rotating slogan visible
- [ ] Pre-upload once off-camera so model weights are warm (no long loading on tape)
- [ ] Use the Hindi fake clip on the Audio page for the strongest reaction (99% FAKE)
- [ ] End card: product name + full form + "Built for RAKSHAM PS3"
