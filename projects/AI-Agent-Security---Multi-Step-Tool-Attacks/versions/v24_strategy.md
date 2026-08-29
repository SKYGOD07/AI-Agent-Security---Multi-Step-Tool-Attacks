# Version 24 — Strategy & Rationale

## Goal: Break the 90+ Barrier

| Version | Public Score | Architecture |
|---|---|---|
| v16 | 87.660 | Single TEMPLATE + FRAME_TEMPLATE split, REPLAY_SAFE=0.97 |
| v69 | 88.200 | Identical to v16 (natural variance) |
| v23 | 53.190 | v16 + PROBE_HOPS=1 (broken: REPLAY_COST_COEF=2.0 miscalibrated) |
| **v24** | **target: 90+** | **5-template fire-rate race, REPLAY_SAFE=0.99** |

## What v24 Changes

### 1. Five-Template Fire-Rate Race (replaces SPLIT_BY_LATENCY)
v16 hard-codes two templates: `TEMPLATE` (verbose, for gemma) and `FRAME_TEMPLATE` (Harmony injection, for gpt_oss). The model is identified by latency classification.

v24 probes **all 5 templates** live for `PROBE_REPS=5` rounds, then the fire-rate selector picks the one with the lowest `effective_cost = median(latency) / fire_rate`. This is strictly better because:
- `inj_close` collapses gpt_oss reasoning → ~2× candidates on the slow row
- `bare`/`bare_ok` may beat `plain` on gemma (fewer generated tokens)
- The selector is model-adaptive: whatever fires cheapest wins, no hard-coded split

### 2. REPLAY_SAFE = 0.99 (from 0.97)
- v16 leaves 3% margin = 270s unused replay budget
- v24 leaves 1% margin = 90s unused replay budget
- Reclaims ~180s → ~20 more gpt_oss candidates, ~30 more gemma candidates
- Safe because: search probes at `max_tool_hops=8` (same as replay), so measured latency = actual replay cost. The 90s margin covers model-load variance.

### 3. Replay-Cost-Capped Fill
The fill loop stops when `replay_cost + fill_unit > REPLAY_SAFE * 9000`. Each candidate's measured latency is accumulated. This is a direct (not estimated) measure of replay cost — self-calibrating per model.

## What Stays the Same
- Single http.post per candidate (BURST_K equivalent = 1)
- SECRET_MARKER test vector
- Only live-verified candidates returned
- No static padding
- Proper 5-cell notebook scaffold with exact Id,Score placeholder
- PROBE_HOPS = 0 (probes at max_tool_hops=8)

## Provenance
The attack.py is decoded from the `jed-multi-step-attack.ipynb` notebook, which uses the "RELAY PUSH100" architecture — itself adapted from "jed-fill-v26-replaysafe" (scored 67; its v24 ancestor scored 87.9). The key techniques documented in its header are:
1. **Harmony injection** (inj_close) for gpt_oss reasoning collapse
2. **Per-model fire-rate selector** for optimal template selection  
3. **Replay-safe sizing** (the Format-Error fix) for safe candidate capping
