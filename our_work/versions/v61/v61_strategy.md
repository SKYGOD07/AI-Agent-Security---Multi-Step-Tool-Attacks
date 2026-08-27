# OMEGA v31 (v61) — TURBO: fix v22's fast-row over-provisioning (CONSERVATIVE FLOOR)

## Hypothesis
This is the **floor-protector** of the experiment set — no packing, no wording change.
It keeps the byte-exact v22 single-post champion (18 raw/candidate) and fixes one real
sizing bug that leaves candidates on the table on the fast row (gemma).

## The bug in v22
v22 seeds `slowest = SLOWEST0 = 12.0` and updates it as a **running maximum**
(`slowest = max(slowest, elapsed)`). On gemma every sample is ~8.5s < 12.0, so `slowest`
stays **pinned at 12.0** for the whole fill. Every stop-check therefore projects the next
candidate at `12.0 × 1.10 = 13.2s` against a true cost of ~8.5s, so the wall/replay guards
trip with a full over-sized cushion of dead headroom.

## The fix
On the **classified fast row only**, reseed `slowest` to a **robust median** of a few
measured samples (default 5), while keeping `SLOWEST_MULT = 1.10` **unchanged**. The
running max still adapts upward instantly if latency rises, and BACKFILL's 0.995 cap still
makes overrun impossible — so the change can only reclaim dead cushion, never regress.

## Not v28's mistake
v28 regressed (89.06) because it dropped the floor **and** tightened the cushion to 1.05,
which tripped early when latencies rose. TURBO keeps the 1.10 cushion; it only replaces a
pinned-too-high **seed** with the measured level. Slow row (gpt_oss) is untouched — exact
v22 behavior with the 12.0 seed and FRAME template.

## Per-candidate raw math
Unchanged: `18 raw/candidate`. The gain is purely more candidates admitted on the fast row.

## Expected outcome
Small, safe uplift (~+a few candidates on gemma, on the order of the master-prompt's
"+3–5 candidates" estimate). Use as the **safe submission** if the packing experiments
(v29/v30/v32) reveal negligible fixed overhead. Guaranteed ≈ champion floor.
