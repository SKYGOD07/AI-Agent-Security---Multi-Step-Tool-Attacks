# OMEGA v28 (v58) — Book 5: Dual-Track Asymmetric Model-Specific Strategy Split

**Status**: Ready for submission | **Baseline**: v22 BACKFILL = 91.305 (repo peak)
**Relationship**: v28 = v22 + ONE technique (per-row asymmetric tuning) — isolated ablation
**Not stacked**: Books 2/3/4 (domains, deputy, EMA sizing)

## 1. The One Idea: Per-Row Tuning, Not Just Per-Row Template

v13/v22 already SELECT a different template per row (FRAME on gpt_oss, plain
TEMPLATE on gemma) but use one-size-fits-all SIZING: the same `SLOWEST0=12.0`
seed, `SLOWEST_MULT=1.10`, and replay fractions for both rows. That over-provisions
the fast row — gemma runs well under 12s, so a 12.0 stop-projection seed dominates
the running max and pads every fast-row stop check against a latency gemma never
reaches, idling fast-row budget. v28 gives each row its own tuning:

| Parameter | Fast row (gemma, <12s) | Slow row (gpt_oss, >12s) |
|---|---|---|
| `slowest` seed | measured classification latency (no 12.0 floor) | 12.0 (v22-exact) |
| `SLOWEST_MULT` | 1.05 (tighter) | 1.10 (v22-exact) |
| PRIMARY replay/wall | 0.955 / 0.988 | 0.945 / 0.985 (v22) |
| BACKFILL replay/wall | 0.996 / 0.998 | 0.995 / 0.997 (v22) |
| Template | TEMPLATE (plain) | FRAME_TEMPLATE (Harmony prefill) |

**Fast row** → pure candidate VOLUME: the measured seed makes the stop projection
track gemma's true ~fast latency (the 12.0 seed is the gpt_oss scale, not gemma's),
the 1.05 cushion tightens end-of-fill, and higher fracs push toward 1100+.
**Slow row** → token PREFILL optimization, byte-exact v22: FRAME_TEMPLATE Harmony
assistant-token prefill (the verified champion) + v22 backfill sizing.

## 2. Why Seeding From One Sample Is Safe

Dropping the 12.0 floor for the fast row seeds `slowest` from the single
classification measurement. This is safe because the running maximum self-corrects
long before the wall binds: early in the fill the wall is thousands of seconds
away (an optimistic projection cannot overrun with that much headroom), and late
in the fill `slowest` is calibrated by hundreds of real samples, so the wall check
`now + slowest*mult >= wall` stops in time. The fast-row fracs stay strictly < 1.0,
so the worst-case total stays under 100% of the window by v22's construction.

## 3. Blacklist Note: No Prompt Compression (rule #9)

The master prompt's Book 5 lists "micro-prompts" as a fast-row volume lever.
That lever is blacklist rule #9 — v15 trimmed exactly these words and regressed
89.640 → 88.920. v28 does NOT compress the champion `TEMPLATE` wording; fast-row
volume comes entirely from TIMING (measured seed + tighter cushion + higher
fracs), not from prompt shortening. The champion template stays byte-exact.

## 4. Inherited From v22 (unchanged)

One warm-up (hops=1, harvested); classification at 12s; keep-only-if-fired
validation at hops=8; two-phase fill structure; REPLAY_COST_COEF=1.0; unique .co
domains; HARD_N_CAP=2000; latency-ascending submission order; defensive imports;
`separate_budgets=False` rollback to exact v13 accounting; termination phrase.
No deputy, no domain race, no EMA (pure Book 5 isolation).

## 5. Score Ladder (honest)

| Scenario | Public score |
|---|---|
| Fast-row seed ≈ 12.0 anyway (gemma unexpectedly slow near 12s) | ~91.3 (== v22) |
| Fast-row seed meaningfully < 12.0 (typical gemma) | ~92 – 93 (+fast-row candidates) |
| Fast row reaches the 1100+ volume target with budget to spare | 93 – 95 |

The prior session's "Book 5 already exists" verdict referred to per-row TEMPLATE
selection (which v22 already does). v28's distinct contribution is per-row SIZING
— the measured fast-row seed + tighter cushion — which v22 does NOT do.

## 6. Blacklist Compliance

- Rule #1 (no stop-rule contamination): PASS — slowest updated from real fill
  candidates only; no probes.
- Rule #3 (termination): PASS — champion template unchanged.
- Rule #5 (cost coef): PASS — REPLAY_COST_COEF=1.0.
- Rule #9 (no prompt compression): PASS — volume from timing, not micro-prompts.
- Rule #6 (no raw .ipynb edits): PASS — notebook built via build_v58.py + json.dump().

## 7. Submission Plan

Submit as an isolated ablation vs v22. The fast-row measured-seed is the
highest-leverage lever; if it banks materially more gemma candidates than v22,
promote the per-row sizing into a consolidated v29+ and combine with whichever of
v26/v27 also scored positive.
