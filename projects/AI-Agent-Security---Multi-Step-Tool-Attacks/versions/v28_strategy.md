# v28 Strategy: v69 Architecture + jedforce-1 Scaffolding

## Overview
- **Notebook**: `stockfish_v28_attack.ipynb`
- **Script**: `jed_attack_decoded_v28.py`
- **Build Script**: `build_v28.py`
- **Public Score**: 85.590

## Strategy & Key Innovations
- Combined v69 live validation-fill algorithm with `jedforce-1` defensive scaffolding.
- Added base64 string encoding, defensive try/except imports, and defensive `__init__`.
- Relaxed margins slightly (`MARGIN_S = 44.0`, `FILL_BUDGET_FRAC = 0.96`) to eliminate format errors.

## Outcome & Failure Post-Mortem
- Succeeded cleanly without format errors, scoring **85.590**.
- **Regression Analysis vs 90.09**: `v28` explicitly set `BURST_K = 1` and `SLOW_MULTIPOST_N = 1`, limiting each candidate to only 1 `http.post` call (18 raw points).
- **Lesson**: Restricting multi-post density caps the maximum possible score. We must re-enable dual-track multi-post routing (`BURST_K = 2` for gemma, `SLOW_MULTIPOST_N = 4` for gpt_oss).
