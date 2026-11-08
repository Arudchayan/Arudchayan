# Contributing to PokéLab

PokéLab is a research benchmark, so contributions are judged on **reproducibility
and evidence**, not only on features. A change that makes the engine more fun
but untestable is a hard sell.

## Good first contributions

- Add a test that pins a mechanic you rely on.
- Improve the failure log with a reproducible bug and seed.
- Add a held-out species experiment or a new baseline agent.
- Improve the dashboard, report, or documentation without adding runtime
  dependencies.
- Profile the engine and propose a measured optimization.

## Development setup

```bash
git clone https://github.com/Arudchayan/Arudchayan.git
cd Arudchayan
python -m pip install -e ".[dev]"
python -m pytest
python -m pokerl verify
```

Optional neural work:

```bash
python -m pip install -e ".[nn]"
```

## Pull request checklist

- [ ] Tests pass: `python -m pytest`
- [ ] Determinism holds: `python -m pokerl verify`
- [ ] Lint passes: `python -m ruff check .` and `python -m ruff format --check .`
- [ ] No runtime dependency added to `[project].dependencies`
- [ ] New mechanics are documented in `paper/main.md` and `FAILURES.md`
- [ ] Results, seeds, and sample sizes are reported if claims change
- [ ] Generated figures/README blocks were produced by `python -m pokerl report`

## Adding a species

1. Add a `Species` entry in `pokerl/dex.py` with accurate base stats and typing.
2. Add a fixed `PokemonSet` with a legal ability, item, nature, EVs, and four
   moves. `SETS` validates itself at import time.
3. If the species is part of the held-out split, keep it out of
   `TRAIN_SPECIES`; otherwise add it there.
4. Add a test if the species exercises a new mechanic.
5. Re-run the benchmark. Do not compare new ratings to old ones without noting
   the roster change.

## Adding a move or ability

- Implement the effect in `pokerl/engine.py`, not in an agent.
- Add a deterministic unit test with a fixed seed.
- Add the move to at least one set if it should appear in the benchmark.
- Document any approximation in `FAILURES.md`.

## Research claims

If you change a result, include:

- the exact command;
- the seed;
- the number of games;
- the confidence interval;
- the git SHA / config hash from the result metadata.

A claim without a rerunnable command is not a result.

## Style

- Python 3.11+, type hints on public functions.
- 120-column lines, Ruff formatting.
- Prefer standard library. Optional heavy dependencies belong behind extras.
- Keep engine mechanics deterministic; never use `random` for battle state.
- Keep the tone precise. Hype is not a substitute for evidence.

## Code of conduct

Be excellent to each other. Harassment, discrimination, and bad-faith review are
not welcome. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
