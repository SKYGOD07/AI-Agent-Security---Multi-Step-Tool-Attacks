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

---

## Absolute Rules (Derived from Failures)

1. **Never add unverified candidates** to the returned portfolio. Every returned candidate must have been live-probed and confirmed firing during the fill phase.
2. **Never multiply per-candidate replay cost**. BURST_K must stay 1. SLOW_MULTIPOST_N must stay 1. Each candidate = one http.post = one replay slot.
3. **Never edit .ipynb with string replacement**. Always use `json.load()` / `json.dump()` via Python.
4. **Preserve the minimal notebook scaffold**: write `attack.py`, write `submission.csv` with exact `Id,Score` placeholder, rerun gating.
5. **The throughput bottleneck is fill efficiency**, not template diversity or per-candidate yield. More candidates × single-post × verified fire = higher score.
