# Failure Blacklist — Permanent Memory

## v19: Submission Format Error
**Root cause**: Static unverified diversity padding inflated replay cost without guaranteed new fired traces. The notebook appended CONFUSED_DEPUTY, DESTRUCTIVE_WRITE, and extra EXFIL candidates that were never live-verified during the fill. On a replay-validated benchmark, padding candidates that never proved themselves burns replay budget and can flip the run into a submission failure. The earlier v8 analysis says the real bottleneck is mono-family exfil saturation and grinding dead branches, not more template spam.

## v20: Scored 2.250 (near-zero)
**Root cause**: Diversity layer decayed too quickly. The code is structurally safe (probe → select → seed → fill → dedup → compact portfolio, only keeps candidates that actually fired), but it is too conservative. The controlled live diversity layer (Phase E with `div_consecutive_misses < 4`) does not generate enough distinct fired traces to move the score. The `SignatureArchive` dedup further compacts the portfolio. Combined with `PROBE_REPS = 5` (vs v16's 3) eating more search time and `MARGIN_S = 60.0` (vs v16's 47.0) leaving a bigger cushion, too few candidates end up in the returned set.

## v21: Submission Format Error  
**Root cause**: Notebook JSON got corrupted during PowerShell string replacement. The `.ipynb` file was edited with `$content -replace` which mangled the JSON structure. Never edit `.ipynb` files with raw string replacement — always use a JSON parser.

## v22: Submission Format Error
**Root cause**: `BURST_K=4` and `SLOW_MULTIPOST_N=4` multiplied per-candidate replay cost. On a benchmark that replays every returned candidate under a fixed budget, this multiplies replay cost per candidate. The rerun overflows the replay window and gets marked as a format/error-style failure. This is the same class of mistake as v19: anything that bloats the returned portfolio's total replay cost without guaranteed new replay value.

## v18: Scored 57.285 (regression from 87.660)
**Root cause**: Same BURST_K=4 problem but in a different architecture. The v18 template-race design uses BURST_K=4 to create multi-post messages. Each candidate requires 4x the replay time. The fill loop does correctly verify each candidate fires, but the per-candidate cost is ~4x so fewer total candidates fit in the replay budget.

## v23: Scored 53.190 (regression from 87.660)
**Root cause**: `PROBE_HOPS=1` with `REPLAY_COST_COEF=2.0` miscalibrated the fill loop's stop condition. The `_replay_stop()` function estimates the next candidate's cost as `slowest * SLOWEST_MULT * replay_cost_coef`, but with hops-1 probing, `slowest` stays artificially low (~half of hops=8). The 2× coefficient doesn't compensate correctly because the stop condition uses `slowest * SLOWEST_MULT` (the cushion estimate) not the actual per-candidate elapsed. The net effect: the fill loop either over-fills (replay overruns, losing candidates) or the wall-clock deadline binds first (under-filling). Either way, fewer scored candidates than v16.

## v25: Submission Format Error
**Root cause**: v25 failed because it increased per-candidate replay cost by packing two URLs into each template without recalibrating replay-safe sizing. Do not change the notebook wrapper when the failure is replay-budget related. Preserve the verified Id,Score output path, keep only candidates that fired in live validation, and size the returned portfolio by measured replay cost, not by search-time budget. Never add denser templates or static padding unless the replay cap is re-estimated from the actual candidate shape.

## v26: Scored 57.210 (regression from 84.645)
**Root cause**: `REPLAY_SAFE=0.92` + `REPLAY_COST_COEF=1.15` was too conservative. The dual-URL templates also reduced fire-rate (model often failed to execute both http.post calls). Combined effect: far fewer scored candidates than v24's single-URL approach. The dual-URL template experiment is a dead end — it doubles replay cost per candidate while reducing fire-rate.

## v27: Submission Format Error
**Root cause**: Three compounding bugs: (1) Fragile direct imports (`from aicomp_sdk.attacks.contracts import ...` and `from aicomp_sdk.core.env.api import AttackEnvProtocol`) crashed when the SDK path differed on Kaggle rerun. (2) No defensive `__init__` — if base class doesn't set `self.config` as dict, every `self.config.get()` call crashes. (3) Over-tightened margins (`MARGIN_S=42 + FILL_BUDGET_FRAC=0.97 + MARGIN_FLOOR_MIN=3.0`) all at once could overshoot replay budget. Fix: use jedforce-1's defensive try/except imports, defensive `__init__`, base64 encoding, always-serve pattern, and moderate (not aggressive) margin tuning.

---

## Absolute Rules (Derived from Failures)

1. **Never add unverified candidates** to the returned portfolio. Every returned candidate must have been live-probed and confirmed firing during the fill phase.
2. **Never multiply per-candidate replay cost**. BURST_K must stay 1. SLOW_MULTIPOST_N must stay 1. Each candidate = one http.post = one replay slot.
3. **Never edit .ipynb with string replacement**. Always use `json.load()` / `json.dump()` via Python.
4. **Preserve the minimal notebook scaffold**: write `attack.py`, write `submission.csv` with exact `Id,Score` placeholder, rerun gating.
5. **The throughput bottleneck is fill efficiency**, not template diversity or per-candidate yield. More candidates × single-post × verified fire = higher score.
