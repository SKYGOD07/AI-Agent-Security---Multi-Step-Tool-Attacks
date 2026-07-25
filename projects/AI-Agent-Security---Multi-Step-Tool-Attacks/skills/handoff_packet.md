# Handoff Packet: The baseline v16 strategy
v19 and v20 failed because they introduced static/unverified diversity padding on top of the proven v16 replay-throughput baseline. This padding increased candidate count without verified fire rates, diluted the replay budget, and caused Replay Timeout / Submission Format Errors. 

**Moving forward to v21 and beyond:**
We must stick to the v16 working baseline behavior. This means:
1. Minimal notebook wrapper.
2. Correct Id,Score placeholder on commit.
3. Rerun gating.
4. Only replay-safe, verified candidates in the returned portfolio.
5. **ABSOLUTELY NO UNVERIFIED STATIC PADDING.**
