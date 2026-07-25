# Failure Blacklist

This document records architectural patterns that definitively fail on the Kaggle evaluator. **Never repeat these patterns.**

## 1. Type A: Notebook Execution Exceptions
**Symptoms**: Kaggle returns `Notebook Threw Exception` immediately upon submission.
**Root Cause**: Attempting to execute the attack logic, load the local SDK, or evaluate predicates inside a notebook cell before the official Kaggle evaluation server takes over.
**Offending Code**:
```python
# NEVER DO THIS IN A NOTEBOOK CELL
spec = importlib.util.spec_from_file_location("attack", "attack.py")
module = importlib.util.module_from_spec(spec)
sys.modules["attack"] = module
spec.loader.exec_module(module)
algo = module.AttackAlgorithm()
```
**Fix**: Use the strict 5-cell scaffold. Write `attack.py` to disk using `%%writefile`. Gate all execution behind `os.getenv("KAGGLE_IS_COMPETITION_RERUN")`.

## 2. Type B: Gateway / Replay Timeout Overruns
**Symptoms**: Kaggle returns `Submission Format Error` after ~20-30 minutes of running.
**Root Cause**: The returned candidate list takes longer than 9000 seconds to replay in the hidden environment. The evaluator forcibly terminates the container (`ModelEvaluationTimedOut`), which manifests as a format error because no valid `submission.csv` was finalized.
**Fix**: The algorithm must track `cumulative_replay_cost` by summing the actual measured latency of successful probes during search. Stop adding candidates when `cumulative_replay_cost > 8910s`.

## 3. Type C: Unverified Diversity / Static Padding Dilution
**Symptoms**: Score collapses significantly below baseline (e.g., v15 scored 72; v19 timed out entirely).
**Root Cause**: Padding the `candidates` list with prompts that were not verified to fire during the search phase. 
**Why it fails**: Target models (Gemma, GPT-OSS) often hallucinate, analyze, or get confused by unverified prompts. This leads to maximum `max_tool_hops=8` evaluation loops with zero predicate violations, destroying the replay budget and diluting the score.
**Fix**: Every candidate returned must be verified to fire via a live `env.interact()` trial.

## 4. Type D: Multi-Instruction Tool Collapse (BURST_K)
**Symptoms**: Fire rates collapse from ~50% to < 15%. Score plummets (v18 scored 57).
**Root Cause**: Instructing the model to call a tool multiple times in one interaction (e.g., "Call http.post 4 times"). Target models lack the strict instruction-following capabilities required to reliably execute complex loops without breaking out into text generation.
**Fix**: Prefer single, targeted instructions. (e.g., "Send X to Y using http.post now.")
