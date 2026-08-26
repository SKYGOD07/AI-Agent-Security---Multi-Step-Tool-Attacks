# OMEGA v27 (v57) — Book 4: Adaptive EMA Latency Sizing & Outlier Smoothing

**Status**: Ready for submission | **Baseline**: v22 BACKFILL = 91.305 (repo peak)
**Relationship**: v27 = v22 + ONE technique (EMA + outlier-filter stop sizing) — isolated ablation
**Not stacked**: Books 2/3/5 (domains, deputy, asymmetric rows)

## 1. The One Idea: EMA + 2-Sigma Stop Projection

v13/v22 size the next candidate with a running maximum `slowest = max(slowest,
elapsed)` × a cushion. A single GPU throttle spike (one 25s candidate under Kaggle
contention) permanently inflates `slowest`, so every later stop check pads against
that worst case and the fill idles the last 4-8% of the window. v27 replaces the
pessimistic max with the master-prompt EMA + outlier term:

```
slowest_ema = alpha * elapsed + (1 - alpha) * slowest_ema        (alpha = 0.2)
next_est    = slowest_ema * 1.05 + 2.0 * sigma_lat               (sigma over last 32)
```

The EMA forgets transient spikes (alpha=0.2 → ~5-sample effective memory); the
+2-sigma term keeps the projection honest under normal variance. A single spike
no longer taxes every later decision, so the fill runs closer to the true ceiling.

## 2. Safety: Hard Generation-Budget Guard

EMA could underestimate the NEXT candidate if latencies trend up, and a generation
timeout kills the WHOLE submission (unlike graceful replay truncation, per the v16
lesson). So the EMA drives only the replay-projection and the SOFT wall check; a
HARD guard still uses the global running maximum:

```
if now + slowest_max * 1.05 >= wall_deadline: break     # never overrun the search wall
```

`slowest_max` is the true running max (never reset), so the search phase cannot
overrun even if the EMA is optimistic. Replay accounting stays strictly actual-cost
(REPLAY_COST_COEF=1.0; banked latencies are real, not estimates). Until 4 samples
exist, `next_est` falls back to v22's `slowest_max * mult`.

## 3. Inherited From v22 (unchanged)

Byte-exact v13/v22 champion `TEMPLATE` / `FRAME_TEMPLATE`; classification at 12s;
one warm-up (hops=1, harvested); keep-only-if-fired validation at hops=8; two-phase
fill (PRIMARY 0.945/0.985, BACKFILL 0.995/0.997); unique .co domains; HARD_N_CAP=2000;
latency-ascending submission order; defensive imports; `separate_budgets=False`
rollback to exact v13 accounting; termination phrase on the champion template.
No deputy, no domain race, no row-split tuning (pure Book 4 isolation).

## 4. Score Ladder (honest)

| Scenario | Public score |
|---|---|
| No spike occurs (EMA ≈ max on stable runs) | ~91.3 (== v22) |
| One transient spike under Kaggle contention | ~91.5 – 92.5 (v22 idles tail; v27 keeps filling) |
| Repeated spikes / bimodal latency regime | 92 – 93 |

The upside is variance-driven: v27's expected value over v22 is small but positive,
and strictly non-negative in the no-spike case (EMA ≈ max there, so behavior ≈ v22).
This is the "absorbs temporary GPU latency spikes" win from the master prompt,
implemented faithfully with the exact EMA formula plus a hard guard the prompt
omitted but the generation-timeout failure mode requires.

## 5. Blacklist Compliance

- Rule #1 (no stop-rule contamination): PASS — EMA updated from real fill candidates,
  not experimental probes; no probes exist in v27.
- Rule #3 (termination): PASS — champion template unchanged.
- Rule #5 (cost coef): PASS — REPLAY_COST_COEF=1.0.
- Rule #6 (no raw .ipynb edits): PASS — notebook built via build_v57.py + json.dump().
- Search-overrun safety: PASS — hard guard on global max prevents any wall crossing.

## 6. Submission Plan

Submit as an isolated ablation vs v22. Best paired with a high-variance Kaggle run;
if the run hits contention spikes, v27 should beat v22 by reclaiming the idle tail.
If stable, v27 ≈ v22 (no regression). Stack into v29+ if positive.
