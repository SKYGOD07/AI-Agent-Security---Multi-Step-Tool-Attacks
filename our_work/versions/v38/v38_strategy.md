# OMEGA Attack v8 Strategy (v38) -- Clean Recovery

## Background & v7 Post-Mortem

v7 introduced multi-predicate stacking (`http.post` + `fs.delete`) to attempt +44% score per candidate (26 raw vs 18 raw). However, v7 resulted in a **-1.305 regression** (89.640 → 88.335).

### Root Cause Analysis of v7 Failure
1. **Warm-up Overhead**: Warm-up at `max_tool_hops=2` wasted ~5–15s during environment warm-up.
2. **Per-Candidate Latency Penalty**: Executing two tools (`http.post` and `fs.delete`) increased candidate execution time from ~8.5s to ~12s (+41% time cost).
3. **Guardrail Failure**: If `fs.delete` was blocked by environment guardrails (`ok=False`), candidates remained worth 18 raw points while taking 41% longer. The total candidate count dropped by ~30%, leading directly to score loss.

### Rule Established for Future Iterations
> **Never add multi-hop sequences to the high-throughput fill loop.** Extra tool hops increase per-candidate time cost significantly, dropping candidate yield below the recovery threshold.

---

## OMEGA v8 Strategy

OMEGA v8 is a **clean recovery release** that reverts to the exact architecture of v5 (our peak benchmark of **89.640**):
- **Single-predicate targeting**: Focused exclusively on `http.post` with `SECRET_MARKER`.
- **Fast warm-up**: Restored to `max_tool_hops=1`.
- **Proven tuning parameters**:
  - `REPLAY_SAFE_FRAC = 0.99`
  - `SPLIT_CLASSIFY_N = 3`
  - `SLOWEST0 = 25.0`
  - `SLOWEST_MULT = 1.20`
- **Double-counting bug fix preserved**: Warm-up candidate is harvested with 0 replay charge.

---

## Score Trajectory

| Version | Score | Key Feature |
|---|---|---|
| v3 | 86.490 | 91.305 architecture direct port |
| v4 | 88.560 | 5 precision levers |
| v5 | **89.640** | Double-counting bug fix |
| v6 | 89.640 | Parameter micro-tuning (plateau) |
| v7 | 88.335 | Multi-predicate attempt (regression) |
| **v8** | **89.640 target** | Clean recovery & baseline verification |

---

## Files

- `omega_v8_attack.py` — Attack algorithm (267 lines, exact v5 logic)
- `build_v38.py` — Notebook generator with 20-point validation suite
- `v38_strategy.md` — Strategy and post-mortem document
- `omega_v8_attack.ipynb` — Clean recovery notebook for Kaggle submission
