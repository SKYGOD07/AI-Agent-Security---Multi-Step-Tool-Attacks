# Stockfish Attack Engine v9: Adaptive Replay-Portfolio Optimizer (Online UCB/Thompson Sampling Allocator & Marginal Gain Selection)

## 1. Executive Summary & The Bottleneck Blocking 110+ Score

In `v8`, we introduced 4 distinct predicate families (`EXFILTRATION`, `UNTRUSTED_TO_ACTION`, `DESTRUCTIVE_WRITE`, `CONFUSED_DEPUTY`) along with a heuristic static **Family Pivot Rule** (`if 3 consecutive attempts yield no new signature, skip to next family`). While `v8` successfully eliminated mono-family `http.post` saturation and recovered performance into the mid-80s band, it plateaued because **its family allocation strategy remained static and heuristic rather than adaptive and online**.

### Why Heuristic Stop/Go Rules Cap Score in the Mid-80s
- **Heterogeneous Target Refusal Surfaces**: When evaluated across diverse benchmark models (`GPT-OSS` vs `Gemma 4`), each model exhibits drastically different vulnerability profiles. A static rule (`try 3 times, then pivot`) wastes compute grinding against rigid refusal boundaries on one model while under-allocating compute to highly yielding arms on another.
- **Generic Novelty vs. Marginal Leaderboard Yield**: Without explicitly scoring candidate branches by their net contribution to the competition objective (`severity + unique signature diversity - measured replay cost - duplicate penalty`), static generators inevitably collect redundant or high-latency branches.

---

## 2. v9 Architectural Transformation: Online Bandit Allocator & Pareto Portfolio

`v9` transforms the attack engine from a static procedural loop into an **Online Multi-Armed Bandit Replay-Portfolio Optimizer**:

### Innovation A: Adaptive Family Allocator (`Thompson Sampling / Beta Distributions`)
Each of the 4 predicate families is treated as a distinct bandit arm:
$$\text{Arm}_f \sim \text{Beta}(\alpha_f, \beta_f) \quad \text{for } f \in \{\text{EXFILTRATION}, \text{UNTRUSTED\_TO\_ACTION}, \text{DESTRUCTIVE\_WRITE}, \text{CONFUSED\_DEPUTY}\}$$
- **Online Reward Update (`record_feedback`)**:
  When a candidate generated from family $f$ discovers a brand-new replay signature or improves coverage:
  $$\alpha_f \leftarrow \alpha_f + 1.0 + \min\left(5.0, \frac{\text{Marginal Gain}}{\max(\text{LAT\_FLOOR\_S}, \text{latency})} \times 0.1\right)$$
- **Automatic Decay for Dead Branches**:
  If a candidate triggers a refusal or exact duplicate without improvement:
  $$\beta_f \leftarrow \beta_f + 1.0$$
This guarantees that **compute naturally flows to families actively producing unique replay signatures** while unproductive branches automatically decay during the run (`Point 1`).

### Innovation B: Marginal Leaderboard Gain (`Point 4`)
Instead of generic novelty, `v9` scores each candidate by its approximated net contribution to the Kaggle evaluation metric:
$$\text{Marginal Gain} = \text{Bonus}_{\text{new\_sig}}(30.0) + \text{Bonus}_{\text{new\_fam}}(50.0) + \sum \text{Severity Gain} - \text{Latency} - \text{Penalty}_{\text{duplicate}}(5.0)$$
Candidates and family beams are ranked directly by **yield per second** ($\frac{\text{Marginal Gain}}{\text{Latency}}$), ensuring the budget is spent exclusively on high-value discoveries.

### Innovation C: Compact Pareto Set Portfolio (`ParetoPortfolioArchive`)
When adding a candidate with `(sig, latency, score, fam, mut_fam, msg_len)` (`Point 5`):
- If `sig` is brand new: retained immediately.
- If `sig` already exists: the new candidate replaces the existing entry **if and only if** it dominates across at least one meaningful dimension (`msg_len < existing.msg_len` OR `latency < existing.latency` OR `score > existing.score`). Strictly dominated entries are dropped immediately.

### Innovation D: Small Beams per Family (`Point 7`)
Instead of global tree search, `ThinStockfishController` maintains a small live beam (`top 3 branches`) per family. If a family's beam fails to yield any new replay signature across consecutive expansions, `allocator.beta[fam] += 2.0`, immediately shifting budget to other families.

---

## 3. Before vs. After Comparison (`v8` vs. `v9`)

| Architectural Dimension | v8 (`Replay-Throughput Controller`) | v9 (`Adaptive Replay-Portfolio Optimizer`) |
| :--- | :--- | :--- |
| **Family Allocation (`Point 1`)** | Heuristic static round-robin with `PIVOT_LIMIT = 3` stop/go counter. | **Online Multi-Armed Bandit** (`Thompson Sampling Beta distributions`), sampling `allocator.select_arm()` to continuously adapt to target vulnerability profiles. |
| **Candidate Valuation (`Point 4`)** | Static violation count + basic family bonus. | **Marginal Leaderboard Gain per Second**: $\frac{\text{new\_sig}(30) + \text{new\_fam}(50) + \text{severity} - \text{cost} - \text{dup}}{\text{latency}}$. |
| **Portfolio Retention (`Point 5`)** | Basic shorter-prompt replacement. | **Compact Pareto Set (`ParetoPortfolioArchive`)**: Retains only entries improving unique coverage, severity, or replay efficiency. Prunes strictly dominated items. |
| **Exploration Structure (`Point 7`)** | Global top-16 archive mutations. | **Small Beams per Family (`top 3 live branches`)**: Local beam expansion that decays arm weight automatically if the beam fails to improve. |
| **Replay Safety (`Point 8`)** | Measured `0.99 * 9000s` safe cap. | Measured `0.99 * 9000s` (`REPLAY_SAFE = 8910s`) safe cap driven by empirical median latencies. |
| **Code Structure (`Point 9`)** | Clean `attack.py` engine (~450 lines). | Simpler, leaner, high-performance `attack.py` (~450 lines) stripped of search bloat. |

---

## 4. Verification & Standalone Artifacts

- **Core Engine File**: [attack.py](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/our_work/attack.py) (Bytecode & local test harness verified).
- **New Standalone Kaggle Notebook**: [stockfish_v9_attack.ipynb](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/our_work/stockfish_v9_attack.ipynb) (Compiled cleanly via `build_notebook.py`; prior notebooks `v8`, `v7`, `v6`, `v5`, `v4`, `v3` preserved untouched).
- **Test Harness Checks**: [verify_notebook.py](file:///C:/Users/intel/.gemini/antigravity-ide/brain/3ca15b07-f7c3-4220-b5bd-7563a666d067/scratch/verify_notebook.py) and [test_search.py](file:///c:/OPENAI%20AI%20AGENT%20CYBERSEC/our_work/test_search.py) (All checks passed).

By converting from static heuristics to an **Adaptive Replay-Portfolio Optimizer with Online Bandit Allocation**, `v9` maximizes unique replay signatures, predicate coverage, and yield-per-second—breaking through the mid-80s plateau toward the **110+ leaderboard ceiling**.
