# Ponytail Audit 4 — over-engineering findings (ranked, current tree)

- `shrink:` `select_signature_moves` still carries ceremony after the audit-3 trim: a `take()` closure + parallel `final_names` set, three sequential selection loops that all walk the same sorted list, and candidates storing full dicts just to pop a sort key. One loop over sorted candidates with `if len(final) < 4 and raw not in taken` picks the same four. [scripts/build_readme.py:223]
- `yagni:` six decoration replacements for three mechanics — `{MEGA_VISUAL}`+`{MEGA_STONE_EMOJI}`, `{ZMOVE_VISUAL}`+`{ZMOVE_EMOJI}`, `{TERA_VISUAL}`+`{TERA_EMOJI}` all derive from the same three `chosen.get()` checks. Fold each pair into its `{*_INFO}` string ("◆ Metagrossite 💎" / "—") and delete six dict entries. [scripts/build_readme.py:705]
- `shrink:` no-token mock dict and `_FALLBACK` are same-shape literals built twice; derive the mock from `_FALLBACK` (`{**_FALLBACK, "total_contributions": 432, ...}`) so one shape owns the schema. [scripts/github_metrics.py:14]
- `shrink:` SVG path built twice — `generate_radar_chart` returns a filename the only caller ignores, then the caller re-derives the identical `assets/stats_{identifier}.svg` string at dossier time. Drop the `return` and keep one canonical construction. [scripts/svg_generator.py:34] [scripts/build_readme.py:398]
- `yagni:` dead `archetype_data` parameter on `fetch_pokemon_data` — never referenced in the body; one caller even passes `{}`. Remove it from signature and both call sites. [scripts/build_readme.py:365]
- `delete:` unreachable trailing `return _FALLBACK` — every path through the try/except above already returns; the statement after cannot execute. [scripts/github_metrics.py:66]
- `shrink:` `calculate_genetic_bonuses` computes `min(100, stats["total_contributions"] // 5)` twice for level and desc; bind `level = min(...)` once and reuse. [scripts/github_metrics.py:73]
- `shrink:` `{SHINY_HUNT_STATUS}` hardcodes the literal `1/48` while `SHINY_TRIGGER_RATE` exists eight hundred lines up; use the named constant so the odds can't drift apart. [scripts/build_readme.py:723]

net: -32 lines, -0 deps possible.
