# v10 Replay Throughput Report

## Summary
The v10 implementation replaces static family allocation with adaptive Multi-Armed Bandit (Thompson Sampling / UCB) based family allocation. It retains the JED-style prompt probing frontend to select the fastest reliable attack format but shifts all subsequent budget into dynamic replay-signature coverage.

## Key Changes
1. **Adaptive Family Allocator**: Predicts the best predicate family to probe using empirical marginal gains per second of runtime. Penalizes slow and repetitious branches.
2. **Thin Stockfish**: Reduced tree depth in favor of wider family beams and aggressive pruning of branches that don't produce new `CellSignatures`.
3. **Replay Cost Strictness**: Halts automatically when measured trace latencies sum to 0.99 * 9000 seconds, virtually guaranteeing submission validity.

## Preliminary Offline Throughput Estimates
- Expected valid signatures per run: ~100-150 depending on model response latency.
- Expected replay execution time: capped effectively at ~8900s.
- Predicate diversity: Expected near-even coverage if all families are equally vulnerable; dynamically shifts to most vulnerable family in case of asymmetric defense.
