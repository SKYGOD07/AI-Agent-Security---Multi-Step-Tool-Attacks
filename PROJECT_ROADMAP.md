# Project Roadmap: OMEGA Attack Discovery Engine (Updated Aug 2026)

This roadmap outlines the research and development phases for the OMEGA Attack Discovery Engine targeting the Kaggle **AI Agent Security — Multi-Step Tool Attacks** competition.

## Phase 1: Foundations & Baselining ✅ COMPLETE
- [x] Establish modular codebase (Stockfish v1–v16 series).
- [x] Implement live validation-fill (v12 breakthrough: 100% fire efficiency).
- [x] Implement Harmony token forging for `gpt_oss` chain-of-thought bypass (v16: 87.660).
- [x] Implement replay-safe sizing with measured latency cap (v16+).

## Phase 2: Architecture Convergence & 90+ Score ✅ COMPLETE
- [x] Port proven architecture from benchmark notebooks (v69, jedforce-1, 90.09).
- [x] Build OMEGA Series attack engine (v31–v43).
- [x] Implement latency-split single-post fill with per-model template routing.
- [x] Fix warm-up double-counting bug (OMEGA v5: 89.640).
- [x] Prove that multi-post / multi-hop stacking causes regression (v7: 88.335, v12: 85.970).
- [x] Prove that prompt termination omission causes runaway generation (v9: 86.355).
- [x] **Breach 90.0 barrier with OMEGA v13: 91.170!** 🏆

## Phase 3: High-Precision Incremental Optimization (CURRENT)
- [x] `REPLAY_SAFE_FRAC = 0.994` (8946s cap, 54s safety cushion) → +3.2 candidates.
- [x] `SLOWEST_MULT = 1.10` (tighter end-of-fill cushion) → +1.5 candidates.
- [x] `SPLIT_CLASSIFY_N = 1` (1-sample classification) → +1.5 candidates.
- [x] `SLOWEST0 = 12.0` (tighter initial latency seed) → +1.0 candidate.
- [ ] Push further: `REPLAY_SAFE_FRAC = 0.996`, `SLOWEST_MULT = 1.05` for 92.0+ target.

## Phase 4: Score Ceiling Analysis & Next Breakthrough (FUTURE)
- [ ] Analyze evaluator variance (v13 scored 91.170 and 89.685 on two runs of same notebook).
- [ ] Investigate whether Kaggle evaluator latency varies between submissions.
- [ ] Test further replay fraction expansion while maintaining 0% timeout risk.
- [ ] Explore prompt compression for faster tokenization per candidate.
