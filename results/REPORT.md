# PokéLab, Experimental Report

**Generated:** 2026-11-08 15:41 UTC  
**Config hash:** `3c2112ced2e22897`  
**Git SHA:** `0b7e141c0e0edd74ddd7173bf522adea6a54ce6e`  
**Python:** `3.12.10`

## Key numbers

- Highest-rated agent: **Search-1** at **1153** Elo.
- MLP BC reaches **41.0%** win rate in round-robin play.
- Linear BC is a negative control: **3.8%** to **0.0%**; the MLP is the model that learns.
- Mean held-out transfer gap: **-2.7 pp**.
- Search-2 oracle: **90.0%** vs Heuristic at **31 decisions/s**.

## Leaderboard

| Agent | Elo | W-L-D | Win rate | 95% CI | Decisions/s |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Search-1** | 1153 | 429-158-13 | 73.1% | [69.3, 76.7] | 445 |
| **Heuristic** | 1104 | 392-204-4 | 65.8% | [61.9, 69.6] | 3827 |
| **Greedy** | 1073 | 363-230-7 | 61.2% | [57.3, 65.1] | 4078 |
| **MLP BC** | 943 | 242-348-10 | 41.0% | [37.1, 44.9] | 2519 |
| **MLP+DAgger** | 913 | 214-375-11 | 36.3% | [32.6, 40.2] | 2585 |
| **Random** | 813 | 134-459-7 | 22.6% | [19.4, 26.1] | 4171 |

Ratings are Bradley-Terry strengths mapped to an Elo-like scale (mean 1000, 400 points per decade of odds). CIs are 95% percentile bootstrap intervals over decisive side-swapped games. Draws are reported but excluded from the win-rate denominator.

**Oracle match.** 90-10-0 against Heuristic, win rate **90.0%** at **31 decisions/s**. This row is a separate 100-game match, not part of the six-agent round robin.

## Strength and compute

![Leaderboard](assets/leaderboard.svg)

![Pareto](assets/pareto.svg)

## Sample efficiency

| Stage | Budget | Win rate vs Heuristic |
| --- | ---: | ---: |
| BC, linear control | 500 decisions | 3.8% |
| BC, linear control | 1000 decisions | 6.2% |
| BC, linear control | 2000 decisions | 3.8% |
| BC, linear control | 3006 decisions | 0.0% |

![Learning curve](assets/learning_curve.svg)

## Generalisation to held-out species

| Agent | Train species | Held-out species | Delta |
| --- | ---: | ---: | ---: |
| **Heuristic** | 54.1% | 63.6% | +9.6 pp |
| **Search-1** | 64.6% | 78.0% | +13.4 pp |
| **MLP BC** | 37.4% | 14.3% | -23.1 pp |
| **Hybrid-1** | 66.0% | 66.0% | -0.0 pp |
| **MLP+DAgger** | 30.2% | 17.0% | -13.2 pp |

![Generalisation](assets/generalization.svg)

## Training summary

| Method | Budget | Eval win rate | Val loss |
| --- | ---: | ---: | ---: |
| Linear BC | 3006 | - | 1.4176 |
| MLP BC | 3006 | 37.5% | 0.9865 |
| MLP + DAgger | 3493 | 40.0% | - |

## Efficiency

| Agent | Elo | Mean decisions/s | Relative cost |
| --- | ---: | ---: | ---: |
| **Search-1** | 1153 | 445 | 9.4x |
| **Heuristic** | 1104 | 3827 | 1.1x |
| **Greedy** | 1073 | 4078 | 1.0x |
| **MLP BC** | 943 | 2519 | 1.7x |
| **MLP+DAgger** | 913 | 2585 | 1.6x |
| **Random** | 813 | 4171 | 1.0x |

## Reproducibility

```bash
python -m pokerl bench --games 120 --seed 2025
python -m pokerl train --decisions 3000 --epochs 15 --mlp-epochs 50 --dagger 1
python -m pokerl generalize --games 100 --seed 2025
python -m pokerl report
```

The engine uses a SplitMix64 stream and never imports `random` for battle mechanics. Team schedules are shared across all agent pairs. The full benchmark is deterministic given `--seed`.

## Limitations

- Fixed level-100 sets; no teambuilding.
- No weather, terrain, Mega/Z/Dynamax, multi-hit moves, or accuracy/evasion stages.
- Opponent model is the heuristic policy, not a human or a stronger search agent.
- Full observability; hidden information is not modelled.
- Small roster (24 species) and a single 3v3 format.
- The MLP is trained with optional PyTorch; inference uses NumPy when available.

## Non-claims

This is a controlled benchmark, not a claim about competitive Pokémon strength, human play, or frontier-agent safety. It is a testbed for reproducible decision-making research.
