# Ponytail Audit 2 — over-engineering findings (ranked)

- `delete:` Committed `__pycache__/` .pyc files for 5 modules — build artifacts in git. Delete the directory; `.gitignore` already covers it. [scripts/__pycache__/]
- `delete:` `TYPE_CHART['resist']`/`'immune'` lists (≈40 of 91 lines) — only `'weak'` is ever read (coach.py:54, build_readme.py:494). Store just the weak lists. [scripts/battle_engine.py]
- `delete:` `simulate_battle()` returns a fully hardcoded battle log — the "simulation" is one static string; nothing varies. Inline the constant or cut the feature. [scripts/build_readme.py:200]
- `yagni:` `svg_generator.generate_radar_chart(stats, name, normalize_name)` takes a function parameter to call a 3-line name-mangler that has exactly one caller shape. Pass the string back and normalize at the caller. [scripts/svg_generator.py:4]
- `yagni:` Unused payload fields fetched and threaded through every Pokémon dict (`shiny_sprite`, `id`, `role`) but never rendered anywhere. Cut from dict + fallback. [scripts/build_readme.py:566,724,839,945]
- `yagni:` Unused imports `urllib.error`, `datetime` (github_metrics.py), `Optional` re-exported... actually used once; cut the first two plus `labels` var in svg_generator. [scripts/github_metrics.py:3, scripts/build_readme.py:8, scripts/svg_generator.py:6]
- `shrink:` `bar`/`create_power_gauge`/`create_flux_meter`/`ratio_pct` — four helpers where two suffice; gauge/meter are bar + suffix. Fold into `bar(value, max, length, char, suffix)`. [scripts/build_readme.py:579-600]
- `shrink:` `select_signature_moves` builds 6-tuples then sorts on `item[:4]` and unpacks with `_, _, _, move_name, ...`; a small dataclass or plain dicts would drop ~15 lines of index juggling. [scripts/build_readme.py:342-360]

net: -120 lines, -0 deps possible.
