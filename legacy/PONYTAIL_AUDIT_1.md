# Ponytail Audit 1

- `delete:` `assets/snake.svg` — orphaned artifact of `.github/workflows/snake.yml`, itself cut in round 4 (commit 27899dd); no workflow regenerates it and no README/template/script references the file. Replacement: nothing. Proof: `grep -rin "snake" .github/workflows/ README.md README.template.md scripts/` → zero matches; `grep -rn "assets/snake" .` → zero matches (docs only mention the workflow name, not the asset). [assets/snake.svg]
- `delete:` `assets/stats_metagross.svg` — stale generated radar chart. The live README references `stats_metagross-mega.svg`, not the base variant, and `fetch_pokemon_data()` → `svg_generator.generate_radar_chart()` rewrites whatever radar it needs on every build, so no committed copy is load-bearing. Replacement: nothing; regenerated on demand. Proof: `grep -o 'assets/stats[^"]*\.svg' README.md | sort -u` → decidueye, gengar, metagross-mega, noivern, rayquaza, zeraora — base `stats_metagross.svg` absent. [assets/stats_metagross.svg]
- `delete:` `PONYTAIL_AUDIT_10.md` — stacked one-shot audit report; the keep-only-newest rule from earlier rounds applies and this file supersedes it. Replacement: this report. Proof: `git ls-files | grep AUDIT` → tracked at HEAD, already deleted in the working tree (`git status`: ` D PONYTAIL_AUDIT_10.md`). [PONYTAIL_AUDIT_10.md]
- `delete:` the five `"colors": [(r,g,b),(r,g,b)]` entries in `WEATHER_TYPES` — leftover palette data for the Pillow banner generator deleted in round 10; only `name`/`emoji`/`effect` are ever read. Replacement: nothing. Proof: `grep -rn '"colors"' scripts/` → only the five definition lines (build_readme.py:158-162); `grep -rn "\['colors'\]\|\[\"colors\"\]" scripts/` → zero reads. [scripts/build_readme.py:158-162]
- `delete:` stale bytecode `scripts/__pycache__/battle_engine.cpython-311.pyc` and `github_metrics.cpython-311.pyc` — both source modules were cut in earlier rounds; Python never imports orphaned `__pycache__` entries without their `.py`. Untracked/gitignored, so local hygiene rather than repo content. Proof: `ls scripts/*.py` → no `battle_engine.py`, no `github_metrics.py`; `git check-ignore -v scripts/__pycache__/github_metrics.cpython-311.pyc` → matched by `.gitignore:1`. [scripts/__pycache__/]

Verified clean (checks ran, nothing provable):
- Zero-caller functions: AST scan of all 24 function defs across the 4 scripts against all sources → every def referenced ≥2 times; `process_challenge()` invoked by `.github/workflows/challenge.yml:24`.
- Unused module constants: none — every top-level assignment in all four scripts is read at least once.
- Template parity: script-generated diff of `{PLACEHOLDER}` sets in `README.template.md` vs `replacements` keys in `build_readme.py` → empty in both directions.
- Dead dependencies: none possible — no `package.json`, no `requirements.txt`; `dependabot.yml` watches github-actions only and the sole action (`actions/checkout@v7`) is used.
- Data files: `move_cache.json` stays — consumed by `load_move_cache()`, no in-repo writer by design; deleting it multiplies PokéAPI calls (carried over from audit 10, re-verified).
- Protected per rules, untouched: README/SETUP/CONTRIBUTING/QUICKSTART/PROJECT_INFO/IMPROVEMENTS/.github/WORKFLOWS markdown, LICENSE, all workflow yml, .env/config files.

net: -14 lines, -0 deps possible.
