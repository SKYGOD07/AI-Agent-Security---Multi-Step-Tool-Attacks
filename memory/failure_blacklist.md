# Failure Blacklist (Updated August 2026 — OMEGA v22 Peak: 91.305 🏆)

This document records architectural patterns that definitively fail on the Kaggle evaluator. **Never repeat these patterns.**

## 0. Type G: Multi-Predicate Slot Displacement (v26: 86.545)
**Symptoms**: Score drops from 91.305 to 86.545.
**Root Cause**: 2-hop deputy candidates (15s latency) yield 22 raw points, but evict ~1.8 single-post candidates (32.4 raw points lost), causing a severe net loss.
**Fix**: Keep candidates strictly single-hop (`BURST_K = 1`, `SLOW_MULTIPOST_N = 1`).

## 0.1 Type H: Domain Generator Formatting Alteration (v25: 86.215)
**Symptoms**: Score drops from 91.305 to 86.215.
**Root Cause**: Changing `_url(i)` formatting degrades model instruction matching/fire rate.
**Fix**: Keep `_url(i)` formatting byte-exact: `http://{_label(i)}.co`.

---

## 0. Type F: Stop-Rule Latency Contamination & Unverified Prefill Noise (v20, v21)
**Symptoms**: Score drops to 86.070 (v20) or 80.865 (v21).
**Root Cause**: Updating `slowest` with experimental probe latencies inflates `slowest * 1.10`, cutting off fill early. Also, unverified prefill text (`INJ_CLOSE`) confuses `gpt_oss`.
**Fix**: Isolate experimental latencies from `slowest`. Keep champion templates byte-exact (`TEMPLATE` & `FRAME_TEMPLATE`). Use two-phase backfill sizing (v22).

---

## 1. Type A: Notebook Execution Exceptions
**Symptoms**: Kaggle returns `Notebook Threw Exception` immediately upon submission. **[VERIFIED]**
**Root Cause**: Attempting to execute the scenario logic, load the local SDK, or evaluate predicates inside a notebook cell before the official Kaggle evaluation server takes over. **[VERIFIED]**
**Fix**: Use the 3-cell Base64 scaffold. Write `attack.py` to disk via base64 decoding. Gate all execution behind `os.getenv("KAGGLE_IS_COMPETITION_RERUN")`. **[VERIFIED]**

## 2. Type B: Gateway / Replay Timeout Overruns
**Symptoms**: Kaggle returns `Submission Format Error` after ~20-30 minutes of running. **[VERIFIED]**
**Root Cause**: The returned candidate list takes longer than 9000 seconds to replay. **[STRONG EVIDENCE]**
**Fix**: Track `cumulative_replay_cost` by summing actual measured latency. Stop adding candidates when `cumulative_replay_cost > REPLAY_SAFE_FRAC * 9000s`. Optimal: `REPLAY_SAFE_FRAC = 0.994` (8946s cap). **[VERIFIED — v13 scored 91.170]**

## 3. Type C: Unverified Diversity / Static Padding Dilution
**Symptoms**: Score collapses significantly below baseline (v15 scored 72; v19 timed out). **[VERIFIED]**
**Root Cause**: Padding the candidates list with prompts not verified to fire. **[STRONG EVIDENCE]**
**Fix**: Every candidate returned must be verified via a live `env.interact()` trial. **[VERIFIED]**

## 4. Type D: Multi-Post / Multi-Hop Latency Overhead
**Symptoms**: Score drops despite higher per-candidate point yield. **[VERIFIED]**
**Root Cause**: Multi-post stacking (`SLOW_MULTIPOST_N > 1`) or multi-predicate stacking (`http.post` + `fs.delete`) increases per-candidate execution time by +41% to +300%, reducing total candidate yield. **[VERIFIED — v7 dropped to 88.335, v12 dropped to 85.970]**
**Fix**: Keep candidates strictly single-hop (`BURST_K = 1`, `SLOW_MULTIPOST_N = 1`). The throughput bottleneck is fill efficiency, not per-candidate yield. **[VERIFIED — v13 scored 91.170 with single-post]**

## 5. Type E: Prompt Termination Omission
**Symptoms**: Per-candidate latency explodes to 60+ seconds. Score drops. **[VERIFIED]**
**Root Cause**: Omitting explicit termination instructions causes `gpt_oss` to enter 4096-token runaway generation. **[VERIFIED — v9 dropped to 86.355]**
**Fix**: Always include "Then answer OK only." in all prompt templates. **[VERIFIED]**
