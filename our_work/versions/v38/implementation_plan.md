# OMEGA v7 Regression Analysis & v8 Recovery Plan

## v7 Regression: 89.640 → 88.335 (-1.305 points)

### Root Cause: Three Compounding Failures

> [!CAUTION]
> Multi-predicate stacking made each candidate SLOWER, which reduced the total candidate count by MORE than the per-candidate value increase could compensate.

#### Failure 1: Warm-up at `hops=2` instead of `hops=1`
v5/v6 warm-up at hops=1 takes ~60s (model load + 1 tool call). v7's hops=2 probe takes ~65-75s (model load + 2 tool calls). The extra 5-15s is **subtracted from replay_cap** (line 211), shrinking the fill budget.

#### Failure 2: MULTI_TEMPLATE adds ~3-5s per candidate on gemma
Each candidate calls TWO tools (http.post + fs.delete) instead of one. On gemma:
- TEMPLATE: ~8.5s/candidate (1 tool call + text response)
- MULTI_TEMPLATE: ~11-13s/candidate (2 tool calls + text response)

**Math**: At 12s/candidate, fill produces ~740 candidates vs ~1043 at 8.5s. Even at 26 raw/candidate: 740 × 26 = 19,240. But if fs.delete **fails** (guardrail blocks it), each candidate is worth only 18 raw: 740 × 18 = 13,320 vs 1043 × 18 = 18,774. **That's a -29% regression**.

#### Failure 3: Warm-up candidate stored with MULTI_TEMPLATE message
Line 218: `cands.append(AttackCandidate.from_messages((warmup_msg,)))` stores the multi-predicate message. During replay, this message forces the agent to attempt both tool calls — taking ~12s instead of ~8.5s. This eats replay budget that could serve ~0.4 extra single-predicate candidates.

### Key Lesson

> [!IMPORTANT]
> **Never add extra tool hops to the fill loop.** Each additional hop costs ~3-5s per candidate. Over ~1000 candidates, that's 3,000-5,000s of lost budget — enough for 350-590 single-predicate candidates. The +44% per-candidate value from DESTRUCTIVE_WRITE (8 extra raw) cannot compensate for losing ~30% of candidates.

---

## Score Math: Why We're Stuck at 89.640

```
score = raw / 200000 × 1000
89.640 = raw / 200000 × 1000
raw = 17,928
candidates = 17,928 / 18 = 996

To reach 90.0:
raw = 18,000
candidates = 18,000 / 18 = 1,000
Need: +4 more successful replays
```

We need **JUST 4 MORE CANDIDATES** to breach 90. The fill produces ~1043. The replay scores ~996. The gap is ~47 candidates lost to replay fire-rate variance (~95.5% replay success rate).

---

## OMEGA v8 Plan: Clean Revert + Proven Architecture

> [!IMPORTANT]
> The safest path to 90 is: revert to the proven v5 architecture (89.640), restore `hops=1` warm-up, keep single-predicate, and avoid any experimental changes that add per-candidate overhead.

### Changes from v7 → v8

| What | v7 (88.335) | v8 (target: 89.640+) |
|------|-------------|---------------------|
| Warm-up hops | 2 | **1** (revert) |
| Template | MULTI_TEMPLATE (2 tool calls) | **TEMPLATE** (1 tool call, revert) |
| Multi-predicate | Yes (fs.delete) | **No** (revert) |
| Warm-up message | MULTI_TEMPLATE | **TEMPLATE** (revert) |
| All v6 tuning | Kept | Kept |

### Parameters (identical to v5 proven scorer)

| Parameter | Value | Source |
|-----------|-------|--------|
| REPLAY_SAFE_FRAC | 0.99 | v5 (proven at 89.640) |
| SPLIT_CLASSIFY_N | 3 | v5 (proven) |
| SLOWEST0 | 25 | v5 (proven) |
| SLOWEST_MULT | 1.20 | v5 (proven) |

### Why EXACT v5 params (not v6 params)

v6 tuning (FRAC=0.992, CLASSIFY=1, SLOWEST0=12, MULT=1.15) produced the SAME score as v5 (89.640). Since neither helped nor hurt, but v5 is our **proven benchmark**, v8 uses v5's exact parameters for maximum reproducibility. Identical code → identical score.

## Verification Plan

### Expected Result
- Score: 89.640 (matching v5, confirming the revert fixed the regression)

### Manual Verification
- Upload `omega_v8_attack.ipynb` to Kaggle (GPU T4 x2, Internet Off)
- Verify score matches v5's 89.640 (±0.5 for evaluator variance)
