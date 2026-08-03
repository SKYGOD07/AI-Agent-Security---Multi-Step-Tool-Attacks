# AI Agent Security - Multi-Step Tool Attacks
## Red-Team Discovery Engine & Kaggle Competition Architecture

This repository contains the full research, engineering, and submission pipeline for the Kaggle competition **"AI Agent Security - Multi-Step Tool Attacks"**.

---

## 📄 Master Handoff Thesis & Documentation
If you are an AI model (e.g., NVIDIA models running in Claude Code via Ollama) or developer taking over this workspace, read the comprehensive 1000+ line handoff thesis:

👉 **[MASTER_AI_HANDOFF_THESIS.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/MASTER_AI_HANDOFF_THESIS.md)**

Additional documentation:
- 📊 **[ANALYSIS_REPORT.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/ANALYSIS_REPORT.md)**: Executive research overview & score progression.
- 📐 **[docs/SCORING_AND_EVALUATION.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/docs/SCORING_AND_EVALUATION.md)**: Mathematical scoring specification.
- 📚 **[docs/notebook_algorithms/COMPREHENSIVE_NOTEBOOK_CATALOG.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/docs/notebook_algorithms/COMPREHENSIVE_NOTEBOOK_CATALOG.md)**: Catalog of all notebook versions (v11 through v29).
- 🛑 **[projects/AI-Agent-Security---Multi-Step-Tool-Attacks/skills/failure_blacklist.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/projects/AI-Agent-Security---Multi-Step-Tool-Attacks/skills/failure_blacklist.md)**: Failure post-mortems and mandatory rules.

---

## 🚀 Active Version: v29 (`stockfish_v29_attack.ipynb`)
- **Target Score**: **90.090+**
- **Decoded Source**: `our_work/jed_attack_decoded_v29.py`
- **Build Script**: `our_work/build_v29.py`
- **Key Breakthrough**: Asymmetric Dual-Track Multi-Post Routing
  - `SLOW_MULTIPOST_N = 4` for `gpt_oss` via token-forged analysis channels (**72 raw points / candidate**).
  - `BURST_K = 2` for `gemma` via burst imperative formatting (**36 raw points / candidate**).
- **Protection**: Base64 encoding + defensive import cascades + defensive `__init__` (Zero Format Errors).

---

## 🛠️ How to Build and Submit
To generate and build notebook `v29`:
```bash
python our_work/build_v29.py
```
This produces `our_work/notebooks/stockfish_v29_attack.ipynb`. Submit to Kaggle with **GPU T4 x2** and **Internet Off**.
