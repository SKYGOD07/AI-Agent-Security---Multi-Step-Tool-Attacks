# v26 Strategy: Dual-URL Replay-Recalibrated scenario

## Overview
- **Notebook**: `stockfish_v26_attack.ipynb`
- **Script**: `jed_attack_decoded_v26.py`
- **Build Script**: `build_v26.py`
- **Public Score**: 57.210

## Strategy & Key Innovations
- Attempted to use dual-URL templates (2 endpoints per candidate) to double raw score density.
- Recalibrated replay budget: `REPLAY_SAFE = 0.92` and `REPLAY_COST_COEF = 1.15`.

## Outcome & Failure Post-Mortem
- Score dropped to **57.210** (regression from v24's 84.645).
- **Root Cause**: Dual-URL templates caused models to fail execution of both HTTP POST calls, lowering the fire rate. Squeezing replay budget with 1.15 multiplier reduced total returned candidate count.
- **Lesson**: Dual-URL templates without token forging are a dead end. Single-URL or token-forged multi-post is far superior.
