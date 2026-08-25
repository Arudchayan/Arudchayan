# Ponytail Audit 10

- `yagni:` `github_metrics.py` module — two functions, one caller each, returns hardcoded constants (`432/12/15/8`). Replacement: inline the bonus math into build_readme next to its only use site, delete the module. [scripts/github_metrics.py]
- `delete:` `PONYTAIL_AUDIT_9.md` — stacked one-shot reports ship as repo content; the keep-only-newest rule from audit 8 still applies. Replacement: this file supersedes it. [PONYTAIL_AUDIT_9.md]
- `delete:` Rayquaza/Dragon Ascent special case — pops Dragon Ascent from the sorted four and re-inserts a hand-built dict at slot 0. Replacement: nothing; the competitive sort key already ranks a 120BP physical Flying STAB near the top. [scripts/build_readme.py:255-260]
- `shrink:` the twelve-entry `{LEAD_HP}`…`{LEAD_SPEED_BAR}` replacement grid, hand-typed one key per stat. Replacement: one loop over `[('hp','HP'),('attack','ATK'),…]` emitting value + bar pairs. [scripts/build_readme.py:642-653]
- `shrink:` `process_challenge` winner if/elif chain plus a three-key `result_line` dict that recomputes the score twice. Replacement: chained conditional expressions for `winner` and `result_line`. [scripts/process_challenge.py:52-64]
- `shrink:` `' '.join(get_type_emoji(t) + t.upper() …)` copy-pasted at three call sites. Replacement: one `def types_line(types)` helper called three times. [scripts/build_readme.py:607,635,707]

Carry-over from audit 9, verified clean or still load-bearing: move_cache.json stays (no in-repo writer, deleting it multiplies PokéAPI calls); template placeholders all match replacements exactly (0 orphaned either direction); `__pycache__/` untracked and ignored; Pillow is the only third-party dep and has no stdlib substitute for PNG compositing.

net: -39 lines, -0 deps possible.
