# Ponytail Audit 1 — over-engineering findings (ranked, current tree)

- `delete:` `battle_engine.simulate_team_battle` — a 91-line "engine" whose gym_power sums single-key mock dicts and challenger_power is a flat 500; it's a coin flip dressed in armor. Roll scores directly in `process_challenge` (~10 lines); move `TYPE_CHART` to its only real consumers (`coach.py`, weakness analysis). [scripts/battle_engine.py:24]
- `yagni:` `roll_random_encounter` computes a shiny pity rate (`SHINY_TRIGGER_RATE` + dry-day bonus) that never gates anything — `is_shiny` only decorates one callout string. Replace the ladder with `is_shiny = random.random() < 1/48`. [scripts/build_readme.py:530]
- `shrink:` `select_signature_moves` — 113 lines where ~40 do the work: the 75-move trim, rank tuple, and three selection passes all funnel into picking ≤4 moves; collapse passes 1–2 into the pass-3 loop with two guard clauses. [scripts/build_readme.py:257]
- `yagni:` `fetch_move_metadata`'s runtime cache-miss fetches plus `time.sleep(0.05)` throttle — metadata for ~9 fixed Pokémon never changes; ship needed entries in the existing `data/move_cache.json`, drop the miss path. [scripts/build_readme.py:239]
- `shrink:` `get_github_stats` mock dict duplicated verbatim across no-token and exception paths, plus a `"mock"` flag nobody reads; merge into one zero-dict without the flag. [scripts/github_metrics.py:14]
- `yagni:` `select_competitive_item` mega/z-move branches return `{Name}ite`/`{Type}ium Z` strings no consumer distinguishes from any other item; fold into the generic stat ladder. [scripts/build_readme.py:392]
- `shrink:` `generate_branching_paths` — nested `render_tactic` closure plus zip/sample scaffolding for static `<details>` text; an f-string comprehension over sampled pairs cuts ~15 lines. [scripts/build_readme.py:556]
- `shrink:` "Check for Changes" step in update-readme.yml — `git diff --quiet README.md assets/ data/ || git commit …` in the commit step covers it without `$GITHUB_OUTPUT` plumbing and a conditional gate. [.github/workflows/update-readme.yml:45]
- `shrink:` EV-string formatting duplicated (5-line loop in `generate_paste`, list-comp in dossier builder); one shared expression serves both. [scripts/build_readme.py:205]
- `shrink:` `calculate_evs` four-arm table compresses to computed values: `{'HP': 0 if fast else 252, 'Atk': 252 if phys else 0, ...}` — same output, one literal. [scripts/build_readme.py:430]
- `shrink:` `create_flux_meter` — 6-line mode ladder wrapped around `bar()`; two `bar()` calls with an inline ternary suffix suffice. [scripts/build_readme.py:513]
- `delete:` `POKEMON_ASCII_ART` fallback sprite — renders as a fenced ASCII blob inside an HTML README when sprite is None; plain `???` does the same job. [scripts/build_readme.py:93]
- `delete:` dependabot timezone/open-PR-limit/labels tuning — weekly interval alone is fine; defaults cover the rest. [.github/dependabot.yml:11]
- `shrink:` `bar()` clamps value, then ratio, then int-rounds the pre-clamped product; one clamp plus `'█'*f + '░'*(l-f)` suffices. [scripts/build_readme.py:507]

net: -130 lines, -0 deps possible.
