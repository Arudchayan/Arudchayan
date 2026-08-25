# Ponytail Audit 1 — over-engineering findings (ranked, current tree)

- `yagni:` `roll_random_encounter` computes a shiny pity rate (`SHINY_TRIGGER_RATE` + dry-day bonus) that never gates anything — `is_shiny` only decorates a callout string and the counter resets. Replace the whole ladder with `is_shiny = random.random() < 1/48`. [scripts/build_readme.py:530]
- `delete:` `battle_engine.simulate_team_battle` — 60-line "engine" whose gym_power is `sum(stats.values())` of single-key mock dicts and challenger_power is a flat 500; it's a coin-flip dressed up. process_challenge could roll scores directly in ~10 lines. [scripts/battle_engine.py:24]
- `shrink:` `select_signature_moves` — 113 lines where ~40 do the work: the 75-move trim, three selection passes, and rank tuple all funnel into picking ≤4 moves; collapse passes 1–2 into the pass-3 loop with two guard clauses. [scripts/build_readme.py:257]
- `stdlib:` `analyze_team_weaknesses` hand-rolls nested counting loops over `battle_engine.TYPE_CHART`; one `Counter` comprehension replaces them (Counter already imported). [scripts/build_readme.py:418]
- `yagni:` `load_trainer_history` seeds a 9-field default profile (`rank`, `wins`, `pokedex_*`, …); only `shiny_hunt` is ever read or written. Default to `{"shiny_hunt": {"encounters_since_last": 0, "last_found": None}}`. [scripts/build_readme.py:218]
- `native:` PIL banner gradient drawn line-by-line via `draw.line`; PIL ships `Image.linear_gradient("L").resize((w,h))` + `ImageOps.colorize(img, black=c0, white=c1)` — two calls, no loop. [scripts/banner_generator.py:39]
- `delete:` committed `__pycache__/*.pyc` build artifacts (6 files) despite `.gitignore` covering them — `git rm -r --cached scripts/__pycache__`. [scripts/__pycache__/]
- `yagni:` `fetch_move_metadata`'s runtime cache-miss fetches plus `time.sleep(0.05)` throttle — move metadata for ~9 fixed Pokémon is static; ship the needed entries in the existing `data/move_cache.json` and drop the miss path. [scripts/build_readme.py:239]
- `shrink:` EV-string formatting duplicated (5-line loop in `generate_paste`, list-comp in dossier builder); extract one helper or reuse the list comp both places. [scripts/build_readme.py:205]
- `shrink:` `calculate_evs` four-arm table compresses to computed values: `{'HP': 0 if fast else 252, 'Atk': 252 if phys else 0, ...}` — same output, one dict literal. [scripts/build_readme.py:430]
- `shrink:` `generate_branching_paths` — nested `render_tactic` closure + zip/sample scaffolding for static `<details>` text; inline f-string comprehension over sampled pairs cuts ~15 lines. [scripts/build_readme.py:556]
- `shrink:` `create_flux_meter` — 6-line mode ladder + wrapper around `bar()`; two `bar()` calls with an inline ternary suffix suffice. [scripts/build_readme.py:513]
- `yagni:` `select_competitive_item` mega/z-move branches return `{Name}ite`/`{Type}ium Z` strings no consumer distinguishes from any other item; fold into the generic stat ladder. [scripts/build_readme.py:392]
- `shrink:` `get_github_stats` mock/fallthrough dicts duplicated verbatim; merge to one zero-dict returned by both paths. [scripts/github_metrics.py:65]
- `delete:` `POKEMON_ASCII_ART` fallback sprite — renders as a fenced ASCII blob inside HTML README when sprite is None; plain `???` text does the same job. [scripts/build_readme.py:93]
- `shrink:` "Check for Changes" step in update-readme.yml — `git diff --quiet && git commit || echo none` in the commit step covers it without `$GITHUB_OUTPUT` plumbing and a conditional gate. [.github/workflows/update-readme.yml:45]
- `shrink:` `bar()` clamps value then ratio then int-rounds a pre-clamped product; `'█'*round(ratio*l) + '░'*(l-round(...))` after one clamp suffices. [scripts/build_readme.py:507]
- `delete:` dependabot labels/timezone/open-PR-limit tuning — defaults or one-line equivalents cover it. [.github/dependabot.yml:11]
- `delete:` `ImageFont` import — banner draws shapes only, never text. Trim from PIL import. [scripts/banner_generator.py:2]

net: -155 lines, -0 deps possible.
