# Handoff Packet: evaluation AI Agent Security Engine (Updated Aug 2026)

> **IMPORTANT**: The primary comprehensive handoff and failure analysis documents are:
>
> 🏆 **[FAILURES_AND_LESSONS.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/FAILURES_AND_LESSONS.md)** — Master OMEGA post-mortem & architecture guide.
> 📚 **[failure_analysis_and_knowledge_base.md](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/our_work/docs/failure_analysis_and_knowledge_base.md)** — Complete version taxonomy (v4–v43).

## Quick Handoff Summary
- **Current Version**: `omega_v13_attack.ipynb` (v43) — **Peak Public Score: 91.170**
- **Key Architecture**: Latency-Split Single-Post Validation-Fill with high-precision replay-safe sizing.
- **Key Parameters**: `REPLAY_SAFE_FRAC = 0.994`, `SLOWEST_MULT = 1.10`, `SPLIT_CLASSIFY_N = 1`, `SLOWEST0 = 12.0`.
- **Scaffolding**: Base64 scenario encoding + defensive `try/except` imports + defensive `__init__` (Zero Format Error Guarantee).
- **Build Command**: `python our_work/versions/v43/build_v43.py`
