# Ponytail Audit 7 — over-engineering findings (ranked, current tree)

- `delete:` 10 dead fields in `data/trainer_history.json` (`trainer_name`, `rank`, `total_battles`, `wins`, `losses`, `badges_earned`, `pokedex_seen`, `pokedex_caught`, `start_date`, `last_active`) — no code reads them; `build_readme.py` loads the file solely for `shiny_hunt` and round-trips the rest untouched. Keep only the shiny_hunt state. [data/trainer_history.json]
- `shrink:` `META_LEADS` and `META_THREATS` are two parallel tables keyed by the same four Pokémon, synced by hand; merge into one list of `(label, threat, (speed, types))` triples and drop the dict lookup. [scripts/coach.py:24-37]
- `shrink:` `generate_paste` unpacks four single-use locals (`name`, `item`, `ability`, `nature`) then interpolates them once; inline `p['name']`, `p['item']`, `p['best_ability']`, `p['nature']` straight into the f-string. [scripts/build_readme.py:178-187]
- `delete:` `assets/stats_mega-gengar.svg` — stale artifact; README links only `stats_{decidueye,gengar,metagross,noivern,rayquaza,zeraora}.svg` and no current build writes a `mega-gengar` file (archetypes say "Mega Gengar"). [assets/stats_mega-gengar.svg]
- `shrink:` sprite-selection if/elif chain repeats each full nested-`.get` path twice (test + assign); one `or`-chained expression assigns the first hit. [scripts/build_readme.py:340-347]
- `shrink:` `calculate_evs` four-arm return ladder collapses to one computed literal — `'HP': 0 if is_fast else 252, 'Atk': 252 if is_physical else 0, 'Def': 4 if is_physical else 0, 'SpA': 0 if is_physical else 252, 'SpD': 0 if is_physical else 4, 'Spe': 252 if is_fast else 0` (audit-1 re-flag, still present). [scripts/build_readme.py:316-326]
- `shrink:` no-token mock dict in `get_github_stats` duplicates the `_FALLBACK` shape verbatim two paths apart; hoist one module-level mock and return it from both branches (audit-6 re-flag, still present). [scripts/github_metrics.py:5,17]

Re-checked from audit 6, now clean: snake.yml, setup-python steps, heredoc commit body, scripts/assets/team_banner.png, dual coach import, shiny default duplication, banner `return`.

net: -42 lines, -0 deps possible.
