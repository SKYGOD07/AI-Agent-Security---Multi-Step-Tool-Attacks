# Failure Blacklist — Permanent Memory (Updated v4 – v44 — Peak: 91.170 🏆)

## v44 (OMEGA v14): Replay Cost Under-Estimation Regression (Score: 86.760 / 83.835)
**Root cause**: Setting `REPLAY_COST_COEF = 0.97` under-estimated candidate replay latency by assuming replay runs 3% faster than fill. In Kaggle's evaluation server, replay runs at forced `max_tool_hops=8` against hidden model instances and is **NOT** faster than search time. Under-estimating replay cost caused the candidate list returned by `run()` to **OVERRUN THE 9000s REPLAY BUDGET**, causing trailing candidates to be cut off or timed out during evaluation. Setting `SLOWEST_MULT = 1.05` was also too tight, causing end-of-fill deadline overshooting.
**Rule**: `REPLAY_COST_COEF` MUST REMAIN STRICTLY $\ge 1.00$ (100% 1:1 cost accounting). Never under-estimate replay latency! `SLOWEST_MULT` must remain $\ge 1.10$.

---

## v43 (OMEGA v13): BREAKTHROUGH — Score 91.170 🏆
**Achievement**: Confirmed peak score of 91.170 using single-post latency-split fill. Also scored 89.685 on a 2nd run (evaluator variance). Proved that incremental precision tuning of the v11 architecture (`FRAC=0.994`, `MULT=1.10`, `CLASSIFY_N=1`, `SLOWEST0=12`, `COEF=1.0`) is the winning path.

---

## v42 (OMEGA v12): Multi-Post Harmony Token Forging Overhead (Score: 85.970)
**Root cause**: Forged `gpt_oss`'s analysis channel for 4 `http.post` calls per candidate (`SLOW_MULTIPOST_N = 4`). Executing 4 hops added per-candidate latency overhead on the Kaggle evaluator, reducing total candidate yield (-3.985 pts).
**Rule**: Single-post latency-split architecture (`SLOW_MULTIPOST_N = 1`) is the proven optimal high-throughput path.

---

## v39 (OMEGA v9): Prompt Termination Omission / Runaway Generation (Score: 86.355)
**Root cause**: Omitted explicit natural language termination instructions ("Then answer OK only.") in `FRAME_TEMPLATE`, causing `gpt_oss` to enter 4096-token runaway generation (~60s/cand).
**Rule**: Always include explicit termination instructions ("Then answer OK only.") in all prompt templates.

---

## Absolute Rules (Derived from Failures & Victories)

1. **`REPLAY_COST_COEF` MUST REMAIN STRICTLY $\ge 1.00$**. Never under-estimate replay cost.
2. **Keep candidates strictly single-hop (`http.post` only)** (`SLOW_MULTIPOST_N = 1`, `BURST_K = 1`).
3. **Keep `SLOWEST_MULT \ge 1.10`**. Never squeeze stop cushion below 1.10.
4. **Never omit prompt termination constraints** ("Then answer OK only.").
5. **Size portfolio by measured replay cost** (`REPLAY_SAFE_FRAC = 0.994`, 8946s cap).
