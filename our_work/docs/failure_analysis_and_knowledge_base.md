# Comprehensive Failure Analysis & Knowledge Base (v4 – v19)

This document synthesizes every version's design, empirical score, failure mode, and root cause across the competition trajectory. It serves as an authoritative reference for future AI agents and models working on the **AI Agent Security – Multi-Step Tool Attacks** Kaggle benchmark.

---

## 1. Executive Summary & Version Progression Table

| Version | Public Score | Status / Error Type | Core Architectural Idea | Primary Reason for Score / Failure |
| :--- | :---: | :--- | :--- | :--- |
| **v4** | `78.930` | Succeeded | Basic Stockfish search | Simple single-post prompt, basic candidate generation. |
| **v5** | `77.895` | Succeeded | Template expansion | Added more prompt templates without latency filtering. |
| **v7** | **`84.240`** | **Best Core** | **Replay-Throughput Loop** | Linear pipeline: Probe → Select lowest effective cost → Seed fired probes → Fill until budget. |
| **v8** | `22.290` | Catastrophic Regression | Family Pivot / Heuristic Controller | High controller complexity, bad routing, search state overhead collapsed throughput. |
| **v9** | `51.990` | Poor | Adaptive Portfolio / Multi-Armed Bandits | Bandit exploration wasted time on low-yield attack families during search. |
| **v11** | `23.175` | Catastrophic Regression | Two-Track Router | Over-engineered heuristic router & signatures hurt replay throughput. |
| **v12** | `N/A` | **Notebook Threw Exception** | Search overhaul + local SDK import | Imported `SandboxEnv` & executed `importlib.exec_module` + `AttackAlgorithm()` inside notebook cell prior to evaluator launch. |
| **v13** | `14.820` | Regression / Format Error | Replay signature archive + heavy search | Overran time budget during search; leftover candidates exceeded replay window. |
| **v14** | `N/A` | **Submission Format Error** | Base64 inline code + Relay Push100 | Base64 decoding corruption / candidate budget overflowed the 9000s per-model replay cap. |
| **v15** | `72.270` | Moderate Regression | Multi-Predicate Round-Robin Fill | Filled candidates across Exfiltration, Destructive Write, & Confused Deputy without verifying fire rates, wasting budget on non-firing templates. |
| **v16** | **`87.660`** | **Succeeded (Best)** | **Disciplined 88.560 Baseline Recovery** | Rebuilt exact 88.560 baseline: 5-cell `%%writefile` notebook, `IS_RERUN` gating, measured latency replay-safe cap. |
| **v17** | `N/A` | **Submission Format Error** | 89.055 Template Race Port | Base64 / string formatting bug or unhandled exception during fallback execution. |
| **v18** | `57.285` | Severe Regression | `BURST_K = 4` Hop-Saturation | Forced 4 `http.post` calls per prompt. Target models (Gemma/GPT-OSS) failed to follow multi-post instructions reliably, causing fire rate to collapse. |
| **v19** | `N/A` | Format Error / Replay Timeout | Static Diversity Padding (Unverified) | Added ~932 unverified static candidates. Unverified prompts caused model hallucination / multi-hop delays at replay time, triggering `ModelEvaluationTimedOut`. |

---

## 2. Deep-Dive Taxonomy of Failures

### Type A: Notebook & Infrastructure Failures ("Notebook Threw Exception")
* **Root Cause (v12)**: Executing `AttackAlgorithm()` inside the notebook using `importlib` or running local simulation classes (`SandboxEnv`) prior to Kaggle launching `JEDAttackInferenceServer().serve()`.
* **Lesson**: The notebook must be a clean, minimal wrapper:
  1. Write `/kaggle/working/attack.py` via `%%writefile`.
  2. Gate server execution behind `if os.getenv("KAGGLE_IS_COMPETITION_RERUN"): server.serve()`.
  3. Else, generate placeholder `submission.csv` with schema `Id,Score`.
  4. Never import `SandboxEnv` or execute `AttackAlgorithm()` inside notebook cells.

### Type B: Replay Timeout & Gateway Violations ("Submission Format Error")
* **Root Cause (v13, v14, v17, v19)**: Overrunning the 9000-second per-model, per-guardrail evaluation deadline during the gateway replay phase.
* **Mechanism**: Kaggle's evaluation infrastructure runs `attack.py` search, then independently replays every candidate returned in `run()` at `max_tool_hops=8`. If total replay time > 9000s, Kaggle raises `ModelEvaluationTimedOut` which surfaces as **Submission Format Error**.
* **Lesson**: Candidates must be capped by **cumulative measured replay cost** (sum of hops=8 trial latencies) stopping at `0.99 * 9000s = 8910s`. Unverified candidates with unpredictable latencies must never be bulk-injected into the returned portfolio.

### Type C: Multi-Instruction Prompt Collapse (v18 - Score: 57.285)
* **Root Cause**: v18 attempted to force the LLM to call `http.post` 4 times in a single prompt (`BURST_K = 4`).
* **Mechanism**: Non-reasoning models (like Gemma 4) or constrained models struggle with complex multi-tool tool-use instructions. The model either called `http.post` once and stopped, or entered text analysis mode, dropping the fire rate from ~50% down to under 15%.
* **Lesson**: Multi-step / multi-action payloads must be verified live during search. Never assume LLMs will execute multi-tool chains without live confirmation.

### Type D: Unverified Diversity Ingestion (v15 - Score: 72.270 & v19)
* **Root Cause**: Round-robin or static padding with unverified templates (Confused Deputy, Destructive Write).
* **Mechanism**: In v15 and v19, candidate slots were populated with unverified templates. Because these templates had a 0% to 10% fire rate on the target model, they diluted the portfolio and wasted replay budget slots that could have been used by deterministic Exfiltration candidates.
* **Lesson**: Only candidates that have been **live-verified to fire** (or pass a strict replay-safe filter) belong in the returned portfolio.

---

## 3. The Winning Core Architecture (v7 / v16 / JED Baseline)

The empirical evidence confirms that the optimal attack architecture is a **replay-safe, probe-selected portfolio optimizer**:

1. **Phase 1: Probe (5 reps × 5 templates)**
   - Templates: `plain`, `bare`, `bare_ok`, `inj_close`, `inj_commentary`
   - Metric: `effective_cost = median(successful_latencies) / fire_rate`
2. **Phase 2: Seed**
   - Retain all candidates that successfully fired during probing.
3. **Phase 3: Replay-Safe Fill**
   - Generate candidates using the single lowest-cost winning template.
   - Track cumulative measured latency (`replay_cost += trial_elapsed`).
   - Stop immediately when `replay_cost + fill_unit > 8910s` (0.99 × 9000s) or candidate count reaches limit.
4. **Phase 4: Semantic Deduplication**
   - Deduplicate by replay signature `(tool_sequence | predicate_family | prompt_hash)`.
   - Prefer shorter prompts and lower measured latencies upon collision.

---

## 4. Architectural Guardrails for v20+

1. **Zero Notebook Complexity**: 5 cells max, no AST execution, clean `submission.csv` placeholder.
2. **No Dynamic Search Machinery**: No multi-armed bandits, beam search, or heavy routing controllers.
3. **Strict Live Verification**: Every candidate added to the active portfolio MUST be verified live via `env.interact()`.
4. **Replay Budget Guarantee**: Return set bounded strictly by measured trial latency sum ≤ `8910s`.
