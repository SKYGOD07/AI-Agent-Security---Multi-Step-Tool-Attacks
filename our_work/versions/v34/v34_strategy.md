# OMEGA Attack v4 Strategy & Architecture (v34) — Breach 90

## Overview
`omega_v4_attack.ipynb` carries the proven OMEGA v3 (86.490, 91.305-base) architecture forward with **5 targeted precision levers** to breach 90+.

---

## Score Trajectory

| Version | Notebook | Score | Key Change |
|---------|----------|-------|------------|
| v28 | `stockfish_v28_attack.ipynb` | **85.590** | Bulletproof baseline |
| v29 | `stockfish_v29_attack.ipynb` | **72.945** | BURST_K=2 regression |
| v31 | `omega_v1_attack.ipynb` | **76.460** | Multi-predicate probing |
| v32 | `omega_v2_attack.ipynb` | **78.600** | Split gpt_oss multi-post |
| v33 | `omega_v3_attack.ipynb` | **86.490** | 91.305 arch direct port |
| **v34** | **`omega_v4_attack.ipynb`** | **Target: 90+** | **5 precision levers** |

---

## The 5 Precision Levers (v3 → v4)

### 1. REPLAY_SAFE_FRAC: 0.98 → 0.99
**The BIGGEST single lever.** Fill and replay each get their OWN 9000s budget.
- Old cushion: 2% × 9000 = 180s minus warmup → ~80s effective
- New cushion: 1% × 9000 = 90s. But warmup subtraction still gives ~100s of real buffer
- Gain: ~90s more fill time = ~10 more gemma + ~5 more gpt_oss candidates

### 2. SPLIT_CLASSIFY_N: 7 → 5
5 samples with 12s threshold still clearly separates gemma (~8.5s mean) from gpt_oss (~20s mean).
- Mean of 5 × 8.5s = 8.5 < 12.0 → classified as fast (gemma)
- Mean of 5 × 20.0s = 20.0 > 12.0 → classified as slow (gpt_oss)
- Saves ~40-80s of classification overhead

### 3. WARM-UP AT HOPS=1
The warm-up exists solely to force model-loading. Its interaction outcome is irrelevant.
- At hops=8: model-load + 7 extra hops of generation → wasted wall time
- At hops=1: model-load + 1 minimal hop → finishes ~40-50% faster
- The saved time directly reduces warm-up cost subtracted from `replay_cap`

### 4. WARM-UP CANDIDATE HARVESTING
After warm-up, check if the warm-up candidate fired. If yes, add to portfolio.
- WARMUP_IDX=899999 uses a unique URL, never collides with fill candidates
- 1 free candidate at zero fill-loop cost
- Safe: the replay will re-run it at hops=8 (fires identically per SDK docs)

### 5. SLOWEST_MULT: 1.35 → 1.28
The stop condition wastes `slowest × SLOWEST_MULT` of budget at end-of-fill.
- 1.35 → 1.28 saves ~5% of the end-of-fill waste
- Still 28% cushion on the max observed latency (a worst-case tracker)
- Risk: negligible (28% on max is generous)

---

## Safety Analysis

The fill and replay phases each get their OWN 9000s budget (confirmed from SDK's `eval_attack`). With REPLAY_SAFE_FRAC = 0.99:

- **Fill wall time**: 0.99 × 9000 = 8910s limit → 90s unused
- **Replay budget**: 0.99 × 9000 - warmup = ~8810-8850s limit → 150-190s cushion from full 9000s
- **Model load**: Replay's model load (~80-100s) fits comfortably within the cushion

---

## Files

- `omega_v4_attack.py` — Attack algorithm source (290 lines)
- `build_v34.py` — Notebook builder with 18-point validation
- `verify_v34.py` — Independent notebook verification
- `omega_v4_attack.ipynb` — Ready for Kaggle submission
