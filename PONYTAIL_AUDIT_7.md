# Ponytail Audit 7 — over-engineering findings (ranked, current tree)

- `delete:` 13 unreachable `META_THREATS` entries (Dragapult, Kingambit, Great Tusk, Iron Valiant, Gholdengo, Flutter Mane, Walking Wake, Roaring Moon, Dragonite, Volcarona, Blissey, Dondozo, Clodsire) — `random.choice(META_LEADS)` can only ask up Landorus-Therian, Torkoal, Alomomola, Ribombee, and only the first/third/fourth are keyed. Keep the three used entries (or add a Torkoal tuple) and index directly instead of `.get(..., (90, ["normal"]))`. [scripts/coach.py:32]
- `yagni:` `original_name` parameter on `fetch_pokemon_data` — both call sites pass the same value as `pokemon_name`; collapse to one argument. [scripts/build_readme.py:337,503,557]
- `shrink:` `get_version_priority` — 5-line one-caller wrapper around `VERSION_PRIORITY.index` with ValueError catch; inline `(VERSION_PRIORITY.index(n) if n in VERSION_PRIORITY else len(VERSION_PRIORITY))` in the sort-key lambda (audit-5 re-flag, still present). [scripts/build_readme.py:208]
- `shrink:` `eligible()` named def used once to drop `dragon-ascent`; `[m for m in final_moves if m["raw_name"] != 'dragon-ascent'][:3]` (audit-5 re-flag, still present). [scripts/build_readme.py:261]
- `delete:` `{HYPERSTREAM_BLOCK}` + `{ANALYTICS_BLURB}` — restate "N types / Avg speed" verbatim from the Unique Typings + Average Speed rows and the Synergy/Speed flux bars; nothing new. Delete builder entries and both template slots. [scripts/build_readme.py:721] [README.template.md:23,103]
- `shrink:` candidate move dicts carry dead `method`/`level` keys — both feed the sort key from locals before storage and no consumer (`format_move`, paste) reads them afterward; stop storing them. [scripts/build_readme.py:247,248]
- `yagni:` `generate_team_banner` returns the output path its only caller discards; drop the `return`. [scripts/banner_generator.py:77]
- `delete:` `assets/.gitkeep` — directory holds eight tracked files; audit-5 re-flag, still present. [assets/.gitkeep]

net: -32 lines, -0 deps possible.
