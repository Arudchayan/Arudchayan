# Ponytail Audit 8 — over-engineering findings (ranked, current tree)

- `delete:` `PONYTAIL_AUDIT_1.md` through `PONYTAIL_AUDIT_7.md` — seven stacked one-shot reports (92 lines) shipped as repo content; each audit just accrues another file nobody re-reads. Replacement: keep only the newest report, delete predecessors when the next lands. [PONYTAIL_AUDIT_1.md … PONYTAIL_AUDIT_7.md]
- `delete:` 11 dead fields in `data/trainer_history.json` (`trainer_name`, `rank`, `total_battles`, `wins`, `losses`, `badges_earned`, `pokedex_seen`, `pokedex_caught`, `start_date`, `last_active`, plus `shiny_hunt.start_date`) — no code reads any of them; `load_trainer_history` round-trips the file solely for `shiny_hunt.encounters_since_last`/`last_found`. Keep only those two. [data/trainer_history.json]
- `shrink:` `META_LEADS` and `META_THREATS` are two parallel structures keyed by the same four Pokémon, synced by hand; merge into one list of `(label, threat, speed, types)` tuples and drop the dict lookup (re-flag from audit 7, still present). [scripts/coach.py:24-37]
- `shrink:` `calculate_evs` four-arm return ladder collapses to one dict literal — `'HP': 0 if is_fast else 252, 'Atk': 252 if is_physical else 0, 'Def': 4 if is_physical else 0, 'SpA': 0 if is_physical else 252, 'SpD': 0 if is_physical else 4, 'Spe': 252 if is_fast else 0` (open since audit 1). [scripts/build_readme.py:319-329]
- `shrink:` `generate_paste` unpacks four single-use locals (`name`, `item`, `ability`, `nature`) then interpolates each once; inline `p['name']`, `p['item']`, `p['best_ability']`, `p['nature']` straight into the f-string (re-flag from audit 7, still present). [scripts/build_readme.py:181-187]
- `shrink:` sprite-selection if/elif chain repeats each nested-`.get` path twice (test + assign); one `or`-chained expression assigns the first hit (re-flag from audit 7, still present). [scripts/build_readme.py:344-350]
- `delete:` `{LEAD_ASCII}` bullet in the template-placeholders list — names a placeholder that exists in neither `README.template.md` nor the `replacements` dict; points contributors at a ghost. Replacement: delete the line. [CONTRIBUTING.md:43]

Re-checked from audit 7, now clean: `stats_mega-gengar.svg` deleted. Dropped from audit 7: the `github_metrics.py` mock-vs-`_FALLBACK` duplicate — the branches now intentionally return different values, so merging would cost clarity for 2 lines.

net: -123 lines, -0 deps possible.
