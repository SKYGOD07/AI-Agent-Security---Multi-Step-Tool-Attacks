# Next Model Handoff Packet

Welcome to the AI Agent Security repo. Before you write a single line of code, read this.

## 1. Current Best Strategy
The current gold standard is **v20 (Compact Replay-Portfolio Engine)**. 
The algorithm does NOT rely on heavy search machinery. Instead, it relies on a linear, highly optimized Replay-Throughput loop:
1. Probe 5 distinct templates, 5 reps each.
2. Select the fastest, highest-firing template via `median_latency / fire_rate`.
3. Seed the portfolio with fired probes.
4. Fill the remaining slots using the single winning template.
5. Probe a "Controlled Live Diversity Layer" (Confused Deputy, Destructive Write) and decay immediately if they fail to fire.
6. Stop generating candidates the moment cumulative measured replay latency hits **8910s**.
7. Deduplicate the portfolio semantically by `(tool_seq | predicate_family | prompt_hash)`.

## 2. Top 3 Things to Preserve
1. **The 5-Cell Notebook Scaffold**: `%%writefile /kaggle/working/attack.py`, `IS_RERUN` gating, and the exact `Id,Score` CSV fallback schema.
2. **Replay-Safe Sizing Cap**: Tracking cumulative latency and stopping at `0.99 * 9000s`. **Do not guess latency.**
3. **Live Verification Rule**: Only add candidates to the portfolio if they successfully triggered a tool execution during the live `env.interact()` search phase.

## 3. Top 3 Things to Avoid (See `failure_blacklist.md`)
1. **Notebook Execution**: Never execute `attack.py`, `importlib`, or `SandboxEnv` directly in the notebook cell.
2. **Unverified Padding**: Never pad the candidate list with static, unverified templates. They hallucinate during replay and trigger timeouts.
3. **Bandits / Heavy Controllers**: Do not add multi-armed bandits, adaptive routing, or deep search state. They collapse throughput.

## 4. Next Experiment to Run
- Wait for the Kaggle evaluation results for `v20`.
- If `v20` succeeds, analyze which predicate families fired the most.
- If `v20` timeouts, lower the `REPLAY_SAFE` margin from `0.99` to `0.95`.
- If `v20` score is low, investigate if the Controlled Live Diversity Layer decayed too quickly.

## 5. Required Reading Map
Before modifying any files, read:
1. `our_work/memory/core_memory.md` (Competition mechanics)
2. `our_work/memory/strategy_library.md` (Verified tactics)
3. `our_work/memory/failure_blacklist.md` (Blacklisted bad ideas)
4. `our_work/v20/attack_v20.py` (The current active baseline codebase)
