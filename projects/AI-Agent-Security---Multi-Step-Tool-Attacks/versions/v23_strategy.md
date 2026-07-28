# Version 23 — Strategy & Rationale

## Base: v16 (87.660 public score)
v23 is built from an exact byte-level copy of v16 using `json.load()` / `json.dump()` (never string replacement on `.ipynb`). The notebook scaffold is identical: 5 cells, `%%writefile attack.py`, exact `Id,Score` placeholder, rerun gating.

## The Single Change: PROBE_HOPS = 1 + REPLAY_COST_COEF = 2.0

### What it does
v16 probes every candidate at `max_tool_hops=8` (the same hop cap the replay uses). The exfil event fires at hop-0 (before the wrap-up hop), so a candidate fires identically whether you probe it at 1 hop or 8. Probing at 1 hop skips the scoring-irrelevant wrap-up generation, giving a **~1.5-2x faster fill**.

This means: in the same 9,000s budget, the fill loop can verify and keep **~1.5-2x more candidates**. Each candidate is still a single `http.post` with `SECRET_MARKER`, costing the same replay time as v16. More verified candidates × identical per-candidate replay cost = higher score.

### Why it's safe
- `REPLAY_COST_COEF = 2.0` conservatively scales each hops=1 measurement back up to the hops=8 replay cost. This prevents `REPLAY_SAFE_SIZING` from under-counting and overflowing the replay budget.
- `BURST_K = 1` (unchanged) — single post per candidate.
- `SLOW_MULTIPOST_N = 1` (unchanged) — single post on slow row.
- No static padding added. Every candidate is live-verified.

### What stays identical to v16
- All templates (TEMPLATE, FRAME_TEMPLATE)
- SPLIT_BY_LATENCY = True, SPLIT_THRESHOLD_S = 12.0, SPLIT_CLASSIFY_N = 8
- REPLAY_SAFE_SIZING = True, REPLAY_SAFE_FRAC = 0.97
- MARGIN_S = 47.0, FILL_BUDGET_FRAC = 0.95
- HARD_N_CAP = 2000, FALLBACK_N = 300
- The entire notebook wrapper (cell 3: serve, cell 4: submission.csv)

## Failure Modes Avoided
| Blacklisted Pattern | v23 Status |
|---|---|
| Static unverified padding (v19) | ❌ Not present |
| BURST_K > 1 (v18, v22) | ❌ BURST_K = 1 |
| SLOW_MULTIPOST_N > 1 (v22) | ❌ SLOW_MULTIPOST_N = 1 |
| .ipynb string replacement (v21) | ❌ Built with json.load/dump |
| Decaying diversity layer (v20) | ❌ Not present |

## Expected Outcome
If PROBE_HOPS=1 delivers the documented 1.5-2x fill throughput gain:
- v16 gemma row (~900 candidates) → v23 gemma row (~1350-1800 candidates)
- v16 gpt_oss row (~375 candidates) → v23 gpt_oss row (~560-750 candidates)
- Conservative REPLAY_COST_COEF=2.0 may leave some replay budget on the table, but it guarantees no overrun.
