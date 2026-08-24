# Ponytail Audit 4 — over-engineering findings (ranked, current tree)

- `yagni:` Post-substitution `re.sub` rewriting the CURRENT_ARCHETYPE block + `import re` — the placeholders inside it were already filled by the replacements dict one statement earlier. Delete the regex (and `import re`); trim the Roster line in the template block instead. [scripts/build_readme.py:911]
- `yagni:` `load_trainer_history` seeds a 9-field default profile (`rank`, `wins`, `pokedex_seen`, …) — only `shiny_hunt` is ever read or written. Default to `{"shiny_hunt": {"encounters_since_last": 0, "last_found": None}}`. [scripts/build_readme.py:224]
- `shrink:` `get_github_stats(username, token)` — sole caller passes neither arg; plus a 5-line prose comment about streak options and a redundant `if response.status == 200` inside `urlopen` (it raises non-2xx). Hardcode username, read token inside, delete comment and check. [scripts/github_metrics.py:5]
- `stdlib:` `analyze_team_weaknesses` hand-rolls nested counting loops; `collections.Counter(w for ts in team_types.values() for t in ts for w in TYPE_CHART.get(t, []))` replaces them. [scripts/build_readme.py:437]
- `shrink:` Move-formatting loop duplicated verbatim for dossiers and lead moves (emoji · class · BP). Extract one `format_move(move)` helper used twice. [scripts/build_readme.py:755]
- `delete:` Static placeholder pipeline entries `{LEAD_ROLE}`, `{BONKERS_TAGLINE}`, `{SHINY_TRIGGER_PANEL}` — always constant strings. Put the literals in README.template.md, drop the three dict entries. [scripts/build_readme.py:885]
- `shrink:` Validate Output step's `[ ! -f README.md ]` check — subsumed by the existing `[ ! -s ]` (a missing file also fails `-s`). Delete it. [.github/workflows/test-build.yml:36]
- `native:` Vertical gradient drawn line-by-line via `draw.line` — PIL ships `Image.linear_gradient("L").resize((width, height))` + `ImageOps.colorize(img, black=c0, white=c1)`: two calls, no loop. [scripts/banner_generator.py:39]
- `delete:` `sys.path.append(os.getcwd())` hack + `scripts.` package prefix — running `python scripts/process_challenge.py` puts `scripts/` first on `sys.path`; plain `from battle_engine import simulate_team_battle` works, drop the `sys` import. [scripts/process_challenge.py:6]
- `shrink:` `calculate_evs` — the four `is_physical × is_fast` arms cover every input; the trailing two `defense > sp_defense` returns are unreachable. Delete them. [scripts/build_readme.py:462]
- `shrink:` Dead `len(final_moves) >= 4` guards in passes 1 and 2 of move selection — both loops append at most one move then `break`, so the cap can never trip. Drop the guards. [scripts/build_readme.py:354]
- `yagni:` `fetch_pokemon_data(..., original_name=None)` optional default — both call sites pass it, and every `original_name or data['name']` reduces to `original_name`. Make it a required positional, collapse the five fallbacks, drop the `Optional` import. [scripts/build_readme.py:465]
- `delete:` "Create assets directory" `mkdir -p assets` step — `assets/.gitkeep` is tracked so checkout recreates it, and the snk action creates output dirs anyway. Drop the step. [.github/workflows/snake.yml:13]
- `native:` Post-result comment via `actions/github-script@v9` — preinstalled `gh issue comment --body "$BATTLE_LOG"` with `GH_TOKEN: ${{ github.token }}` does the same, unpinned. [.github/workflows/challenge.yml:31]
- `delete:` `ImageFont` import — banner draws shapes and thumbnails only, no text. Trim the PIL import. [scripts/banner_generator.py:2]
- `delete:` `COMPETITIVE_ABILITIES['charizard']` — charizard appears in no archetype, wild roster, or legendary roster; unreachable key. Remove. [scripts/build_readme.py:72]

net: -64 lines, -0 deps possible.
