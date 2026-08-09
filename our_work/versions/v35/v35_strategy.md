# OMEGA Attack v5 Strategy & Architecture (v35) -- Final Push to 90

## Score Trajectory

| Version | Notebook | Score | Key Change |
|---------|----------|-------|------------|
| v28 | `stockfish_v28_attack.ipynb` | **85.590** | Bulletproof baseline |
| v31 | `omega_v1_attack.ipynb` | **76.460** | Multi-predicate probing |
| v32 | `omega_v2_attack.ipynb` | **78.600** | Split gpt_oss multi-post |
| v33 | `omega_v3_attack.ipynb` | **86.490** | 91.305 arch direct port |
| v34 | `omega_v4_attack.ipynb` | **88.560** | 5 precision levers |
| **v35** | **`omega_v5_attack.ipynb`** | **Target: 90+** | **Bug fix + 2 tuning levers** |

---

## Changes from v4 (88.560) to v5

### 1. [CRITICAL BUG FIX] Warm-Up Replay Cost Double-Counting

In v4, the warm-up candidate's replay cost was charged as `(time.monotonic() - run_start)`,
which is the FULL warm-up duration (~60-100s including model load). But this time was
ALREADY subtracted from `replay_cap`:

```python
# Line 206 (v4): warm-up time already subtracted here
replay_cap = replay_safe_frac * replay_budget - (time.monotonic() - run_start)

# Line 217 (v4): DOUBLE-COUNTING -- charging it AGAIN as replay cost
replay_cost += (time.monotonic() - run_start) * replay_cost_coef
```

This meant we were paying for the warm-up TWICE, effectively reducing the replay budget
by an extra ~60-100s = **~7-12 fewer candidates than possible**.

**v5 fix**: Charge ZERO for the warm-up candidate. The warm-up subtraction in `replay_cap`
already reserves space for the replay's model-load overhead, and the warm-up candidate's
actual replay cost (~8-20s for one interaction) is safely absorbed by the existing 1%
REPLAY_SAFE_FRAC cushion (90s on 9000s budget).

**Expected gain: ~0.7-1.0 points** (the biggest v5 lever).

### 2. SPLIT_CLASSIFY_N: 5 -> 3

3 samples at 12s threshold: gemma mean ~8.5s, gpt_oss mean ~20s. The gap is 12s wide
with the threshold exactly in the middle. Even 3 samples clearly separate them.

**Expected gain: ~0.3 points** (saves ~25-50s of classification overhead).

### 3. SLOWEST_MULT: 1.28 -> 1.20

20% cushion on the MAX observed latency is still generous. The max is already a worst-case
tracker that only ever increases.

**Expected gain: ~0.1 points** (marginal but safe).

---

## Complete Parameter Comparison (v3 -> v4 -> v5)

| Parameter | v3 (86.490) | v4 (88.560) | v5 (target 90+) |
|-----------|-------------|-------------|-----------------|
| REPLAY_SAFE_FRAC | 0.98 | **0.99** | 0.99 |
| SPLIT_CLASSIFY_N | 7 | 5 | **3** |
| SLOWEST_MULT | 1.35 | 1.28 | **1.20** |
| Warm-up hops | 8 | **1** | 1 |
| Warm-up harvest | No | **Yes** | Yes |
| Warm-up replay charge | N/A | ~60-100s (BUG) | **0s (FIXED)** |

---

## Files

- `omega_v5_attack.py` -- Attack algorithm source (295 lines)
- `build_v35.py` -- Notebook builder with 15-point validation (incl. bug-fix check)
- `v35_strategy.md` -- This document
- `omega_v5_attack.ipynb` -- Ready for Kaggle submission
