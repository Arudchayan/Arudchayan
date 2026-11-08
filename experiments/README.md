# Experiments

The reference pipeline is deliberately explicit:

```bash
python experiments/run_all.py
python experiments/fill_readme.py
```

`run_all.py` invokes the CLI in order:

1. `pokerl train` — collect search-labelled decisions, fit linear and MLP
   behaviour clones, run two DAgger rounds, and save policy artifacts.
2. `pokerl bench` — round-robin evaluation of the runnable agent zoo.
3. `pokerl eval --agent search-2` — the strong-search oracle match.
4. `pokerl generalize` — train-species vs held-out-species transfer.
5. `pokerl report` — regenerate the report, SVG figures, Pages data, and the
   README results block.
6. `pokerl dispatch` — write the deterministic daily lab dispatch.

The full transcript is written to `results/run.log`. `experiments/run_eval.py`
runs the evaluation-only phase (benchmark, oracle, generalisation, report,
dispatch) using the committed training artifacts. `fill_readme.py` copies the
headline numbers from the committed JSON into the README placeholders so the
front page cannot drift from the evidence.

For a quick sanity run:

```bash
python -m pokerl train --decisions 200 --epochs 3 --mlp-epochs 3 --dagger 0 --eval-games 8
python -m pokerl bench --games 8 --agents random heuristic search-1 --no-report
python -m pokerl report
```
