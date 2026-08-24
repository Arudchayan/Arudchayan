# Ponytail Audit — Arudchayan/Arudchayan

Ranked, biggest cut first. Scope: over-engineering only. Findings listed, nothing applied.

- delete: five overlapping docs files (IMPROVEMENTS/PROJECT_INFO/SETUP/QUICKSTART/.github/WORKFLOWS, ~1030 lines re-explaining one cron script). Fold a short "how it works" section into README. [IMPROVEMENTS.md, PROJECT_INFO.md, SETUP.md, QUICKSTART.md, .github/WORKFLOWS.md]
- delete: manual-update.yml duplicates update-readme.yml, which already has workflow_dispatch. Delete the file. [.github/workflows/manual-update.yml]
- yagni: 15 replacement keys computed but absent from template ({FASTEST_*}, {HEAVIEST_*}, {HIGHEST_BST*}, {API_CALLS}, {ACHIEVEMENT_DATE}, {GENERATION}, {TEAM_VISUAL}, {LEAD_ASCII}, {LEAD_EMOJI}, {ARCHETYPE_EMOJI}, {POKEDEX_COUNT}, {RANDOM_POKEMON}); the fastest/heaviest/bst tracking loops feed only these dead keys. Cut keys and trackers. [scripts/build_readme.py:885-906,1037-1059]
- stdlib: `requests` in two modules while the rest of the repo uses urllib (and requirements.txt installs nothing, so these imports silently fail in CI). Use urllib.request, drop the dep. [scripts/github_metrics.py:4, scripts/banner_generator.py:3]
- delete: TYPE_CHART copy-pasted 3x (battle_engine, coach, inline in analyze_team_weaknesses). One shared table in one module. [scripts/battle_engine.py:6-25, scripts/coach.py:23-42, scripts/build_readme.py:534-553]
- delete: compiled .pyc committed to git. Add .gitignore entry, `git rm -r --cached`. [scripts/__pycache__/]
- delete: try/except ImportError guards around four same-repo sibling modules that are always importable; they only mask real breakage (e.g. the requests failure above). Plain imports. [scripts/build_readme.py:14-32]
- delete: COMPETITIVE_ITEMS dict defined, never read. Nothing. [scripts/build_readme.py:97-101]
- yagni: WeatherSystem/BattleSimulator/QuestGenerator/PokePasteGenerator are classes of staticmethods with one call site each returning hardcoded/pure data. Plain functions or literals. [scripts/build_readme.py:224-290]
- shrink: create_stat_bar / create_power_gauge / create_flux_meter are the same bar renderer thrice. One `def bar(value, max, length, chars)` helper. [scripts/build_readme.py:651-677]
- shrink: requirements.txt is a 22-line comment wishlist advertising deps the code needs but never declares. Go stdlib-only and delete the file plus the `pip install` CI step. [requirements.txt]
- shrink: pick_index(n, seed) is `seed % n` with one caller; inline it. [scripts/build_readme.py:687-689]
- yagni: `role` param threaded into calculate_evs and select_competitive_item but never used in either body. Drop param. [scripts/build_readme.py:507,566]
- shrink: `from typing import List, Dict, Tuple` on Python 3.12; use builtins, drop import. Unused `math` import too. [scripts/build_readme.py:10-11]

net: -1250 lines, -1 dep possible.
