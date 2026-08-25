# Ponytail Audit 6 — over-engineering findings (ranked, current tree)

- `delete:` `snake.yml` generates `assets/snake.svg` on a daily cron, but no file in the repo references it — not README.md, not the template, nothing. A scheduled job burning runner minutes to produce an orphan asset via the third-party `Platane/snk` action. Delete workflow + svg; reinstate only if the svg gains a consumer. [.github/workflows/snake.yml]
- `native:` all three workflows declare `actions/setup-python@v7` steps, but every script is stdlib-only plus PIL — and ubuntu-latest runners ship python3 and Pillow preinstalled. Drop the setup steps (and the 3.11-vs-3.12 version ping-pong between workflows) and call python3 directly. [.github/workflows/update-readme.yml:22, .github/workflows/test-build.yml:20, .github/workflows/challenge.yml:17]
- `shrink:` update-readme.yml builds an 8-line heredoc commit body ("✨ Archetype… ⚡ Gotta Code 'Em All!") for a bot commit nobody reads. One `-m "🎮 Daily Pokémon Profile Update [skip ci]"` does the job. [.github/workflows/update-readme.yml:38]
- `delete:` `scripts/assets/team_banner.png` — a stale copy of the generated banner committed under scripts/; the real artifact is written to `assets/team_banner.png` each run and nothing reads the scripts/ copy. [scripts/assets/team_banner.png]
- `shrink:` `get_github_stats` no-token path does `{**_FALLBACK, "total_contributions": 432, …}` — the spread overrides all four `_FALLBACK` keys immediately; return the four-key dict literal and let `_FALLBACK` serve only the exception path. [scripts/github_metrics.py:17]
- `shrink:` build_readme.py imports coach twice (`import coach` + `from coach import TYPE_CHART`); keep `import coach` and say `coach.TYPE_CHART` in `analyze_team_weaknesses`. [scripts/build_readme.py:13-15]
- `shrink:` `load_trainer_history` seeds the `shiny_hunt` default dict, then line 542 repeats the identical literal in a `.get` fallback — have the loader guarantee the key and the caller reads `trainer_history["shiny_hunt"]` plainly. [scripts/build_readme.py:201,542]

Re-checked from audit 5, now clean: `__pycache__` untracked, `{SHINY_HUNT_STATUS}` uses `SHINY_TRIGGER_RATE`, `create_flux_meter` gone. False alarm in audit 5: dragonite/gyarados/lucario `COMPETITIVE_ABILITIES` entries ARE reachable via `WILD_ROSTER` random encounters — do not cut.

net: -46 lines, -1 dep possible.
