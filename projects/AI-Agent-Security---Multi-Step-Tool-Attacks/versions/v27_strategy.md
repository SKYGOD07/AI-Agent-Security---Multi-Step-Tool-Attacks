# v27 Strategy: v69 Architecture Adoption & Margin Squeezing

## Overview
- **Notebook**: `stockfish_v27_attack.ipynb`
- **Script**: `jed_attack_decoded_v27.py`
- **Build Script**: `build_v27.py`
- **Public Score**: Submission Format Error (0.000)

## Strategy & Key Innovations
- Wholesale adoption of the `v69/ea-b` architecture (88.200 scorer).
- Switched back to single-URL per candidate with per-model latency routing and Harmony token forging.
- Tightened margins: `MARGIN_S = 42.0`, `FILL_BUDGET_FRAC = 0.97`, `MARGIN_FLOOR_MIN = 3.0`.

## Outcome & Failure Post-Mortem
- Returned **Submission Format Error**.
- **Root Cause**:
  1. Direct SDK imports (`from aicomp_sdk.attacks.contracts import ...`) crashed on Kaggle's evaluation environment when SDK module paths differed.
  2. Missing defensive `__init__` caused `self.config` lookup failures.
  3. Over-aggressive margin tightening caused replay budget overruns.
- **Lesson**: Always use try/except defensive imports, base64 encoding, and robust `__init__` wrappers.
