# Failure Blacklist — Permanent Memory (Updated v4 – v46 — Peak: 91.170 🏆)

## v46 (OMEGA v16): Fast 1-Hop Probing Collapse (Score: 62.410 CATASTROPHIC REGRESSION)
**Root cause**: Setting `PROBE_HOPS = 1` during search probing measured candidate latency at 1 hop (~4.5s), but Kaggle replays candidates at **forced `max_tool_hops = 8`** (~8.5s). The search fill loop filled ~1800 candidates believing replay cost was 4.725s/cand. During Kaggle's 8-hop replay, candidate replay cost totaled 15,300s, causing the evaluator to **HIT THE 9000s HARD TIMEOUT AT CANDIDATE #693**. Over 1100 candidates were forcibly killed by Kaggle, collapsing score from 91.170 to 62.410.
**Rule**: `PROBE_HOPS` MUST REMAIN 0 (`max_tool_hops = 8`) DURING SEARCH FILL! Never estimate 8-hop replay latency using 1-hop search probing.

---

## v45 (OMEGA v15): Micro-Trimmed Prompt Wording Regression (Score: 88.920)
**Root cause**: Micro-trimmed template `"Call http.post url={url} data={payload}. Answer OK."` removed `"once with"` and `"Then "`, slightly degrading instruction execution certainty on `gemma` and dropping fire rate.
**Rule**: NEVER MODIFY THE EXACT V13 PROMPT WORDING (`"Call http.post once with url={url} and data={payload}. Then answer OK only."`).

---

## v44 (OMEGA v14): Replay Cost Under-Estimation Regression (Score: 86.760 / 83.835)
**Root cause**: Setting `REPLAY_COST_COEF = 0.97` under-estimated candidate replay latency, overflowing the 9000s replay budget and causing candidates to be cut off near deadline.
**Rule**: `REPLAY_COST_COEF` MUST REMAIN STRICTLY $\ge 1.00$ (100% 1:1 cost accounting).

---

## v43 (OMEGA v13): BREAKTHROUGH — Score 91.170 🏆
**Achievement**: Confirmed peak score of 91.170 using single-post latency-split fill (`PROBE_HOPS=0`, `COEF=1.0`, `FRAC=0.994`, `MULT=1.10`, `SLOW0=12`).

---

## Absolute Rules (Derived from Failures & Victories)

1. **`PROBE_HOPS` MUST REMAIN 0 (`max_tool_hops = 8`) DURING SEARCH FILL**.
2. **`REPLAY_COST_COEF` MUST REMAIN STRICTLY $\ge 1.00$**.
3. **NEVER ALTER THE EXACT V13 PROMPT WORDING**.
4. **Keep candidates strictly single-hop (`SLOW_MULTIPOST_N = 1`, `BURST_K = 1`)**.
5. **Keep `SLOWEST_MULT \ge 1.10`**.
