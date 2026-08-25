# Ponytail Audit 9 — over-engineering findings (ranked, current tree)

- `yagni:` the real-data half of `get_github_stats` (GraphQL query string, headers, payload, urlopen/parse block, `_FALLBACK`) — `update-readme.yml` and `test-build.yml` never export `GITHUB_TOKEN` into the step env, so CI always hits the mock branch; the fetch path only ever runs if someone hand-exports a PAT locally. Replacement: delete the token branch and return the mock constants outright — or wire `${{ secrets.GITHUB_TOKEN }}` via `env:` if real stats are wanted. [scripts/github_metrics.py:10-58]
- `delete:` `PONYTAIL_AUDIT_7.md` and `PONYTAIL_AUDIT_8.md` — stacked one-shot reports shipped as repo content; audit 8 set the rule (keep only the newest, delete predecessors when the next lands). Replacement: this file supersedes both. [PONYTAIL_AUDIT_7.md, PONYTAIL_AUDIT_8.md]
- `shrink:` `weather_colors` in the banner generator is a second name-keyed weather table that must stay hand-synced with `WEATHER_TYPES` in build_readme (drift silently degrades to gray). Replacement: have `WEATHER_TYPES` carry the color pair and pass it straight into `generate_team_banner(pokemon_sprites, colors)`, deleting the dict and lookup. [scripts/banner_generator.py:28-36, scripts/build_readme.py:159-165]

Re-checked from audit 8, now clean: trainer_history dead fields gone (file is down to the two live keys); `META_LEADS`/`META_THREATS` merged into one tuple list; `calculate_evs` collapsed to a dict literal; `generate_paste` inlines its locals; sprite selection is one `or`-chain; `{LEAD_ASCII}` ghost removed from CONTRIBUTING. `__pycache__/` is untracked. `move_cache.json` stays — it is load-bearing (485 entries, no in-repo writer, deleting it would multiply PokéAPI calls).

net: -66 lines, -0 deps possible.
