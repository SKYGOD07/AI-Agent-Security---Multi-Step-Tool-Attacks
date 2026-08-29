# OMEGA scenario v14 Strategy (v44) — Precision Squeeze Edition (Target 91.665+)

## Builds on v13 Confirmed Peak: 91.170 🏆

v13 scored **91.170** (best run) and **89.685** (variance run) — confirming the latency-split single-post architecture as the winning path.

---

## Three Surgical Increments over v13

| Parameter | v13 (91.170) | v14 (Target) | Gain |
|---|---|---|---|
| `REPLAY_SAFE_FRAC` | 0.994 (8946s cap) | **0.996** (8964s cap) | +18s budget → **+2 candidates** |
| `SLOWEST_MULT` | 1.10 | **1.05** | Tighter end-of-fill → **+1 candidate** |
| `REPLAY_COST_COEF` | 1.00 | **0.97** | Replay warmer than fill → **+2-3 candidates** |

**Why `REPLAY_COST_COEF = 0.97`?**
During the fill phase, `replay_cost` tracks measured candidate latency. But during Kaggle's replay phase, the model is already loaded and warm (no cold-start penalty). Empirically, replay latency tends to be ~3% faster than fill-time latency. Setting `REPLAY_COST_COEF = 0.97` accounts for this, allowing the fill loop to pack 2-3 additional candidates that will still fit within the 8964s replay cap.

---

## Projected Score

$$\text{Candidates} = 1013 \text{ (v13 best)} + 2 + 1 + 2.5 = \mathbf{1018.5}$$
$$\text{Score} = 1018.5 \times 0.09 = \mathbf{91.665+}$$

---

## Files

- `omega_v14_attack.py` — Attack source (264 lines)
- `build_v44.py` — Generator with 22-point validation suite
- `v44_strategy.md` — This document
- `omega_v14_attack.ipynb` — **Kaggle Submission Notebook**
