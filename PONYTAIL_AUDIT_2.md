# Ponytail Audit 2 — over-engineering findings (ranked, current tree)

- `shrink:` `META_TEAMS` — 4 dicts of 6-Pokémon rosters where only `name` and one random `pokemon` are ever read. Four `(name, lead)` tuples + `meta_name, meta_lead = random.choice(META_LEADS)`. [scripts/coach.py:24]
- `shrink:` "Check for Changes" step — `$GITHUB_OUTPUT` plumbing plus a conditional gate on the commit step. `git diff --quiet README.md assets/ data/ || { git add … && git commit … && git push; }` in one step. [.github/workflows/update-readme.yml:44]
- `delete:` `POKEMON_ASCII_ART` — 7-line art block rendered as a fenced code blob inside HTML when a sprite 404s; `'???'` matches every other missing-data slot. Delete the constant and the fallback branch in `get_pokemon_sprite_html`. [scripts/build_readme.py:92]
- `yagni:` dependabot `day`/`time`/`timezone`/`open-pull-requests-limit`/`labels` tuning — defaults cover it; keep `interval: weekly` alone. [.github/dependabot.yml:8]
- `shrink:` Three parallel collections for one team — `pokemon_data` dict, `team_list_data` list, `sprite_urls` list filled side-by-side in both branches of the fetch loop. Derive the latter two at their single use sites: `[pokemon_data[n] for n in chosen['team']]` and `[d.get('sprite') for d in …]`. [scripts/build_readme.py:619]
- `yagni:` `select_competitive_item` mega-stone/Z-crystal special cases — two early-return branches producing strings no consumer distinguishes from any other held item. Fold into the generic stat ladder. [scripts/build_readme.py:392]
- `shrink:` EV-string built three times — 5-line loop in `generate_paste`, listcomp for `{LEAD_EVS}`, `ev_parts`/`ev_text` in the dossier builder. One `ev_string(evs)` helper, three call sites. [scripts/build_readme.py:204]
- `shrink:` `create_flux_meter` 6-line `if/elif` mode ladder — one chained-ternary `mode =` line feeding the existing `bar(...)` suffix. [scripts/build_readme.py:512]
- `delete:` `"mock"` flag in `get_github_stats` — set in all three return paths, read by zero callers. Drop the key everywhere. [scripts/github_metrics.py:20]
- `shrink:` Shiny pity arithmetic (`base_rate` + dry-day `bonus`) — the rate only decorates one callout and the Hunt-status line. `trigger_rate = SHINY_TRIGGER_RATE`; the ladder earns nothing. [scripts/build_readme.py:530]
- `shrink:` `bar()` clamps `value`, then clamps the ratio, then round-clamps the product — `filled = int(min(max(value, 0) / max_value, 1) * length) if max_value > 0 else 0` does it once. [scripts/build_readme.py:506]

net: -68 lines, -0 deps possible.
