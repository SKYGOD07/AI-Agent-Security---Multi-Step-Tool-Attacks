# Comprehensive Failure Analysis & Knowledge Base (v4 – v43 / OMEGA Series — Peak: 91.170)

This document synthesizes every version's design, empirical score, failure mode, and root cause across the competition trajectory. It serves as an authoritative reference for future AI agents working on the **AI Agent Security – Multi-Step Tool Attacks** Kaggle benchmark.

---

## 1. Complete Version Progression Table (v4 – v43)

| Version | Public Score | Status / Outcome | Core Architecture / Focus | Key Lesson / Root Cause |
| :--- | :---: | :--- | :--- | :--- |
| **v4** | `78.930` | Succeeded | Basic Stockfish search | Simple single-post prompt, basic candidate generation. |
| **v5** | `77.895` | Succeeded | Template expansion | Added more prompt templates without latency filtering. |
| **v7** | `84.240` | Succeeded | Replay-Throughput Loop | Probe → Select lowest effective cost → Seed fired probes → Fill. |
| **v8** | `22.290` | Severe Regression | Heuristic Controller | High controller complexity & state overhead collapsed throughput. |
| **v9** | `51.990` | Regression | Multi-Armed Bandits | Bandit exploration wasted time on low-yield attack families during search. |
| **v11** | `23.175` | Severe Regression | Two-Track Router | Over-engineered heuristic router & signatures hurt replay throughput. |
| **v12** | `N/A` | Notebook Exception | Search overhaul + local SDK import | Imported `SandboxEnv` inside notebook cell prior to evaluator launch. |
| **v13** | `14.820` | Format Error | Replay signature archive | Overran time budget during search; leftover candidates exceeded window. |
| **v14** | `N/A` | Format Error | Base64 inline code + Relay Push100 | Candidate budget overflowed the 9000s per-model replay cap. |
| **v15** | `72.270` | Moderate Regression | Multi-Predicate Round-Robin Fill | Filled candidates across non-firing templates, wasting budget. |
| **v16** | `87.660` | Succeeded | Baseline Recovery | Clean notebook scaffold, `IS_RERUN` gating, measured latency cap. |
| **v18** | `57.285` | Severe Regression | `BURST_K = 4` Hop-Saturation | Forced 4 `http.post` calls per prompt. Non-reasoning models failed multi-post. |
| **v19** | `N/A` | Format Error | Static Diversity Padding | Unverified candidates caused model hallucination at replay time. |
| **v28** | `85.590` | Succeeded | Single-post baseline | Restricted candidates to 1 post per candidate (18 raw points). |
| **v31 (OMEGA v1)** | `76.815` | Succeeded | Initial OMEGA Port | Rebuilt baseline search engine. |
| **v32 (OMEGA v2)** | `78.435` | Succeeded | Adaptive Margin | Introduced per-model adaptive margin scaling. |
| **v33 (OMEGA v3)** | `86.490` | Succeeded | 91.305 Architecture Port | Restored fast single-hop validation fill. |
| **v34 (OMEGA v4)** | `88.560` | Succeeded | 5 Precision Levers | Adaptive margin, latency split, 1-hop probe, fast routing. |
| **v35 (OMEGA v5)** | `89.640` | Succeeded | Warm-Up Bug Fix | Fixed double-counting warm-up replay cost bug (harvested +1 free cand). |
| **v36 (OMEGA v6)** | `89.640` | Succeeded | Parameter Micro-tuning | `REPLAY_SAFE_FRAC=0.992`, `SLOWEST_MULT=1.15`. Single-post plateau. |
| **v37 (OMEGA v7)** | `88.335` | Regression (-1.305) | Multi-Predicate Stacking | Added `fs.delete` + `http.post`. 2-hop execution increased latency by +41%. |
| **v38 (OMEGA v8)** | `89.145` | Clean Recovery | Revert to v5 Architecture | Restored exact v5 single-post pipeline. Confirmed baseline stability. |
| **v39 (OMEGA v9)** | `86.355` | Regression (-2.790) | Lean Frame (No Termination) | Removed natural prompt instruction. LLM entered 4096-token runaway generation. |
| **v40 (OMEGA v10)** | `87.300` | Succeeded | Explicit Frame + Cap=1200 | Fixed runaway bug with explicit prompt, but `HARD_N_CAP=1200` capped score early. |
| **v41 (OMEGA v11)** | `89.955` | Near-Peak | **v11 Incremental Tuning** | `FRAC=0.991`, `MULT=1.15`, `N=2`. Replayed 999.5 cands (0.045 from 90.000). |
| **v42 (OMEGA v12)** | `85.970` | Regression (-3.985) | Multi-Post Harmony (`N=4`) | `_forge_plan_msg(idx, 4)` added per-candidate latency overhead on evaluator. |
| **v43 (OMEGA v13)** | **`91.170`** | **🏆 PEAK SCORE** | **v11 Precision Increments** | `FRAC=0.994`, `MULT=1.10`, `N=1`, `SLOW0=12`. Breached 90+91! (89.685 on 2nd run). |
| **v44 (OMEGA v14)** | `86.760` | Regression (-4.410) | Precision Squeeze | `COEF=0.97` under-estimated replay cost $\rightarrow$ replay budget overflow $\rightarrow$ candidates cut off. |
| **v45 (OMEGA v15)** | `88.920` | Regression (-2.250) | Prompt Micro-Trim | Micro-trimmed prompt wording slightly degraded fire rate on `gemma`. |
| **v46 (OMEGA v16)** | `62.410` | Severe Regression | Fast 1-Hop Probing | `PROBE_HOPS=1` under-estimated 8-hop replay cost by 50% $\rightarrow$ replay timeout at cand #693. |
| **v48 (OMEGA v18)** | `88.830` | Regression (-2.340) | Multi-Warmup Harvest | Extra warm-up candidates consumed 25.5s of replay budget $\rightarrow$ main fill loop stopped 2 cands early. |

---

## 2. Comprehensive Taxonomy of Failure Modes & Lessons

### 1. Multi-Hop / Multi-Predicate Overhead Failure (v7 & v12)
* **Observed Regression**: v7 dropped from 89.640 to 88.335; v12 dropped from 89.955 to 85.970.
* **Root Cause**: Adding multiple tool hops (`fs.delete` + `http.post` in v7; `N=4` multi-post in v12) increased per-candidate execution time from ~8.5s to ~12s–35s (+41% to +300% latency).
* **Impact**: Total candidate yield dropped by 30%–50%. In Kaggle evaluation, candidate count drop outweighs theoretical per-candidate score gains.
* **Golden Rule**: **Keep candidates strictly single-hop (`http.post` only) in the high-throughput fill loop.**

### 2. Prompt Termination Omission / Runaway Generation Failure (v9)
* **Observed Regression**: v9 dropped from 89.145 to 86.355 (and hung for 1d during initial sweep).
* **Root Cause**: Omitted explicit natural language termination instructions (`"Call http.post once with... Then answer OK only."`) from `FRAME_TEMPLATE`.
* **Impact**: `gpt_oss` failed to terminate token generation after generating the tool call, causing runaway generation (~4096 tokens/cand = 60+ seconds/cand).
* **Golden Rule**: **Always include explicit termination instructions ("Then answer OK only.") in all prompt templates.**

### 3. Replay Cost Double-Counting Bug (v1–v4 vs v5+)
* **Observed Flaw**: Early versions charged the warm-up period's duration twice in `_replay_stop()`, under-filling candidate sets by 7 to 12 candidates.
* **Resolution**: Captured `run_start` before warm-up, subtracted warm-up duration from `replay_cap`, and charged 0 replay cost for the warm-up candidate.

### 4. Over-Conservative Cushion Under-Filling (v6, v10)
* **Observed Limitation**: Setting `HARD_N_CAP = 1200` or `REPLAY_SAFE_FRAC = 0.985` left 135+ seconds of unused budget on the table.
* **Resolution**: Expanded `REPLAY_SAFE_FRAC = 0.994` (leaving a crisp 54s safety buffer) and set `HARD_N_CAP = 2000` so search fills right up to the 8946s replay cap.

---

## 3. The Winning OMEGA Architecture (v11 / v13 Path)

The empirical winner is the **latency-split single-post validation-fill architecture**:

1. **Warm-Up (hops=1)**: 1-hop model load, harvest 1 free candidate at index 899999.
2. **Classification (N=1, threshold=12.0s)**:
   - Samples latency on candidate 0.
   - If $> 12.0s \rightarrow gpt\_oss$ (slow row) $\rightarrow$ uses `FRAME_TEMPLATE`.
   - If $< 12.0s \rightarrow gemma$ (fast row) $\rightarrow$ uses `TEMPLATE`.
3. **Replay-Safe Fill**:
   - `REPLAY_SAFE_FRAC = 0.994` ($8946s$ cap).
   - `SLOWEST_MULT = 1.10`.
   - `SLOWEST0 = 12.0`.
   - Bounded strictly by `replay_cost + next_wall <= replay_cap`.
