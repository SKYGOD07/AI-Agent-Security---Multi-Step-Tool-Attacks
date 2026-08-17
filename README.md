# AI Agent Security - Multi-Step Tool Attacks
## Red-Team Discovery Engine & Kaggle Competition Architecture — OMEGA v13 Peak: 91.170

This repository contains the full research, engineering, and submission pipeline for the Kaggle competition **"AI Agent Security - Multi-Step Tool Attacks"**.

---

## 📄 Documentation Index
- 🏆 **[FAILURES_AND_LESSONS.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/FAILURES_AND_LESSONS.md)**: Master OMEGA Series post-mortem & failure guide.
- 📚 **[our_work/docs/failure_analysis_and_knowledge_base.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/our_work/docs/failure_analysis_and_knowledge_base.md)**: Complete version progression & failure taxonomy (v4–v43).
- 📐 **[docs/SCORING_AND_EVALUATION.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/docs/SCORING_AND_EVALUATION.md)**: Mathematical scoring specification.
- 📖 **[MASTER_AI_HANDOFF_THESIS.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/MASTER_AI_HANDOFF_THESIS.md)**: Comprehensive handoff thesis for successor AI models.
- 🛑 **[projects/.../skills/failure_blacklist.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/projects/AI-Agent-Security---Multi-Step-Tool-Attacks/skills/failure_blacklist.md)**: Permanent failure rules.

---

## 🚀 Active Version: v43 / OMEGA v13 — Peak Score: 91.170 🏆
- **Confirmed Scores**: **91.170** (best run) / **89.685** (variance run)
- **Source Code**: `our_work/versions/v43/omega_v13_attack.py`
- **Build Script**: `our_work/versions/v43/build_v43.py`
- **Strategy**: `our_work/versions/v43/v43_strategy.md`
- **Architecture**: Latency-Split Single-Post Validation-Fill
  - `REPLAY_SAFE_FRAC = 0.994` (8946s replay cap, 54s safety cushion).
  - `SLOWEST_MULT = 1.10` (tightened end-of-fill cushion).
  - `SPLIT_CLASSIFY_N = 1` (1-sample classification at 12.0s threshold).
  - `SLOWEST0 = 12.0` (tighter initial latency seed).
- **Protection**: Base64 encoding + defensive import cascades + defensive `__init__`.

---

## 🛠️ How to Build and Submit
```bash
python our_work/versions/v43/build_v43.py
```
This produces `our_work/notebooks/omega_v13_attack.ipynb`. Submit to Kaggle with **GPU T4 x2** and **Internet Off**.
