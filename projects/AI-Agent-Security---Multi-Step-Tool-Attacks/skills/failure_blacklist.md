# Failure Blacklist — Permanent Memory (Updated for v4 – v43)

## v37 (OMEGA v7): Multi-Predicate Stacking Regression (Score: 88.335)
**Root cause**: Added `fs.delete` + `http.post` multi-predicate candidates (`MULTI_TEMPLATE`). Executing 2 tool calls per candidate increased latency from ~8.5s to ~12s (+41% time cost). If `fs.delete` was blocked by guardrails, per-candidate score stayed at 18 raw points while candidate count dropped by ~30%, causing a net score regression (89.640 → 88.335).
**Rule**: Never add multi-hop or multi-predicate sequences to the fill loop.

## v39 (OMEGA v9): Prompt Termination Omission / Runaway Generation (Score: 86.355)
**Root cause**: Omitted explicit natural language termination instructions (`"Call http.post once with... Then answer OK only."`) in `FRAME_TEMPLATE`. Without explicit termination, `gpt_oss` failed to terminate token generation after generating the tool call, entering runaway token generation (~4096 tokens/cand = 60+ seconds/cand).
**Rule**: Always include explicit termination instructions ("Then answer OK only.") in all prompt templates.

## v40 (OMEGA v10): Artificial Cap Under-Filling (Score: 87.300)
**Root cause**: Set `HARD_N_CAP = 1200` and `REPLAY_SAFE_FRAC = 0.985`, leaving 135+ seconds of unused budget on the table. Stopped candidate collection before budget capacity was exhausted.
**Rule**: Set `HARD_N_CAP = 2000` and tune `REPLAY_SAFE_FRAC` (e.g. 0.994) to fill right up to the 8946s replay cap.

## v42 (OMEGA v12): Multi-Post Token Forging Latency Overhead (Score: 85.970)
**Root cause**: Forged `gpt_oss`'s analysis channel to execute 4 `http.post` calls per candidate (`SLOW_MULTIPOST_N = 4`). While theoretically yielding 72 raw points per candidate, execution across 4 hops added substantial latency overhead on the Kaggle evaluator, reducing total candidate yield and causing a score regression (89.955 → 85.970).
**Rule**: Single-post latency-split architecture (`SLOW_MULTIPOST_N = 1`) is the proven optimal high-throughput path.

---

## Proven High-Scoring Victories

### v35 (OMEGA v5): Score 89.640
**Breakthrough**: Fixed warm-up double-counting bug. Subtracted warm-up duration from `replay_cap` once, charged 0 replay cost for warm-up candidate, and harvested 1 free candidate at `max_tool_hops=1`.

### v41 (OMEGA v11): Score 89.955 (PEAK OMEGA BENCHMARK)
**Breakthrough**: Incremental parameter tuning on single-post architecture (`REPLAY_SAFE_FRAC = 0.991`, `SLOWEST_MULT = 1.15`, `SPLIT_CLASSIFY_N = 2`). Replayed 999.5 candidates — 0.045 points away from 90.000!

---

## Absolute Rules (Derived from Failures & Victories)

1. **Keep candidates strictly single-hop (`http.post` only)** in the high-throughput fill loop.
2. **Never omit prompt termination constraints** ("Then answer OK only.").
3. **Never multiply per-candidate replay cost** (`BURST_K = 1`, `SLOW_MULTIPOST_N = 1`).
4. **Size portfolio by measured replay cost** (`REPLAY_SAFE_FRAC = 0.994`, 8946s cap).
5. **Never edit .ipynb with string replacement**. Always use `json.load()` / `json.dump()`.
