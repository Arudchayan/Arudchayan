# Ponytail Audit 3 — over-engineering findings (ranked)

- `delete:` `simulate_battle()` — a fake battle "simulation" returning one fully hardcoded 8-line log, identical every run. Replace call site with the constant string (or drop the drill section). [scripts/build_readme.py:199]
- `yagni:` `forced_moves` pipeline (set-builder, BAD_MOVES bypass, dedicated sort-key slot, pre-selection pass) serving exactly one hardcoded case: Rayquaza gets Dragon Ascent. Replace with a one-liner after selection that prepends `dragon-ascent` when `'rayquaza' in pokemon_name.lower()`. [scripts/build_readme.py:305]
- `shrink:` Best-version/method key computed twice per move — once inside `min(...)`, again verbatim in the appended tuple. Factor a `rank(detail)` helper and feed it to both; kills the copy-paste drift risk. [scripts/build_readme.py:329]
- `shrink:` Coach keeps two partial parallel lookup tables (`meta_speeds` 16 entries, `threat_types` 6) keyed by the same Pokémon. Merge into one per-mon table `{lead: (speed, [types])}`; unknowns keep their defaults. [scripts/coach.py:31]
- `delete:` `if __name__ == "__main__"` block with hardcoded sprite URLs in the banner module — dev scratch shipped in the repo; nothing invokes it in CI. Delete; run ad hoc if ever needed. [scripts/banner_generator.py:85]
- `shrink:` Background-hexagon loop recomputes the same six trig points the radar loop already computes, at full radius. Derive both point strings from one shared comprehension over `(radius_multiplier,)`. [scripts/svg_generator.py:19]
- `yagni:` Commit-message flourish greps/seds README to extract the archetype into the commit body. Hardcode "Daily profile update"; delete the extraction pipeline. [.github/workflows/update-readme.yml:63]
- `delete:` Static placeholders `{LEAD_ROLE}`, `{BONKERS_TAGLINE}`, `{SHINY_TRIGGER_PANEL}` — always filled with constant strings. Put the literals in the template, drop the three replacement entries. [scripts/build_readme.py:929,950]
- `shrink:` `test-build.yml` runs four sequential `if ! grep` checks; one `grep -q -e X -e Y README.md` (plus the empty-file `-s` test) asserts the same in a third of the lines. [.github/workflows/test-build.yml:36]
- `delete:` `Hail` and `Fog` gradient palettes — unreachable; weather only ever comes from `WEATHER_TYPES`, which lists neither. Delete both entries. [scripts/banner_generator.py:34]
- `delete:` `sys.path.append(os.getcwd())` hack plus `scripts.` package prefix — running `python scripts/process_challenge.py` already puts `scripts/` first on `sys.path`; import `battle_engine` plainly and drop `sys`. [scripts/process_challenge.py:6]
- `shrink:` `describe_target()` — 4-line helper with exactly one caller mapping two bools to strings. Inline the ternary chain at the call site. [scripts/build_readme.py:621]

net: -69 lines, -0 deps possible.
