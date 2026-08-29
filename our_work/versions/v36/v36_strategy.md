# OMEGA scenario v6 Strategy & Architecture (v36) -- trigger 90

## Score Trajectory

| Version | Notebook | Score | Key Change |
|---------|----------|-------|------------|
| v33 | `omega_v3_attack.ipynb` | **86.490** | 91.305 arch direct port |
| v34 | `omega_v4_attack.ipynb` | **88.560** | 5 precision levers |
| v35 | `omega_v5_attack.ipynb` | **89.640** | Double-counting bugfix |
| **v36** | **`omega_v6_attack.ipynb`** | **Target: 90+** | **4 final precision levers** |

## Complete Parameter Evolution (v3 -> v6)

| Parameter | v3 (86.49) | v4 (88.56) | v5 (89.64) | v6 (90+) |
|-----------|------------|------------|------------|----------|
| REPLAY_SAFE_FRAC | 0.98 | 0.99 | 0.99 | **0.992** |
| SPLIT_CLASSIFY_N | 7 | 5 | 3 | **1** |
| SLOWEST0 | 25 | 25 | 25 | **12** |
| SLOWEST_MULT | 1.35 | 1.28 | 1.20 | **1.15** |
| Warm-up hops | 8 | 1 | 1 | 1 |
| Warm-up harvest | No | Yes (bug) | Yes (fixed) | Yes (fixed) |

## Files

- `omega_v6_attack.py` -- 285 lines
- `build_v36.py` -- Notebook builder with 16-point validation
- `omega_v6_attack.ipynb` -- Ready for Kaggle (GPU T4 x2, Internet Off)
