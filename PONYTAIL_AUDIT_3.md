# Ponytail Audit 3 — over-engineering findings (ranked, current tree)

- `shrink:` `select_signature_moves` — 114 lines of rank-tuples, a `[:75]` trim, and three sequential selection passes to pick ≤4 moves. One scoring loop over cached metadata with two guards (STAB/class match, status-priority) picks the four directly. [scripts/build_readme.py:226]
- `yagni:` mega-stone/Z-crystal early returns in `select_competitive_item` — two branches fabricating held-item strings (`Metagrossite`, `Ghostium Z`) no consumer distinguishes from any other item; re-flagged, still present from audit 2. Fold into the generic stat ladder. [scripts/build_readme.py:363]
- `shrink:` `get_github_stats` — no-token mock dict and post-exception zero dict are two 6-line literals of the same shape; one module-level `_FALLBACK` constant returned from both paths. [scripts/github_metrics.py:14]
- `delete:` `<!-- CURRENT_ARCHETYPE_START/END -->` markers in the template — audit 4 removed the `re.sub` that consumed them; nothing reads them, they just leak into rendered READMEs. Strip both lines. [README.template.md:42]
- `yagni:` `fetch_move_metadata` — a one-line `MOVE_CACHE.get(move_url, {})` wrapper with a single caller. Inline it. [scripts/build_readme.py:223]
- `delete:` `{n: pokemon_data[n] for n in chosen['team']}` rebuild — the dict was already populated iterating `chosen['team']` in the same order; the comprehension is a no-op. Delete the statement. [scripts/build_readme.py:593]
- `delete:` `<!-- TEAM_BANNER_PLACEHOLDER -->` — a static `<img>` tag above it needs no replacement marker; dead comment shipped in every build. [README.template.md:5]
- `yagni:` dead defensive defaults — `META_THREATS.get(meta_lead, (90, ["normal"]))` (all four META_LEADS are keyed) and `chosen.get('id', idx)` (every archetype has an `id`). Use direct indexing. [scripts/coach.py:55] [scripts/build_readme.py:564]

net: -90 lines, -0 deps possible.
