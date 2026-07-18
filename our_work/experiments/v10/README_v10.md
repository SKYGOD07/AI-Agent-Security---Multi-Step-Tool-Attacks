# v10 Attack Implementation

This is the v10 implementation of the multi-step tool attack for the AI Agent Security Kaggle Competition.

## Strategy

1. **JED Probing Front-End**:
   - Probe exactly 5 templates (`plain`, `bare`, `bare_ok`, `inj_close`, `inj_commentary`).
   - Run 5 probes per template.
   - Select the best template using `median(successful_probe_latency) / fire_rate`.

2. **Adaptive Family Allocation**:
   - Each predicate family (EXFILTRATION, UNTRUSTED_TO_ACTION, DESTRUCTIVE_WRITE, CONFUSED_DEPUTY) is treated as a multi-armed bandit arm.
   - Rewards new signatures, coverage, severity, and efficiency.
   - Penalizes duplicates, refusals, and slow candidates.

3. **Thin Stockfish Controller**:
   - Implements move ordering, caching, deduplication, light prioritization, and early stopping.
   - No deep alpha-beta exploration or decorative pruning layers that don't improve replayable yield.

4. **Pareto Portfolio**:
   - Keeps candidates that improve unique replay signatures, predicate family coverage, severity, or replay cost efficiency.
   - Strictly dedupes by signature (tool sequence + predicate family + mutation family + prompt hash).

5. **Replay Safety**:
   - Stops candidate collection when cumulative measured replay cost reaches 0.99 * 9000 seconds or the candidate cap is met.
