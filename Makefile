.PHONY: install test lint typecheck bench demo report verify generalize clean

PYTHON ?= python

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

typecheck:
	$(PYTHON) -m mypy pokerl

bench:
	$(PYTHON) -m pokerl bench

demo:
	$(PYTHON) -m pokerl demo --seed 1

report:
	$(PYTHON) -m pokerl report

verify:
	$(PYTHON) -m pokerl verify

generalize:
	$(PYTHON) -m pokerl generalize

clean:
	$(PYTHON) -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in list(Path('.').rglob('__pycache__'))]"
	$(PYTHON) -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in [*Path('.').glob('*.egg-info'), *Path('.').glob('build'), *Path('.').glob('dist'), *Path('.').glob('htmlcov'), *Path('.').glob('.pytest_cache'), *Path('.').glob('.ruff_cache'), *Path('.').glob('.mypy_cache')]]"
	$(PYTHON) -c "from pathlib import Path; [p.unlink(missing_ok=True) for p in Path('.').rglob('*.py[co]')]; Path('.coverage').unlink(missing_ok=True)"
