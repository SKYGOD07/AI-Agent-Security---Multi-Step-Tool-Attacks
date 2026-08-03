# Notebook Algorithm Catalog: Stockfish Series & Benchmarks

| Notebook Name | Base Script | Public Score | Key Innovation / Features | Failure Mode (if any) |
|---|---|---|---|---|
| `stockfish_v11_attack.ipynb` | Track 1 & 2 Relay | 47.200 | Initial probe-and-emit two-track architecture | Under-filling due to blind estimation |
| `stockfish_v12_attack.ipynb` | Live Validation Fill | 60.125 | Live deadline-aware validation-fill | Conservative cushion |
| `stockfish_v13_attack.ipynb` | Hops Tuning | 63.850 | `PROBE_HOPS` tuning and tighter margin | Limited by flat margin for gemma |
| `stockfish_v14_attack.ipynb` | Adaptive Margin | 72.270 | `_adaptive_margin()` scaling with slowest latency | Single-post bottleneck |
| `stockfish_v15_attack.ipynb` | Latency Routing | 79.410 | Basic latency-based template selection | Harmony token missing |
| `stockfish_v16_attack.ipynb` | Harmony Injection | 87.660 | Forged Harmony assistant CoT bypass | Restricted to 1 post/candidate |
| `stockfish_v17_attack.ipynb` | Hop Bursting | Format Error | `BURST_K = 4` on all models | Overran replay window |
| `stockfish_v18_attack.ipynb` | Multi-post Race | 57.285 | Race 5 multi-post templates | 4x replay cost penalty |
| `stockfish_v19_attack.ipynb` | Static Diversity | Format Error | Unverified candidate padding | Unverified candidate replay void |
| `stockfish_v20_attack.ipynb` | Signature Archive | 2.250 | Fast signature dedup & decaying diversity | Over-compacted returned set |
| `stockfish_v21_attack.ipynb` | PowerShell Sync | Format Error | Inline string substitution in `.ipynb` | Mangled notebook JSON |
| `stockfish_v22_attack.ipynb` | Dense Multi-post | Format Error | `BURST_K = 4` & `SLOW_MULTIPOST_N = 4` | Replay budget overrun |
| `stockfish_v23_attack.ipynb` | Hops-1 Probing | 53.190 | `PROBE_HOPS = 1` with 2x cost scaling | Miscalibrated stop condition |
| `stockfish_v24_attack.ipynb` | 5-Template Race | 84.645 | Live probe race across 5 candidate templates | Search budget waste (25 probes) |
| `stockfish_v25_attack.ipynb` | Dual-URL Templates | Format Error | 2 URLs per template message | 2x replay cost overrun |
| `stockfish_v26_attack.ipynb` | Dual-URL Recalibrated | 57.210 | Dual-URL + 1.15 cost coefficient | Low fire rate on dual URLs |
| `stockfish_v27_attack.ipynb` | Aggressive Margins | Format Error | Direct SDK imports & margin squeezing | Import crash & replay overrun |
| `stockfish_v28_attack.ipynb` | v69 Scaffolding | 85.590 | v69 arch + jedforce-1 defensive wrapper | Restricted to 1 post/candidate |
| `stockfish_v29_attack.ipynb` | 90+ Multi-post | **90+ Target** | Asymmetric routing: `BURST_K=2`, `SLOW_MULTIPOST_N=4` | None (Defensive Base64) |

## Benchmark Reference Notebooks
- `ai-agent-security-v69.ipynb`: **88.200** (Single URL, Harmony token forging, live validation-fill)
- `jedforce-1.ipynb`: **87.900** (Base64 encoding, defensive imports, `REPLAY_SAFE = 0.99`)
- `ai-agent-security-90.ipynb`: **90.090** (Asymmetric dual-track multi-post: gpt_oss=4 posts, gemma=2 posts)
