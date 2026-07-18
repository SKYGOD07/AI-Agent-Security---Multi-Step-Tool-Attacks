# AI Agent Security – Multi-Step Tool Attacks: Attack Discovery & Optimization Engine

Welcome to our official research repository and submission architecture for the Kaggle competition **AI Agent Security – Multi-Step Tool Attacks**. 

This project evolved from an academic Stockfish-translated tree search lab into a high-throughput **Adaptive Replay-Portfolio Optimizer**, engineered to discover multi-step tool-use vulnerabilities against robust target evaluation models (`GPT-OSS` and `Gemma 4`).

---

## 🏆 Competition Summary & Why the Benchmark is Different

### The Competition Objective
In modern agentic AI architectures, LLMs are granted access to execution tools (`http.post`, `exec.run`, `file.delete`, `auth.grant_role`). The goal of this competition is to act as a red-team discovery engine: generating a portfolio of adversarial prompts (`candidates`) that cause target agent pipelines to execute unauthorized, destructive, or exfiltrative tool sequences.

### Why the Benchmark is Different
Unlike traditional LLM jailbreak competitions that score single-turn text completions using static classifiers or string matching, this benchmark evaluates submissions using a **closed-loop Replay-Validated Execution Pipeline**:
1. **Replay Validation**: Every generated prompt is executed live across target evaluation agents (`GPT-OSS` and `Gemma 4`) in sandboxed environments.
2. **Replay Budgeting**: Submissions are strictly constrained by a **9000-second cumulative replay budget**. Every second spent replaying slow or redundant candidates penalizes overall yield.
3. **Multi-Dimensional Reward Profile**: The leaderboard score is not just the count of violations. It heavily rewards:
   - **Severity**: High-impact violations (`UNTRUSTED_TO_ACTION`, `DESTRUCTIVE_WRITE`, `CONFUSED_DEPUTY`) receive massive score bonuses compared to basic `EXFILTRATION`.
   - **Diversity across Tool Signatures**: The benchmark requires distinct tool-call sequences and prompt structures. Submitting 500 variations of the exact same `http.post` call triggers diminishing marginal returns and refusal adaptation.
   - **Unique Replay Signatures & Coverage**: Only candidates that add unique `(tool_seq, predicate_family, mutation_family, prompt_hash)` signatures or improve empirical yield-per-second increase the final score.

---

## 📈 Score History & What Each Version Taught Us (`v1` $\rightarrow$ `v9`)

| Version | Leaderboard Score | Architectural Approach & Key Learnings |
| :--- | :--- | :--- |
| **`v1` / `v2`** | `~10.000` | **Initial Prototypes**: Basic prompt generation and static templates. *Lesson: Without tool-use awareness, random prompt generation almost never triggers multi-step tool calls.* |
| **`v3`** | `11.250` | **Early Stockfish Search**: Applied traditional alpha-beta minimax search to prompt tokens. *Lesson: Token-level minimax search is far too slow and does not align with agentic tool execution mechanics.* |
| **`v4`** | `78.930` | **Go-Explore & Transposition Caching**: Introduced state-space hashing (`ReplaySignatureArchive`), PUCT move ordering, and multi-dimensional novelty search. *Lesson: Structured state caching and high-throughput discovery jumpstarted our score from the teens into the high 70s.* |
| **`v5`** | `77.895` (`-1.035`) | **Heavy Search Over-Engineering**: Added deep AlphaZero-style multi-hop rollout layers, complex online Beta samplers, and heavy pruning. *Lesson: More search complexity caused a regression! The heavy search layers consumed our execution budget without increasing unique replayable candidate diversity.* |
| **`v6`** | `~78.500` | **Empirical Optimization Cleanup**: Stripped decorative pruning and focused on clean replay tracking. *Lesson: Confirmed that code size and search depth are not the bottleneck; candidate yield-per-second is.* |
| **`v7`** | `~82.000` (`RELAY PUSH100`) | **JED-Style 5-Template Probing**: Adopted front-end template probing (`plain`, `bare`, `bare_ok`, `inj_close`, `inj_commentary`) and stripped out all heavy tree search. *Lesson: Probing reliable structural templates and estimating replay cost via empirical median latency recovered performance and established our clean baseline.* |
| **`v8`** | `~85.000` | **Predicate-Family Aware & Pivot Rule**: Expanded from mono-family exfiltration to 4 severity-weighted families (`EXFILTRATION`, `UNTRUSTED_TO_ACTION`, `DESTRUCTIVE_WRITE`, `CONFUSED_DEPUTY`) with a static `PIVOT_LIMIT = 3` stop/go rule. *Lesson: Plateaued in the mid-80s because static stop/go rules cannot adapt online to heterogeneous target refusal surfaces across different evaluation models.* |
| **`v9`** | **Targeting `110+`** | **Adaptive Replay-Portfolio Optimizer**: Replaced static heuristics with an **Online Multi-Armed Bandit Allocator (`Thompson Sampling Beta distributions`)** and **Marginal Leaderboard Gain selection** inside a compact Pareto set. |

---

## ⚡ Current v9 Strategy & Architecture Overview

`v9` transforms our engine from a static search lab into a self-contained, highly adaptive **Online Replay-Portfolio Optimizer**:

```
+-----------------------------------------------------------------------------------+
|                        PHASE 1: JED PROBING FRONT-END                             |
|  Probe 5 proven templates (5 reps each across balanced families).                 |
|  Select winning template using: median(successful_probe_latency) / fire_rate.     |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                 PHASE 2: SEED COMPACT PARETO ARCHIVE & BANDIT                     |
|  Seed all successful probes into ParetoPortfolioArchive & initialize online       |
|  Beta(alpha, beta) bandit parameters in AdaptiveFamilyAllocator.                  |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|              PHASE 3: ONLINE UCB / THOMPSON SAMPLING BANDIT FILL                  |
|  Sample allocator.select_arm() across 4 families:                                 |
|  - EXFILTRATION (http.post)          - UNTRUSTED_TO_ACTION (exec.run)             |
|  - DESTRUCTIVE_WRITE (file.delete)   - CONFUSED_DEPUTY (auth.grant_role)          |
|  Reward productive arms (+alpha); automatically decay dead/refused arms (+beta).  |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|               PHASE 4: THIN STOCKFISH BEAM EXPANSION (`top 3 beams`)              |
|  Retain strictly top 3 live branches per family. Apply rapid, non-blocking        |
|  mutations (`synonym swap`, `confirm suffix`, `system override`, `param var`).    |
|  Decay arm weight automatically if beam fails to improve across consecutive runs. |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                 PHASE 5: DEDUPLICATED PARETO PORTFOLIO RETURN                     |
|  Sort by Marginal Leaderboard Gain per second (`marginal_gain / latency`).        |
|  Cap exact returned selection safely at `0.99 * 9000 seconds` (`REPLAY_SAFE`).    |
+-----------------------------------------------------------------------------------+
```

### Core Innovations in v9 (`Point 1` $\rightarrow$ `Point 10`)
1. **Adaptive Family Allocator (`Point 1`)**: Treats each predicate family as a bandit arm using `Beta(alpha, beta)` Thompson Sampling. Rewards arms discovering new replay signatures (`+alpha`) and automatically decays unproductive arms (`+beta`).
2. **JED Probing Front-End Selector (`Point 2`)**: Probes the 5 proven templates (`plain`, `bare`, `bare_ok`, `inj_close`, `inj_commentary`) and stops probing (`never becomes main search`).
3. **Thin Stockfish Controller (`Point 3`)**: Preserves Stockfish strictly for move ordering, candidate ranking (`score / latency`), caching, deduplication, and early stopping.
4. **Marginal Leaderboard Gain (`Point 4`)**: Candidate valuation approximates: $\text{expected\_new\_sigs}(30) + \text{expected\_new\_fam}(50) + \text{severity} - \text{cost} - \text{dup}$, prioritizing yield per second.
5. **Compact Pareto Set Portfolio (`Point 5`)**: Retains candidates only if they improve unique signature coverage, family coverage, severity, or replay efficiency. Drops strictly dominated entries.
6. **Strict Replay Signature (`Point 6`)**: Deduplicates by `tool_seq|predicate_family|mutation_family|prompt_hash`.
7. **Small Beam per Family (`Point 7`)**: Each family maintains a local beam (`top 3 branches`). Automatically decays family weight if the beam stops improving.
8. **Measured Replay Safety Cap (`Point 8`)**: Caps portfolio at `0.99 * 9000 seconds` (`REPLAY_SAFE = 8910s`) using measured median latencies.
9. **Simpler, Lean Architecture (`Point 9`)**: Clean, high-performance `~450 line` engine in `attack.py` without search bloat.
10. **Offline & Kaggle Valid (`Point 10`)**: Fully offline with exact schema compliance (`submission.csv` (`Id,Score`)).

---

## 🗺️ Repository File Map

```
C:\OPENAI AI AGENT CYBERSEC\
├── README.md                              # Canonical landing page & architectural guide (this document)
└── our_work/
    ├── attack.py                          # Core v9 Adaptive Replay-Portfolio Optimizer (exact submission engine)
    ├── stockfish_v9_attack.ipynb          # Standalone Kaggle submission notebook wrapper for v9
    ├── v9_replay_throughput_report.md     # Deep-dive architectural breakdown & before/after report for v9
    ├── test_search.py                     # Local runtime testing harness verifying AttackAlgorithm execution
    ├── verify_notebook.py                 # AST/Python syntax verification script for generated notebooks
    ├── build_notebook.py                  # Build tool that compiles attack.py into standalone .ipynb notebooks
    ├── stockfish_v8_attack.ipynb          # Preserved standalone v8 submission notebook
    ├── stockfish_v7_attack.ipynb          # Preserved standalone v7 submission notebook
    ├── stockfish_v6_attack.ipynb          # Preserved standalone v6 submission notebook
    ├── v8_replay_throughput_report.md     # Preserved v8 report
    └── v7_replay_throughput_report.md     # Preserved v7 report
```

---

## 🛠️ How to Run Locally & Validate the Notebook

### 1. Python Environment Setup
We recommend running inside an active virtual environment with `pydantic` installed:
```powershell
# Activate virtual environment (example using algokit venv or local venv)
& "C:\Users\intel\pipx\venvs\algokit\Scripts\python.exe" -m pip install pydantic
```

### 2. Verify Syntax & Bytecode Compilation
To confirm `attack.py` and the generated `stockfish_v9_attack.ipynb` compile cleanly without syntax errors:
```powershell
cd "c:\OPENAI AI AGENT CYBERSEC\our_work"
python -c "import py_compile; py_compile.compile('attack.py'); print('attack.py bytecode valid!')"
python "C:\Users\intel\.gemini\antigravity-ide\brain\3ca15b07-f7c3-4220-b5bd-7563a666d067\scratch\verify_notebook.py"
```

### 3. Run Local Execution Test Harness
To run the local sandbox test suite (`test_search.py`) and verify that `AttackAlgorithm.run` executes seamlessly and returns valid `AttackCandidate` portfolios:
```powershell
& "C:\Users\intel\pipx\venvs\algokit\Scripts\python.exe" test_search.py
```

### 4. Build / Regenerate Standalone Notebooks
If you modify `attack.py` and wish to rebuild `stockfish_v9_attack.ipynb`:
```powershell
python "C:\Users\intel\.gemini\antigravity-ide\brain\3ca15b07-f7c3-4220-b5bd-7563a666d067\scratch\build_notebook.py"
```

---

## 🔬 What the Next Experiment Is (`v10` Horizon)

Having established `v9` as an **Adaptive Replay-Portfolio Optimizer with Online Bandit Family Allocation**, our next horizon (`v10`) focuses on **Fine-Grained Parameter & Multi-Turn Chain Probing**:
1. **Adaptive Parameter-Value Bandits**: While `v9` allocates across the 4 predicate families (`http.post`, `exec.run`, `file.delete`, `auth.grant_role`), `v10` will introduce secondary online arms to dynamically select optimal argument obfuscations (`URL encodings`, `SQL/Bash command chaining`, `nested JSON escaping`).
2. **Multi-Turn Tool-Hop Synthesis**: Leveraging `max_tool_hops`, `v10` will explore chaining non-sensitive prerequisite tools (`file.read` or `db.query`) to establish trust before executing destructive or exfiltrative payloads in subsequent turns.
3. **Cross-Model Refusal Fingerprinting**: Using early probe latencies to classify whether the evaluation container is running `GPT-OSS` vs `Gemma 4`, instantly switching the initial priors ($\alpha_f, \beta_f$) to the optimal model-specific vulnerability profile.
