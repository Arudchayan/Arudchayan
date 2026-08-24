# Ponytail Audit — over-engineering findings (ranked)

- `delete:` Duplicated type chart in `Coach.TYPE_CHART`; module already imports `TYPE_CHART` from battle_engine and uses it at coach.py:75. Delete lines 25-44, use the import. [scripts/coach.py]
- `delete:` Decorative workflow steps that only echo banners ("Show Sample Output", "Test Passed!", "Success!", "No Changes"). Nothing depends on their output. [`.github/workflows/test-build.yml`, `.github/workflows/update-readme.yml`]
- `yagni:` Dependabot `pip` ecosystem block grouping requests/aiohttp/colorama/rich/Pillow — no manifest exists (no requirements.txt/pyproject.toml); only Pillow is used and undeclared. Delete the pip watcher or add a requirements.txt with just Pillow. [.github/dependabot.yml]
- `delete:` Dead constants `COMPETITIVE_ITEMS` and `ROYAL` — referenced nowhere. [scripts/build_readme.py:17,78]
- `yagni:` `BattleEngine` class wrapping a single `@staticmethod` with zero state. Replace with a module-level `simulate_team_battle()` function; also drop its unused `json`/`os` imports. [scripts/battle_engine.py:26]
- `native:` Challenge result passed via deprecated `::set-output` with manual `%0A` encoding, then decoded in bash with `decodeURIComponent`. Write multiline log straight to `$GITHUB_OUTPUT`; delete the decode step. [scripts/process_challenge.py:79, `.github/workflows/challenge.yml`]
- `delete:` Unused env `GITHUB_TOKEN` injected into process_challenge step — script never reads it. [.github/workflows/challenge.yml]
- `shrink:` `fetch-depth: 0` full-history checkout just to regenerate README from APIs. Drop it (default depth suffices). [.github/workflows/update-readme.yml]
- `yagni:` `create_stat_bar` delegates 1:1 to `bar()`, and `analyze_team_weaknesses` builds an `'all'` key nobody reads. Call `bar()` directly; return only critical/moderate. [scripts/build_readme.py:595,508]
- `shrink:` Two parallel Pokémon-name normalizers (`svg_generator.normalize_name` vs `normalize_pokemon_identifier`). Keep one in build_readme and pass it down. [scripts/svg_generator.py:4]
- `delete:` Single-key dict `POKEMON_ASCII_ART{"default": ...}` used once — make it a plain string constant. [scripts/build_readme.py:102]

net: -90 lines, -0 deps possible.
