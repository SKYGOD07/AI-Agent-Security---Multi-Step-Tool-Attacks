# OMEGA v24 (v54) QUAD + v25 (v55) ADAPTIVE — Strategy & Book Review

**Baselines**: v13 = 91.170 | v20 = 86.070 (regression) | Target: beat 91.170, stretch 95+

## 0. Five-Book Review Verdicts (evidence-based triage)

| Book | Verdict | Evidence |
|---|---|---|
| v24 "Supply-Side Prompt Compression" | **REJECTED** | Blacklist rule #9: v15 trimmed exactly these words and regressed 89.640→88.920. The "~0.4s/candidate" claim is physically wrong — 10 fewer prefilled characters cost microseconds on GPU prefill, not 0.4s. The legitimate version of this idea (compressing model-GENERATED tokens) is already shipped as v23 PREFILL |
| v25 "BPE-optimized domains" | **ACCEPTED (modified)** | Real mechanism: domains appear in model-generated tool args, so shorter labels save generated tokens. Modified: 3-letter pure-alpha space (disjoint from legacy digits = collision-proof), label "key" remapped (3-letter ultra-dangerous guardrail pattern), adoption via measured race not blind swap |
| v26 "Target-gated deputy" | **ACCEPTED (modified)** | The +4.4pt claim ignores slot displacement: deputies at >1.222× latency evict more singles than their bonus replaces. Correct form: density-gated tournament adoption (measured, reversible), plus a fast-row micro-race |
| v27 "EMA latency sizing" | **ACCEPTED (modified)** | Running-max `slowest` was v20's killer #2. Implemented as p90-of-recent-window with hard generation-deadline guard (EMA alone could underestimate into a fatal search overrun) |
| v28 "Asymmetric rows" | **ALREADY EXISTS** | v13's latency classification + v21–v23's row-scoped tournaments are exactly this architecture |

## 1. OMEGA v24 QUAD (v54)

1. **Quad density tournament (slow row)**: frame / inject / prefill / deputy selected by
   MEASURED point-density = (mean fired predicate points + cell) / mean fired latency.
   Deputy (exfil+notify combo, verified to fire EXFIL+CONFUSED_DEPUTY=22 raw locally)
   wins only where its extra round-trip is genuinely throughput-positive (>8% density
   advantage over frame). All doctrine guards: harvested, state-isolated, ≥3/4 fires.
2. **Fast-row deputy micro-race**: same gates on the fast row (4v4 slots). Reversible;
   champion retained on ambiguity.
3. **Domain scheme race**: legacy vs token-frugal 3-letter labels alternate over the
   committed template; short adopted only with non-inferior fire rate AND ≥3% faster mean.
   Runtime uniqueness assertion over all banked URLs.

Expected: floor = v23 behavior (~92–93.5); upside if deputy density wins on either row
(+0.5–4) or short domains measure real (+0.3–1).

Validated: 14/14 scripted tests (density wins/rejections both rows, scheme race adopt/
reject, uniqueness across mixed schemes, fallbacks), SDK smoke pass, builder assertions.

## 2. OMEGA v25 ADAPTIVE (v55)

v24 + p90-window stop sizing: `next_est = max(p90(recent 32 fired latencies) × mult)`
falling back to v13's `slowest×mult` until 8 samples exist. The running-max cushion —
documented cause of v20's premature stops — no longer lets one GPU spike tax every later
decision. Safety: an unconditional HARD guard (`now + slowest×1.05 ≥ wall → break`) can
still never allow a search-phase overrun (generation timeout kills whole submissions,
unlike graceful replay truncation); replay accounting stays strictly actual-cost.

Measured properties (scripted): single 400ms spike retains 92% of clean-run supply;
mixed fast/slow regime finishes at 7.81s/8.00 budget while banking honestly; bloated
static seed costs only ~5 candidates under adaptive vs permanent waste under max.

## 3. Submission Ladder

v21 → v22 → v23 → **v24** → **v25** as entries allow; each isolates one technique family
so score deltas attribute cleanly. Promote the best into v26 (lock winners from slot
zero, strip all probing).
