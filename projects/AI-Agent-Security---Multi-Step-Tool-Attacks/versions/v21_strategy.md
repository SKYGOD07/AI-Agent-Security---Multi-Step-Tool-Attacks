# Version 21 Strategy & Growth (Baseline Re-establishment)

## Core Philosophy: The Re-established Baseline
`v21` marks a critical pivot in our algorithmic evolution. While its codebase is heavily inspired by the successful `v16` (scoring 87.660), the *strategic intent* behind `v21` is entirely different. It serves as our "clean slate" after the disastrous `v19` and `v20` experiments.

## What is different from v16?
1. **The Blacklist Constraint**: `v16` succeeded because it naturally adhered to a safe replay budget, but we didn't fully understand *why* until `v19` failed. `v21` operates under the strict, formalized constraint: **ABSOLUTELY NO UNVERIFIED STATIC PADDING**. 
2. **Intentionality**: `v16` was an exploratory success. `v21` is an *intentional foundation*. Every piece of code in `v21` has been vetted against the `failure_blacklist.md` to ensure it only emits replay-safe, verified candidates in the returned portfolio.
3. **The Launchpad for Phase 3**: `v21` strips away the complexity that bloated `v19`/`v20` (like the static diversity padding for CONFUSED_DEPUTY and DESTRUCTIVE_WRITE). It returns to a minimal notebook wrapper with proper Id,Score placeholders and strict rerun gating. This clean state is necessary for our AI Memory System to start iterating and injecting *verified* algorithmic improvements.

## Path Forward for Growth
From `v21` onwards, our growth will be governed by the following rules:
- Any new candidate generation (e.g., trying to trigger DESTRUCTIVE_WRITE) must be **live-validated** during the fill phase. 
- If a candidate pattern does not prove it fires during our 9,000s budget validation loop, it is dropped. 
- We will rely on our new AI Learning Memory (Phase 3) to discover novel, high-fire-rate templates rather than blindly padding the output.
