# Ponytail Audit 3 — over-engineering findings (ranked)

- `yagni:` `forced_moves` machinery (set-builder, BAD_MOVES bypass clause, dedicated sort-key slot, dedicated pre-selection pass) serving exactly one hardcoded case — Rayquaza gets Dragon Ascent. Post-selection one-liner: prepend `dragon-ascent` when `'rayquaza' in pokemon_name.lower()`. [scripts/build_readme.py:305]
- `delete:` `simulate_battle()` — a "simulation" returning one fully hardcoded log; nothing varies run to run. Assign the constant string at its single call site. [scripts/build_readme.py:199]
- `shrink:` Coach keeps two partial parallel lookups keyed by the same Pokémon (`meta_speeds` 16 entries, `threat_types` 6). Merge into one `{name: (speed, [types])}` table; defaults cover the rest. [scripts/coach.py:31]
- `yagni:` `MEGA_NAME_OVERRIDES` (4 entries + lookup branch) — maps Mega Charizard X/Y and Mega Mewtwo X/Y, none of which appear in any archetype roster; every actual Mega (`metagross/gengar/rayquaza-mega`) resolves correctly through the generic `startswith("mega ")` branch. Delete dict and the override check in `normalize_pokemon_identifier`. [scripts/build_readme.py:174]
- `delete:` `if __name__ == "__main__"` dev scratch with hardcoded sprite URLs — nothing in CI invokes it. Delete; run ad hoc if ever needed. [scripts/banner_generator.py:85]
- `shrink:` Best-version/method rank tuple computed twice per move — verbatim inside `min(...)`'s key, again in the appended tuple. Factor a `rank(detail)` helper used by both; kills copy-paste drift. [scripts/build_readme.py:329]
- `shrink:` Background-hexagon loop recomputes six trig points the radar loop already computes, just at full radius. Derive both point strings from one comprehension over `(r_multiplier,)`. [scripts/svg_generator.py:29]
- `shrink:` Twin helpers `get_daily_weather(seed)` / `get_daily_quest(seed)` — both are `random.seed(seed); random.choice(TBL)`. Seed once and call `random.choice` at the two call sites. [scripts/build_readme.py:195]
- `shrink:` Four sequential `if ! grep -q` blocks in Validate Output step — one `grep -q -e X -e Y README.md` plus the existing `-s` empty-check asserts the same in a third of the lines. [.github/workflows/test-build.yml:36]
- `yagni:` `Coach` class wrapping a single zero-state `@staticmethod` with one caller. Module-level `get_coach_advice()` function, same as BattleEngine got in audit 1. [scripts/coach.py:5]
- `shrink:` `describe_target()` — 4-line helper mapping two bools to strings for exactly one caller. Inline the ternary chain. [scripts/build_readme.py:621]
- `shrink:` `create_power_gauge` — thin `bar()` wrapper with a suffix, one caller. Inline as a `bar(...)` call with the suffix arg. [scripts/build_readme.py:575]
- `delete:` Static placeholders `{LEAD_ROLE}`, `{BONKERS_TAGLINE}`, `{SHINY_TRIGGER_PANEL}` — always filled with constant strings. Put the literals in the template, drop the three replacement entries. [scripts/build_readme.py:927]
- `yagni:` Commit-message flourish greps/seds README to extract the archetype into the commit body. Hardcode the message; delete the extraction pipeline. [.github/workflows/update-readme.yml:63]
- `delete:` Leftover scaffolding comments ("# ... (Previous helper functions ...) ...", "# ... (Same as updated previously) ...", "# ... (Include other helper functions ...) ..."). Nothing follows them. [scripts/build_readme.py:245]
- `delete:` `sys.path.append(os.getcwd())` hack + `scripts.` package prefix — running `python scripts/process_challenge.py` puts `scripts/` first on `sys.path`; plain `from battle_engine import ...` works, drop `sys` import. [scripts/process_challenge.py:6]
- `delete:` `Hail` and `Fog` gradient palettes — unreachable; weather only ever comes from `WEATHER_TYPES`, which lists neither. [scripts/banner_generator.py:34]
- `stdlib:` exists+makedirs dance — `os.makedirs(output_dir, exist_ok=True)`, one line, matching svg_generator.py:45. [scripts/banner_generator.py:77]

net: -85 lines, -0 deps possible.
