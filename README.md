# AI Agent Security - Multi-Step Tool Attacks
## Red-Team Discovery Engine & Kaggle Competition Architecture

This repository contains the full research, engineering, and submission pipeline for the Kaggle competition **"AI Agent Security - Multi-Step Tool Attacks"**.

---

## 📄 Master Handoff Thesis & Documentation
If you are an AI model or developer taking over this workspace, read the comprehensive handoff documentation:

- 🏆 **[FAILURES_AND_LESSONS.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/FAILURES_AND_LESSONS.md)**: Master OMEGA Series post-mortem & failure guide.
- 📚 **[our_work/docs/failure_analysis_and_knowledge_base.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/our_work/docs/failure_analysis_and_knowledge_base.md)**: Complete version progression & failure taxonomy (v4–v43).
- 🛑 **[projects/AI-Agent-Security---Multi-Step-Tool-Attacks/skills/failure_blacklist.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/projects/AI-Agent-Security---Multi-Step-Tool-Attacks/skills/failure_blacklist.md)**: Failure post-mortems and mandatory rules.
- 📐 **[docs/SCORING_AND_EVALUATION.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/docs/SCORING_AND_EVALUATION.md)**: Mathematical scoring specification.

---

## 🚀 Active Version: v43 (`omega_v13_attack.ipynb`)
- **Peak Score Benchmark**: **89.955** (v11)
- **Target Score**: **90.600+** (v13 Incremental Goal Edition)
- **Source Code**: `our_work/versions/v43/omega_v13_attack.py`
- **Build Script**: `our_work/versions/v43/build_v43.py`
- **Strategy Specs**: `our_work/versions/v43/v43_strategy.md`
- **Key Breakthrough**: High-Precision Latency-Split Single-Post Fill
  - `REPLAY_SAFE_FRAC = 0.994` (8946s replay cap $\rightarrow$ reclaims +27s of budget).
  - `SLOWEST_MULT = 1.10` (tightens end-of-fill cushion $\rightarrow$ +1.5 candidates).
  - `SPLIT_CLASSIFY_N = 1` (saves 1 classification cycle $\rightarrow$ +1.5 candidates).
  - `SLOWEST0 = 12.0` (tighter initial latency seed $\rightarrow$ +1.0 candidate).
- **Protection**: Base64 encoding + defensive import cascades + defensive `__init__` + 0% timeout risk.

---

## 🛠️ How to Build and Submit
To generate and build notebook `v43`:
```bash
python our_work/versions/v43/build_v43.py
```
This produces `our_work/notebooks/omega_v13_attack.ipynb`. Submit to Kaggle with **GPU T4 x2** and **Internet Off**.
