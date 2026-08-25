# Ponytail Audit 7 — over-engineering findings (ranked)

- `native:` banner pipeline — downloads 6 sprites, composites a gradient PNG with Pillow (the repo's only third-party dep), commits a binary daily. GitHub renders `<img>` rows natively; put a sprite-row snippet in `README.template.md`, delete the module and `assets/team_banner.png`. [scripts/banner_generator.py]
- `delete:` PONYTAIL_AUDIT_1.md–6.md and 8.md — seven stale one-shot reports (92 lines), referenced by nothing; every audit just accrues another file nobody re-reads. Replacement: nothing; applied findings live in git history. [PONYTAIL_AUDIT_1.md … PONYTAIL_AUDIT_6.md, PONYTAIL_AUDIT_8.md]
- `delete:` 11 dead fields in `data/trainer_history.json` (`trainer_name`, `rank`, `total_battles`, `wins`, `losses`, `badges_earned`, `pokedex_seen`, `pokedex_caught`, `start_date`, `last_active`, plus `shiny_hunt.start_date`) — no code reads any of them; `load_trainer_history` round-trips the file solely for `encounters_since_last`/`last_found`. Keep only those two. [data/trainer_history.json]
- `shrink:` `META_LEADS` and `META_THREATS` are two parallel tables over the same four Pokémon, synced by hand; merge into one list of `(label, threat, speed, types)` tuples and drop the dict lookup. [scripts/coach.py:24-37]
- `shrink:` `generate_paste` unpacks four single-use locals (`name`, `item`, `ability`, `nature`) then interpolates each once; inline `p['name']`, `p['item']`, `p['best_ability']`, `p['nature']` straight into the f-string. [scripts/build_readme.py:178-190]
- `shrink:` sprite-selection if/elif chain repeats every nested-`.get` path twice (test + assign); one `or`-chained expression assigns the first hit. [scripts/build_readme.py:344-350]
- `shrink:` `calculate_evs` four-arm return ladder collapses to one computed literal — `{'HP': 0 if is_fast else 252, 'Atk': 252 if is_physical else 0, 'Def': 4 if is_physical else 0, 'SpA': 0 if is_physical else 252, 'SpD': 0 if is_physical else 4, 'Spe': 252 if is_fast else 0}`. [scripts/build_readme.py:319-329]
- `delete:` `{LEAD_ASCII}` bullet in the template-placeholders list — names a placeholder that exists in neither `README.template.md` nor the `replacements` dict; points contributors at a ghost. Replacement: delete the line. [CONTRIBUTING.md]

net: -198 lines, -1 dep possible.
