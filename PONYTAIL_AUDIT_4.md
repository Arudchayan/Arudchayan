# Ponytail Audit 4 — over-engineering findings (ranked)

- `shrink:` Validate Output step — four sequential `if ! … ; exit 1` blocks (existence, emptiness, 2 greps). One `test -s README.md` plus `grep -q -e "POKÉMON TRAINER PROFILE" -e "TEAM CONFIGURATION" README.md`; grep failure already exits nonzero. [.github/workflows/test-build.yml:34]
- `yagni:` `re.sub` rewrite of the `CURRENT_ARCHETYPE` block + `import re` — duplicates placeholders the template system already fills one statement earlier. Put `{ARCHETYPE_TITLE}`/`{LEAD_POKEMON}` literals in the template block, drop the Roster line there, delete the regex. [scripts/build_readme.py:920]
- `delete:` `if __name__ == "__main__"` dev scratch with hardcoded sprite URLs — nothing in CI invokes it. Delete; run ad hoc if ever needed. [scripts/banner_generator.py:85]
- `shrink:` Background-hexagon loop recomputes six trig points the radar loop already computes, just at full radius. Compute the six angles once, derive both point strings from one helper over `(r,)`. [scripts/svg_generator.py:29]
- `shrink:` Coach keeps two partial parallel lookups keyed by the same Pokémon (`meta_speeds` 16 entries, `threat_types` 6). Merge into one `{name: (speed, [types])}` table; defaults cover the rest. [scripts/coach.py:31]
- `yagni:` `Coach` class wrapping a single zero-state `@staticmethod` with one caller. Module-level `get_coach_advice()` function and module-level `META_TEAMS`, same as BattleEngine got in audit 1. [scripts/coach.py:5]
- `shrink:` `describe_target()` — 3-line helper mapping two bools to strings for exactly one caller. Inline the ternary chain at the call site. [scripts/build_readme.py:574]
- `shrink:` `create_power_gauge` — thin `bar()` wrapper with a percent suffix, one caller (its `max_value=1530` default is never used). Inline as a `bar(...)` call with the suffix arg. [scripts/build_readme.py:536]
- `delete:` `sys.path.append(os.getcwd())` hack + `scripts.` package prefix — running `python scripts/process_challenge.py` puts `scripts/` first on `sys.path`, so plain `from battle_engine import simulate_team_battle` works; drop `sys` import. [scripts/process_challenge.py:6]
- `yagni:` `fetch_pokemon_data(..., original_name=None)` — both call sites pass `original_name` equal to the positional name, so every `original_name or data['name']` reduces to the parameter itself. Delete the parameter. [scripts/build_readme.py:465]
- `yagni:` `get_github_stats(username="Arudchayan", token=None)` — sole caller passes neither arg. Hardcode the username, read the token inside; delete both parameters. [scripts/github_metrics.py:5]
- `delete:` `Hail` and `Fog` gradient palettes — unreachable; weather only ever comes from `WEATHER_TYPES`, which lists neither. [scripts/banner_generator.py:34]
- `delete:` Commit-message flourish greps/seds README to extract the archetype into the body. Hardcode the message; delete the extraction pipeline. [.github/workflows/update-readme.yml:63]
- `stdlib:` exists+makedirs dance — `os.makedirs(output_dir, exist_ok=True)`, one line, matching svg_generator.py:45. [scripts/banner_generator.py:77]
- `shrink:` Dead `len(final_moves) >= 4` guards in passes 1 and 2 of move selection — both loops append at most one move then `break`, so the cap can never trip. Drop the guards. [scripts/build_readme.py:379]
- `delete:` Unused `ImageFont` import — banner drawing uses shapes and thumbnails only. Remove it from the PIL import. [scripts/banner_generator.py:2]

net: -70 lines, -0 deps possible.
