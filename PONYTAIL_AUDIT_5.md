# Ponytail Audit 5 — over-engineering findings (ranked)

- `shrink:` `get_version_priority` is a 5-line one-caller wrapper around `VERSION_PRIORITY.index` with a ValueError catch. Inline the lookup in the sort-key lambda: `(VERSION_PRIORITY.index(n) if n in VERSION_PRIORITY else len(VERSION_PRIORITY))` and delete the function. [scripts/build_readme.py:211]
- `yagni:` `eligible()` is a named def used exactly once to drop `dragon-ascent`; replace `final_moves = list(filter(eligible, final_moves))[:3]` with `[m for m in final_moves if m["raw_name"] != 'dragon-ascent'][:3]` and delete the def. [scripts/build_readme.py:264]
- `shrink:` `import coach` and `from coach import TYPE_CHART` both appear; drop the from-import and call `coach.TYPE_CHART` at the one weakness-analysis site. [scripts/build_readme.py:15]
- `shrink:` challengers loader guards `os.path.exists(challenger_path)` for a file that ships in-repo; open it directly like every other data file (`archetypes.json` has no such guard) and drop the branch. [scripts/build_readme.py:568]
- `delete:` `assets/.gitkeep` — the directory holds seven tracked files (snake.svg, team_banner.png, six stats SVGs), so the keep-file is vestigial. Remove it. [assets/.gitkeep]

net: -10 lines, -0 deps possible.
