# Ponytail Audit 1 — over-engineering findings (ranked, current tree)

- `yagni:` `roll_random_encounter` computes a shiny pity rate (`SHINY_TRIGGER_RATE` + dry-day bonus) that never gates anything — `is_shiny` only decorates a callout string and the counter resets. Replace the whole ladder with `is_shiny = random.random() < 1/48`. [scripts/build_readme.py:530]
- `delete:` `battle_engine.simulate_team_battle` — 60-line "engine" whose gym_power is `sum(stats.values())` of single-key mock dicts and challenger_power is a flat 500; it's a coin-flip dressed up. process_challenge could roll scores directly in ~10 lines. [scripts/battle_engine.py:24]
- `shrink:` `select_signature_moves` — 113 lines where 40 do the work: the 75-move trim, three selection passes, and rank tuple all funnel into picking ≤4 moves; collapse passes 1–2 into the pass-3 loop with two guard clauses. [scripts/build_readme.py:257]
- `stdlib:` `analyze_team_weaknesses` hand-rolls nested counting loops over `battle_engine.TYPE_CHART`; `collections.Counter(w for ts in team_types.values() for t in ts for w in battle_engine.TYPE_CHART.get(t, []))` replaces them (Counter is already imported). [scripts/build_readme.py:418]
- `yagni:` `load_trainer_history` seeds a 9-field default profile (`rank`, `wins`, `pokedex_*`, …); only `shiny_hunt` is ever read or written. Default to `{"shiny_hunt": {"encounters_since_last": 0, "last_found": None}}`. [scripts/build_readme.py:218]
- `native:` PIL banner gradient drawn line-by-line via `draw.line`; PIL ships `Image.linear_gradient("L").resize((w,h))` + `ImageOps.colorize(img, black=c0, white=c1)` — two calls, no loop (banner already imports both). [scripts/banner_generator.py:39]
- `delete:` committed `__pycache__/*.pyc` build artifacts (6 files) despite `.gitignore` covering them — `git rm -r --cached scripts/__pycache__`. [scripts/__pycache__/]
- `yagni:` `fetch_move_metadata`'s `time.sleep(0.05)` throttle plus cache-miss fetches at runtime — move metadata for all ~9 Pokémon is static PokéAPI data; ship the needed entries in the existing `data/move_cache.json`, delete sleep + miss path. [scripts/build_readme.py:239]
- `shrink:` `calculate_evs` four-arm table compresses to computed values: `{'HP': 0 if is_fast else 252, 'Atk': 252 if is_physical else 0, ...}` — same output, one dict literal. [scripts/build_readme.py:430]
- `shrink:` `generate_branching_paths` — nested `render_tactic` closure + zip/sample scaffolding for static `<details>` text; inline f-string list comprehension over sampled pairs cuts ~15 lines. [scripts/build_readme.py:556]
- `shrink:` `create_flux_meter` — 6-line mode ladder + wrapper around `bar()`; inline as two `bar(...)` calls with suffix f-string, keep ladder as chained ternary. [scripts/build_readme.py:513]
- `yagni:` `select_competitive_item` mega/z-move branches return `{Name}ite`/`{Type}ium Z` strings that no template slot or paste consumer distinguishes from any other item; fold into the generic stat ladder. [scripts/build_readme.py:392]
- `shrink:` `get_github_stats` mock/fallthrough dicts duplicated; also `streak = min(total_contribs // 20, 365)` approximates nothing real — return zeros like the no-token mock. Merge to one zero-dict. [scripts/github_metrics.py:65]
- `delete:` `POKEMON_ASCII_ART` fallback sprite — every fallback path sets `sprite=None` yet the ASCII block renders as a fenced code blob in HTML README; replace with plain `???`. [scripts/build_readme.py:93]
- `shrink:` `bar()` clamps via `max(value,0)` then `min(ratio,1)` plus int-round dance; `int(round(...))` on a pre-clamped ratio is redundant — `'█'*f + '░'*(20-f)` with `f = round(ratio*length)` suffices. [scripts/build_readme.py:507]
- `delete:` `dependabot.yml` labels list — cosmetic config nobody reads; weekly interval + limit suffice. [.github/dependabot.yml:12]

net: -160 lines, -0 deps possible.
