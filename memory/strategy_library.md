# Strategy Library (Updated v52 / OMEGA Series — Peak: 91.305 🏆)

This library contains reusable tactics that have been empirically tested against the Kaggle evaluator. Only promote a strategy to "Preferred" if it is verified to improve the score and survive replay.

---

## 0. Two-Phase Backfill Sizing (OMEGA v22 Peak 91.305 🏆)
- **Status**: **PREFERRED (ALL-TIME PEAK BENCHMARK: 91.305 in v22 🏆)**
- **Evidence Level**: **[VERIFIED - HIGHEST LB SCORE]**
- **Purpose**: Recover idle cushions (last 4-8% of windows) without overrun risk.
- **Mechanics**:
  - **Primary Segment**: `PRIMARY_REPLAY_FRAC = 0.945`, `PRIMARY_WALL_FRAC = 0.985` (guaranteed safe fit even under pessimistic replay latency).
  - **Backfill Segment**: `BACKFILL_REPLAY_FRAC = 0.995`, `BACKFILL_WALL_FRAC = 0.997` (converts idle window into +3-5 extra candidates).
  - **Latency-Ascending Order**: Submits candidates sorted by latency ascending, so any replay truncation cuts slowest candidates last.
- **When it helped**: OMEGA v22 (**91.305**), OMEGA v23 (**91.125**).
- **Confidence**: 100%
- **Replay Risk**: Low

---

## 1. Latency-Split Single-Post Fill (OMEGA Core)
- **Status**: **PREFERRED**
- **Evidence Level**: **[VERIFIED]**
- **Purpose**: Maximize the number of firing Exfiltration candidates generated within the 9000s per-model budget.
- **Mechanics**: Sample candidate 0 latency. Classify target model:
  - If $> 12.0s \rightarrow gpt\_oss$ (slow row) $\rightarrow$ use Harmony-forged `FRAME_TEMPLATE`.
  - If $< 12.0s \rightarrow gemma$ (fast row) $\rightarrow$ use standard imperative `TEMPLATE`.
- **When it helped**: OMEGA v13 (91.170), OMEGA v22 (91.305), OMEGA v23 (91.125).
- **Confidence**: 100%
- **Replay Risk**: Low

## 2. Replay-Safe Sizing (Measured Latency Cap)
- **Status**: **PREFERRED**
- **Evidence Level**: **[VERIFIED]**
- **Purpose**: Prevent `ModelEvaluationTimedOut` errors (Submission Format Error) during Kaggle's hidden replay phase.
- **Mechanics**: Track cumulative measured execution time of every candidate during search. Stop generating new candidates when `cumulative_cost > (REPLAY_SAFE_FRAC * 9000s)`.
- **Optimal Settings**: `PRIMARY_REPLAY_FRAC = 0.945`, `BACKFILL_REPLAY_FRAC = 0.995`.
- **Confidence**: 100%
- **Replay Risk**: Low

## 3. Warm-Up Replay Cost Exemption & Candidate Harvesting
- **Status**: **PREFERRED**
- **Evidence Level**: **[VERIFIED]**
- **Purpose**: Prevent warm-up model-load latency (75-100s) from inflating candidate costs or under-filling the candidate portfolio.
- **Mechanics**: Subtract warm-up time from `replay_cap` once, charge 0 replay cost for the warm-up candidate, and harvest the warm-up candidate at `max_tool_hops=1` (+1 free candidate).
- **When it helped**: OMEGA v5 (+1.08 points gain), OMEGA v11 (89.955).
- **Confidence**: 100%
- **Replay Risk**: Low

## 4. Multi-Predicate & Multi-Post Stacking
- **Status**: **REJECTED / BLACKLISTED**
- **Evidence Level**: **[EMPIRICAL REGRESSION]**
- **Purpose**: Attempting to force multi-tool execution (`fs.delete` + `http.post` in v7; `N=4` multi-post in v12).
- **Why it Failed**: Executing across 2 to 4 hops increases candidate latency by +41% to +300%. The resulting drop in candidate count outweighs the per-candidate point gains on the Kaggle evaluator, causing regressions (v7 dropped to 88.335, v12 dropped to 85.970).
- **Confidence**: 0%
- **Replay Risk**: High

## 5. Unconstrained Prompt Termination Omission
- **Status**: **REJECTED / BLACKLISTED**
- **Evidence Level**: **[EMPIRICAL REGRESSION & TIMEOUT]**
- **Why it Failed**: Omitting explicit natural language termination instructions ("Then answer OK only.") causes `gpt_oss` to enter 4096-token runaway generation, taking 60+ seconds per candidate and timing out the container (v9 dropped to 86.355).
- **Rule**: Always include explicit termination instructions ("Then answer OK only.") in all prompt templates.
