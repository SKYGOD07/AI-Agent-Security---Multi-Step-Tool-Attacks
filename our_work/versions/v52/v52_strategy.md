# OMEGA v22 (v52) — BACKFILL Edition Strategy

**Status**: Ready for submission | **Companion to**: v21 SAFE-HARVEST | **Baseline**: v13 = 91.170
**Relationship**: v22 = v21 + two-phase budget architecture (floor insurance + wider terminal window)

## 1. The New Idea: Two-Phase Cushion Architecture

Honest finding from development: because `REPLAY_COST_COEF = 1.0` makes measured replay
cost track search wall-clock almost exactly, a "backfill" phase CANNOT create extra
expected candidates beyond what its terminal guard fractions allow (verified empirically:
phased == single-phase at identical terminal caps). What phasing DOES buy is risk-shaping:

1. **PRIMARY segment (replay ≤ 0.945x, wall ≤ 0.985x)**: bulletproof under every timing
   model — even if Kaggle's replay environment runs several percent slower than the search
   environment (different GPU contention, model reload overhead), this segment completes.
   v13/v21 sized single lists near 0.99x with no such floor guarantee; a slow-replay
   scenario truncates their tails (gracefully, but losses land on real candidates).
2. **BACKFILL segment (replay ≤ 0.995x, wall ≤ 0.997x)**: extends utilization past v21's
   wall (0.993 -> 0.997 ≈ +36s ≈ +3-4 candidates/model) while keeping worst-case total
   projection strictly under 100% of either window. No overrun scenario exists by
   construction; v16's partial-scoring behavior is treated as emergency margin only.

Submission order = latency-ascending across both segments (all candidates worth 18 raw,
so latency-greedy ordering maximizes completed count under ANY truncation).

## 2. Everything Inherited From v21 (unchanged)

- Byte-exact v13 champions (TEMPLATE / FRAME_TEMPLATE); classification at 12s threshold.
- Bounded state-isolated slow-row A/B: FRAME vs INJ_CLOSE x5 each, commit inject only on
  >=4/5 fires both sides AND mean_lat(inject) <= 0.80 x frame. Harvested throughout.
- Exactly one warm-up (hops=1, harvested), keep-only-if-fired validation at hops=8,
  REPLAY_COST_COEF=1.0, unique .co domains, HARD_N_CAP=2000, defensive imports,
  `separate_budgets=False` rollback to exact v13 accounting (single phase).

## 3. Score Ladder (honest)

| Scenario | Public score |
|---|---|
| Champions kept everywhere, replay env normal | ~92 – 93.5 |
| Champions kept, replay env slower than search (v22 floor protection kicks in) | ~90 – 92 (v21 in same scenario: ~88 – 90) |
| Inject commits on gpt_oss (1.2–1.5x row throughput) | 96 – 106 |
| Inject commits with ~2x collapse | 108 – 120 |

v22's expected value over v21 is small positive (+0.3–0.8) plus meaningful tail-risk
reduction. The path to 95+ runs through the A/B commit on gpt_oss; the path beyond that
(130+) still requires multi-predicate economics to flip positive — parked behind gates.

## 4. Validation Performed

- 13/13 scripted-env tests: primary guard engages early (30%-config stopped at 22/72),
  backfill resumes to identical terminal as single-phase (72==72), A/B commit/reject paths
  intact, shared-mode rollback, fallbacks, uniqueness, warmup-once.
- Real-SDK SandboxEnv smoke pass; build_v52.py 31/31 assertions (phase-loop structure,
  banned-pattern scan, termination-position check, base64 round-trip).

## 5. Blacklist Compliance

Unchanged from v21 (rules 1-9 all PASS): single post per candidate, termination phrase in
all templates, verified-only submission, hops=8 validation, strict cost coefficient, one
warmup, byte-exact champion wording.

## 6. Submission Plan

Submit v21 first (cleanest baseline+upside). Submit v22 second — it hedges the
replay-slower-than-search tail risk and adds the terminal-window extension. Whichever of
the two scores higher becomes the base for v23 (promote winning template from the start;
revisit deputy only as a measured per-row side-portfolio).
