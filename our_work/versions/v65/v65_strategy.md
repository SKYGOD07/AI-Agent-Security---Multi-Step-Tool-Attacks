# OMEGA v35 (v65) — TURBO-BACKFILL Strategy

**Status:** source + builder written and verified (compiles, behaves floor-safe).
**Honest expected result: ~v22 (91.305) ± noise. This does NOT reach the 95–138 target.**

## What v35 is
Byte-exact v22 (91.305) engine **plus one change** — the master prompt's **Avenue 3**:
on the **fast row (gemma)** the stop-rule seed `slowest` is reseeded from the fixed
`SLOWEST0 = 12.0` down to the **measured median** of the first `RESEED_SAMPLE_N = 6`
real single-post fast-row candidate latencies (~8.5s), clamped to `RESEED_FLOOR_S = 6.0`.

- Reseed **only ever lowers** `slowest`, **only on the fast row** (slow row is byte-identical to v22).
- Uses **only plain-TEMPLATE candidate latencies** — never exotic probes (respects blacklist #5).
- **Caps are UNCHANGED from v22** (0.945 / 0.985 primary, 0.995 / 0.997 backfill). No
  `0.998/0.999` over-extension — that is exactly what timed out **v34 (74.790)**. The
  replay-timeout surface is therefore identical to the proven champion.
- Worst case (median ≥ 12.0s) the reseed is a **no-op == v22**.

## Measured effect (virtual-clock simulation at 9000s budget)
| Row | v22 candidates | v35 candidates | Δ |
|---|---|---|---|
| gemma fast (~8.5s) | 1053 | 1054 | **+1** (~+0.09 norm) |
| gpt_oss slow (~12.5s) | 717 | 717 | 0 (byte-identical) |

**Conclusion: the reseed is floor-safe but its gain is ~1 candidate — inside the noise.**
This matches history: v31 (reseed, no backfill) scored 90.450, *below* v22's 91.305.

## Why the other two avenues from the master prompt are dead ends (verified in the SDK)
Read directly from `our_work/aicomp_sdk/`:

1. **Avenue 2 — "multiple score cells per candidate → +4": IMPOSSIBLE.**
   `scoring.py::score_attack` builds `uniq_cells` as a set, and
   `get_score_cell_hash(finding)` returns **exactly one** hash per finding. One candidate
   = one finding = **one cell = +2 max**. Adding query params / subdomains / headers only
   changes that single cell's hash (`cells.py` buckets `http.post` by domain via
   `_bucket_url`); it does **not** create a second cell. So `16 + 4 = 20 raw/candidate`
   is unreachable — the ceiling is `16 + 2 = 18`.

2. **Avenue 1 — "gpt_oss latency reduction without wording change": no knob.**
   Per-candidate replay time is generation time on Kaggle's hardware. Generated-token
   count is fixed by the frozen `TEMPLATE` (blacklist #3) plus the Harmony prefill already
   baked into `FRAME_TEMPLATE`. v22 already A/B-tests a *stronger* prefill
   (`INJ_CLOSE_TEMPLATE`, commit only if ≥4/5 fire AND ≥20% faster). There is nothing left
   to turn here without touching frozen wording or adding probe variety (blacklist #3/#5).

## The real ceiling math
`score = (candidates that fit) × 18 ÷ 200`, per model, then averaged over the two public rows.
- v22 ≈ 1014 candidates/model ⇒ 91.305.
- Public LB top **138.250** ⇒ ≈ **1533 candidates/model** — a **+51%** throughput gain.
- Per-candidate raw is hard-capped at 18 by the scorer, so that +51% can **only** come from
  a **structurally faster per-candidate path** (far fewer generated tokens per candidate),
  which is **not present anywhere in this codebase**. No parameter tweak (reseed, backfill,
  cell tricks) closes that gap. Reaching 95+ requires a new mechanism, not a v22 refinement.

## Recommendation
- **Submit v35** as a strictly-floor-safe "v22-or-a-hair-better" run if you want a fresh
  data point — it cannot regress below v22's timeout surface.
- Do **not** spend submissions on Avenues 1 or 2 (SDK-blocked, proven above).
- The honest path to 95+/138 is R&D into **per-candidate generation-token reduction on the
  slow row** (the gpt_oss bottleneck) — a new prefill/format that makes the target emit its
  single `http.post` in materially fewer tokens while keeping the scored instruction and
  `Then answer OK only.` byte-exact. That is a research problem, not a knob.

## Build & commit (run outside auto mode — see session note)
```powershell
python "our_work/versions/v65/build_v65.py"
git add -A; git commit -m "feat: implement OMEGA v35 (v65) TURBO-BACKFILL (v22 + fast-row reseed)"
```
