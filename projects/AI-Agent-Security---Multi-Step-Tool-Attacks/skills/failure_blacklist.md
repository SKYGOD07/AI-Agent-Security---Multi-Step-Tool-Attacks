# Failure Blacklist — Permanent Memory (Updated v4 – v53 — Peak: 91.305 🏆)

## v51 (OMEGA v21): Slow-Row A/B Prefill Confusion (Score: 80.865)
**Root cause**: Alternating 10 slots of `INJ_CLOSE_TEMPLATE` prefill text during fill confused `gpt_oss`, causing non-firing slots and latency spikes.
**Rule**: NEVER experiment with unverified prefill prompt text in the early fill loop.

---

## v50 (OMEGA v20): Live Multi-Type Tournament Overhead & Stop Contamination (Score: 86.070)
**Root cause**: Probing 5 candidate types x 3 reps (15 probes) consumed 150-300s of wall-clock time. Worse, exotic probe latencies updated the global `slowest` variable, inflating `slowest * 1.10` and triggering premature stop conditions that cut off ~57 candidates.
**Rule**: NEVER update global stop-rule latency variables (`slowest`) with experimental or probe latencies.

---
**Root cause**: Used `FRAME_TEMPLATE` (Harmony channel tokens) for warmup instead of `TEMPLATE`, hoping to bypass CoT during model load and save 15 seconds. The trick did not provide measurable benefit; warmup with `FRAME_TEMPLATE` may have interfered with initial model state, causing a net regression.
**Rule**: Do NOT change the warmup template from the v13 baseline (`TEMPLATE`). Warmup template changes have no proven benefit.

---

## v48 (OMEGA v18): Multi-Warmup Replay Overhead Regression (Score: 88.830)
**Root cause**: Probing 3 warm-up candidates (`899999`, `899998`, `899997`) during search returned all 3 candidates in `cands`. During Kaggle's offline replay at forced `max_tool_hops=8`, replaying 3 candidates consumed **$3 \times 8.5s = 25.5s$ of replay budget**. The warm-up candidates were NOT free during offline replay! Consuming 25.5s of replay budget forced the main fill loop to stop 2 candidates earlier, dropping score to 88.830.
**Rule**: WARM-UP MUST BE EXACTLY 1 CANDIDATE (`WARMUP_IDX = 899999`)! Never add extra warm-up candidates.

---

## v46 (OMEGA v16): Fast 1-Hop Probing Collapse (Score: 62.410 CATASTROPHIC REGRESSION)
**Root cause**: Setting `PROBE_HOPS = 1` during search probing measured candidate latency at 1 hop (~4.5s), but Kaggle replays candidates at **forced `max_tool_hops = 8`** (~8.5s). The fill loop hit Kaggle's 9000s hard timeout at candidate #693, killing 1100+ candidates.
**Rule**: `PROBE_HOPS` MUST REMAIN 0 (`max_tool_hops = 8`) DURING SEARCH FILL!

---

## v45 (OMEGA v15): Micro-Trimmed Prompt Wording Regression (Score: 88.920)
**Root cause**: Micro-trimmed template removed `"once with"` and `"Then "`, slightly degrading fire rate on `gemma`.
**Rule**: NEVER MODIFY THE EXACT V13 PROMPT WORDING.

---

## Absolute Rules (Derived from Failures & Victories)

1. **WARM-UP MUST BE EXACTLY 1 CANDIDATE (`WARMUP_IDX = 899999`)**.
2. **`PROBE_HOPS` MUST REMAIN 0 (`max_tool_hops = 8`) DURING SEARCH FILL**.
3. **`REPLAY_COST_COEF` MUST REMAIN STRICTLY $\ge 1.00$**.
4. **NEVER ALTER THE EXACT V13 PROMPT WORDING**.
5. **Keep `SLOWEST_MULT = 1.10` & `REPLAY_SAFE_FRAC = 0.994`**.
