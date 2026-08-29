# AI Agent Security - Multi-Step Tool Attacks
## Candidate Discovery Engine & Kaggle Competition Architecture — OMEGA v22 Peak: 91.305 🏆

This repository contains the full research, engineering, and submission pipeline for the Kaggle competition **"AI Agent Security - Multi-Step Tool Attacks"**.

---

## 📄 Documentation Index
- 🏆 **[FAILURES_AND_LESSONS.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/FAILURES_AND_LESSONS.md)**: Master OMEGA Series post-mortem & failure guide.
- 📚 **[our_work/docs/failure_analysis_and_knowledge_base.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/our_work/docs/failure_analysis_and_knowledge_base.md)**: Complete version progression & failure taxonomy (v4–v53).
- 📐 **[docs/SCORING_AND_EVALUATION.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/docs/SCORING_AND_EVALUATION.md)**: Mathematical scoring specification.
- 📖 **[MASTER_AI_HANDOFF_THESIS.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/MASTER_AI_HANDOFF_THESIS.md)**: Comprehensive handoff thesis for successor AI models.
- 🛑 **[projects/.../skills/failure_blacklist.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/projects/AI-Agent-Security---Multi-Step-Tool-scenarios/skills/failure_blacklist.md)**: Permanent failure rules.

---

## 🚀 Active Version: v52 / OMEGA v22 — Peak Score: 91.305 🏆
- **Confirmed Scores**: **91.305** (v22 Peak) / **91.125** (v23) / **91.170** (v13)
- **Source Code**: `our_work/versions/v52/omega_v22_attack.py`
- **Build Script**: `our_work/versions/v52/build_v52.py`
- **Strategy**: `our_work/versions/v52/v52_strategy.md`
- **Architecture**: Two-Phase Backfill Sizing + Latency-Split Single-Post Validation-Fill
  - `PRIMARY_REPLAY_FRAC = 0.945` (safe primary segment).
  - `BACKFILL_REPLAY_FRAC = 0.995` / `BACKFILL_WALL_FRAC = 0.997` (converts idle window to +3-5 candidates).
  - `SPLIT_CLASSIFY_N = 1` (1-sample classification at 12.0s threshold).
  - `SLOWEST0 = 12.0` & latency-ascending submission ordering.
- **Protection**: Base64 encoding + defensive import cascades + defensive `__init__`.

---

## 🛠️ How to Build and Submit
```bash
python our_work/versions/v52/build_v52.py
```
This produces `our_work/notebooks/omega_v22_attack.ipynb`. Submit to Kaggle with **GPU T4 x2** and **Internet Off**.
