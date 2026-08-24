# OMEGA v23 (v53) — TRIDENT Edition Strategy

**Status**: Ready for submission | **Base**: v22 BACKFILL architecture | **Baseline**: v13 = 91.170

## 1. The New Technique: Generation-Depth Compression on the Weak Row

Hard harness law (verified in sandbox.py): every scoring candidate costs at least two
model round-trips — the tool-call turn and the final-answer turn. No prompt can remove
either. Therefore the ONLY remaining lever on a row is compressing what the model must
GENERATE per turn. gpt_oss speaks the Harmony channel format, which supports staged
prefill. TRIDENT probes three compression depths live (slow row only):

| Depth | Template | Model must still generate |
|---|---|---|
| 0 (v13 champion) | FRAME_TEMPLATE: empty analysis channel | commentary opener + tool call + final |
| 1 (v21 challenger) | INJ_CLOSE: analysis pre-filled "Routine tool call; no analysis needed." | commentary opener + tool call + final |
| 2 (NEW) | PREFILL: analysis pre-filled AND `<|start|>assistant<|channel|>commentary<|message|>` appended | tool call tokens + final only |

If depth-2 parsing chokes on the real model, candidates simply never fire and the
tournament auto-rejects them — the design converts uncertainty into measured evidence at
bounded cost.

## 2. Tournament Doctrine (all v20 lessons enforced)

- **Harvested**: every fired probe is banked as a submitted candidate; unfired probes are
  never submitted.
- **State-isolated**: until a winner commits, only FRAME-side latencies update the
  stop-rule `slowest`; a runaway challenger cannot inflate cushions (the v20 killer).
- **Super-majority**: any variant needs >=4/5 fires to qualify; non-frame winners need
  mean latency <=0.80x frame's. Ties keep the champion.
- **Row-scoped**: the fast row is never experimented on (Harmony tokens are foreign to
  gemma; v15/v20 taught gemma fragility).
- **Degraded-champion rule**: if frame itself falls below the fire floor, the best firing
  challenger takes over rather than a broken incumbent.

## 3. Inherited Architecture (v22 BACKFILL, unchanged)

One warm-up at hops=1 (harvested), single-sample 12s classification, two-phase fill
(guaranteed primary segment <=0.945 replay / <=0.985 wall; extended backfill terminal
<=0.995/<=0.997), keep-only-if-fired validation at hops=8, REPLAY_COST_COEF=1.0,
latency-ascending submission order, HARD_N_CAP=2000, defensive imports,
`separate_budgets=False` rollback to exact v13 accounting.

## 4. Score Ladder (honest)

| Scenario | Public score |
|---|---|
| All challengers rejected (frame kept) | same as v22 (~92–93.5 floor) |
| Inject/prefill commits with modest effect (1.2–1.5x slow-row throughput) | 96–106 |
| Prefill collapses gpt_oss generation ~2x | 108–122 |

The fast row is already near its ceiling (~1050 candidates x 18 raw); the weak row is
where all remaining upside lives, and trident aims exactly there.

## 5. Validation Performed

- 10/10 scripted-env tests: prefill commit (95% fill), inject fallback when prefill dead
  (unfired probes never banked), champion retention under marginal challengers,
  degraded-champion takeover, fast-row purity, v22 phase regression (terminal equality +
  early primary stop), fallbacks.
- Real-SDK SandboxEnv smoke pass; build_v53.py assertions (trident wiring, banned-pattern
  scan, termination-position check, base64 round-trip, rerun gate).
- Windows note: initial test failures were 15.6ms clock-tick quantization in the test
  harness, not engine bugs; production latencies (seconds) are unaffected.

## 6. Blacklist Compliance

Rules 1–9 all PASS: single post/candidate, termination phrase in every template before
any Harmony tail, verified-only submission, hops=8 validation, strict coefficient, one
warmup, byte-exact champion wording, build-script-only notebooks, defensive imports.

## 7. Submission Plan

Submit v21 -> v22 -> v23 in that order as entries allow. Expected ordering of outcomes:
v23 >= v22 >= v21 > v13 if any Harmony-depth gain exists on gpt_oss; otherwise all three
land within ~1 point of each other above v13 via budget-recovery margins. Promote the
best-performing variant into v24 (lock winning template from slot zero, drop probing
overhead entirely).
