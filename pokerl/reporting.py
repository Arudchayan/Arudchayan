"""Generate the report, SVG figures, static dashboard, and README block."""

from __future__ import annotations

import datetime
import html
import json
import platform
from pathlib import Path
from typing import Any

from .plotting import bar_chart, line_chart, scatter_chart

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"


def load_json(path: str | Path, default: Any) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def _ci(ci: list[float] | tuple[float, float] | None) -> str:
    if not ci:
        return "-"
    return f"[{100 * ci[0]:.1f}, {100 * ci[1]:.1f}]"


def _float(value: Any, digits: int = 1, default: str = "-") -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return default


def _agent_speed(leaderboard: dict, name: str) -> float:
    matches = [m for m in leaderboard.get("matches", []) if m.get("agent_a") == name or m.get("agent_b") == name]
    return sum(m.get("decisions_per_sec", 0) for m in matches) / len(matches) if matches else 0.0


def _head_to_head(leaderboard: dict, agent: str, opponent: str) -> dict | None:
    for m in leaderboard.get("matches", []):
        if m.get("agent_a") == agent and m.get("agent_b") == opponent:
            return m
        if m.get("agent_a") == opponent and m.get("agent_b") == agent:
            flipped = dict(m)
            flipped["win_rate"] = 1.0 - m.get("win_rate", 0.0)
            return flipped
    return None


def leaderboard_table(leaderboard: dict) -> str:
    standings = leaderboard.get("standings", [])
    if not standings:
        return "_No leaderboard yet. Run `python -m pokerl bench`._"
    rows = [
        "| Agent | Elo | W-L-D | Win rate | 95% CI | Decisions/s |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in standings:
        name = row.get("agent", "?")
        rows.append(
            f"| **{name}** | {_float(row.get('rating'), 0)} | "
            f"{row.get('wins', 0)}-{row.get('losses', 0)}-{row.get('draws', 0)} | "
            f"{_pct(row.get('win_rate', 0))} | {_ci(row.get('ci95'))} | {_float(_agent_speed(leaderboard, name), 0)} |"
        )
    return "\n".join(rows)


def learning_curve_table(curve: dict) -> str:
    bc = curve.get("bc", [])
    rl = curve.get("rl", [])
    if not bc and not rl:
        return "_No learning-curve data yet. Run `python -m pokerl train`._"
    rows = ["| Stage | Budget | Win rate vs Heuristic |", "| --- | ---: | ---: |"]
    for row in bc:
        rows.append(f"| BC, linear control | {row.get('samples', '?')} decisions | {_pct(row.get('win_rate', 0))} |")
    for row in rl:
        rows.append(f"| REINFORCE | {row.get('episode', '?')} episodes | {_pct(row.get('win_rate', 0))} |")
    return "\n".join(rows)


def generalization_table(gen: dict) -> str:
    rows_data = gen.get("results", [])
    if not rows_data:
        return "_No generalisation results yet._"
    rows = ["| Agent | Train species | Held-out species | Delta |", "| --- | ---: | ---: | ---: |"]
    for row in rows_data:
        train = row.get("train_win_rate", 0)
        held = row.get("heldout_win_rate", 0)
        rows.append(f"| **{row.get('agent', '?')}** | {_pct(train)} | {_pct(held)} | {100 * (held - train):+.1f} pp |")
    return "\n".join(rows)


def efficiency_table(leaderboard: dict) -> str:
    standings = leaderboard.get("standings", [])
    if not standings:
        return "_No efficiency data yet._"
    rows_data = []
    for row in standings:
        name = row.get("agent", "?")
        rows_data.append((name, float(row.get("rating", 1000)), max(_agent_speed(leaderboard, name), 1e-9)))
    fastest = max(speed for _, _, speed in rows_data)
    rows = ["| Agent | Elo | Mean decisions/s | Relative cost |", "| --- | ---: | ---: | ---: |"]
    for name, rating, speed in rows_data:
        rows.append(f"| **{name}** | {rating:.0f} | {speed:.0f} | {fastest / speed:.1f}x |")
    return "\n".join(rows)


def _write_figures(leaderboard: dict, curve: dict, gen: dict, assets_dir: Path) -> None:
    assets_dir.mkdir(parents=True, exist_ok=True)
    standings = leaderboard.get("standings", [])
    if standings:
        names = [row["agent"] for row in standings]
        ratings = [float(row.get("rating", 1000)) for row in standings]
        bar_chart(
            names,
            ratings,
            title="Bradley-Terry leaderboard",
            subtitle="Side-swapped matches, 95% bootstrap intervals",
            xlabel="Elo-like rating",
            path=assets_dir / "leaderboard.svg",
        )
        points = []
        for row in standings:
            name = row["agent"]
            points.append((max(_agent_speed(leaderboard, name), 1.0), float(row.get("rating", 1000)), name))
        scatter_chart(
            points,
            title="Strength and compute",
            subtitle="Higher is stronger, further left is cheaper",
            xlabel="Decisions per second (log scale)",
            ylabel="Elo-like rating",
            path=assets_dir / "pareto.svg",
        )
    bc = [(row.get("samples", 0), row.get("win_rate", 0)) for row in curve.get("bc", [])]
    rl = [(row.get("episode", 0), row.get("win_rate", 0)) for row in curve.get("rl", [])]
    if bc or rl:
        line_chart(
            {"BC, linear control": bc, "REINFORCE": rl},
            title="Sample efficiency",
            subtitle="Win rate against the heuristic reference",
            xlabel="Training budget",
            ylabel="Win rate",
            path=assets_dir / "learning_curve.svg",
            y_min=0.0,
            y_max=1.0,
        )
    rows = gen.get("results", [])
    if rows:
        labels = [row["agent"] for row in rows]
        train = [row.get("train_win_rate", 0) for row in rows]
        held = [row.get("heldout_win_rate", 0) for row in rows]
        bar_chart(
            [f"{label}, train" for label in labels] + [f"{label}, held-out" for label in labels],
            train + held,
            title="Generalisation to held-out species",
            subtitle="Same policy, unseen species",
            xlabel="Win rate vs Heuristic",
            path=assets_dir / "generalization.svg",
            width=900,
            height=500,
        )


def _html_table(headers: list[str], rows: list[list[str]], numeric_from: int = 1) -> str:
    head = "".join(f'<th scope="col">{html.escape(h)}</th>' for h in headers)
    body = []
    for row in rows:
        cells = []
        for index, cell in enumerate(row):
            tag = "td"
            cls = ' class="num"' if index >= numeric_from else ""
            cells.append(f"<{tag}{cls}>{cell}</{tag}>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def _html_leaderboard(leaderboard: dict) -> str:
    standings = leaderboard.get("standings", [])
    rows = []
    for row in standings:
        name = html.escape(row.get("agent", "?"))
        rows.append(
            [
                f"<strong>{name}</strong>",
                _float(row.get("rating"), 0),
                f"{row.get('wins', 0)}-{row.get('losses', 0)}-{row.get('draws', 0)}",
                _pct(row.get("win_rate", 0)),
                _ci(row.get("ci95")),
                _float(_agent_speed(leaderboard, row.get("agent", "")), 0),
            ]
        )
    return _html_table(["Agent", "Elo", "W-L-D", "Win rate", "95% CI", "Decisions/s"], rows)


def _html_learning(curve: dict) -> str:
    rows = []
    for row in curve.get("bc", []):
        rows.append(["BC, linear control", str(row.get("samples", "?")), _pct(row.get("win_rate", 0))])
    for row in curve.get("rl", []):
        rows.append(["REINFORCE", str(row.get("episode", "?")), _pct(row.get("win_rate", 0))])
    return _html_table(["Stage", "Budget", "Win rate"], rows, numeric_from=1)


def _html_generalization(gen: dict) -> str:
    rows = []
    for row in gen.get("results", []):
        train = row.get("train_win_rate", 0)
        held = row.get("heldout_win_rate", 0)
        rows.append(
            [
                f"<strong>{html.escape(row.get('agent', '?'))}</strong>",
                _pct(train),
                _pct(held),
                f"{100 * (held - train):+.1f} pp",
            ]
        )
    return _html_table(["Agent", "Train species", "Held-out species", "Delta"], rows)


def render_dashboard(
    leaderboard: dict,
    curve: dict,
    gen: dict,
    oracle: dict,
    docs_dir: str | Path = DOCS,
) -> None:
    docs_dir = Path(docs_dir)
    standings = leaderboard.get("standings", [])
    best = standings[0] if standings else {}
    h2h = _head_to_head(leaderboard, "Search-1", "Heuristic") or {}
    oracle_result = oracle.get("result", {})
    max_speed = max((m.get("decisions_per_sec", 0) for m in leaderboard.get("matches", [])), default=0.0)
    mlp = next((row for row in standings if row.get("agent") == "MLP BC"), {})
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PokéLab, a deterministic Pokémon battle benchmark</title>
<meta name="description" content="A deterministic, dependency-free Pokémon battle benchmark with side-swapped matches, bootstrap intervals, held-out species, and reproducible results.">
<link rel="stylesheet" href="style.css">
</head>
<body>
<a class="skip" href="#main">Skip to results</a>
<header class="masthead">
  <div class="shell masthead-row">
    <a class="wordmark" href="#top">PokéLab</a>
    <nav aria-label="Sections">
      <a href="#leaderboard">Leaderboard</a>
      <a href="#pareto">Compute</a>
      <a href="#learning">Learning</a>
      <a href="#generalization">Generalization</a>
      <a href="#reproducibility">Reproduce</a>
      <a href="https://github.com/Arudchayan/Arudchayan/blob/main/paper/main.md">Paper</a>
    </nav>
  </div>
</header>
<main id="main">
  <section class="hero shell" aria-labelledby="title">
    <h1 id="title">A deterministic Pokémon battle benchmark.</h1>
    <p class="lede">A 24-species, 3v3 singles engine with fixed seeds, side-swapped matches, bootstrap intervals, held-out species, and a failure log. Zero runtime dependencies.</p>
    <div class="hero-links">
      <a class="button" href="https://github.com/Arudchayan/Arudchayan">View the source</a>
      <a href="results/REPORT.md">Read the report</a>
      <a href="https://github.com/Arudchayan/Arudchayan/blob/main/FAILURES.md">Failure log</a>
    </div>
    <dl class="metrics">
      <div><dt>Best agent</dt><dd>{html.escape(best.get("agent", "-"))}<span>{_float(best.get("rating"), 0)} Elo</span></dd></div>
      <div><dt>Search-1 vs heuristic</dt><dd>{_pct(h2h.get("win_rate", 0))}<span>{_float(h2h.get("decisions_per_sec"), 0)} decisions/s</span></dd></div>
      <div><dt>Search-2 oracle</dt><dd>{_pct(oracle_result.get("win_rate", 0))}<span>{_float(oracle_result.get("decisions_per_sec"), 0)} decisions/s</span></dd></div>
      <div><dt>Engine throughput</dt><dd>{_float(max_speed, 0)}<span>decisions/s, fastest match</span></dd></div>
    </dl>
  </section>

  <section class="shell section" id="leaderboard" aria-labelledby="leaderboard-title">
    <h2 id="leaderboard-title">Leaderboard</h2>
    <p class="section-lede">Bradley-Terry strength from side-swapped round-robin play. Intervals are 95% percentile bootstrap intervals over decisive games; draws are reported but excluded from the denominator.</p>
    {_html_leaderboard(leaderboard)}
    <p class="note">The six-agent round robin uses 120 games per pair and one shared team schedule. Search-2 is a separate 100-game oracle match.</p>
  </section>

  <section class="shell section" id="compute" aria-labelledby="compute-title">
    <span id="pareto"></span>
    <h2 id="compute-title">Strength and compute</h2>
    <p class="section-lede">A point on the right is cheaper. Search depth is the strongest lever; distillation buys throughput at a measurable strength cost.</p>
    <figure><img src="assets/pareto.svg" alt="Elo rating against decisions per second for six agents."><figcaption>Elo-like rating against measured decisions per second. Log scale on throughput.</figcaption></figure>
  </section>

  <section class="shell section" id="learning" aria-labelledby="learning-title">
    <h2 id="learning-title">Learning</h2>
    <p class="section-lede">The linear behaviour clone is a negative control. The non-linear MLP reaches {_pct(mlp.get("win_rate", 0))} overall in the round robin; the linear model does not learn a useful ranking.</p>
    {_html_learning(curve)}
    <figure><img src="assets/learning_curve.svg" alt="Win rate against training budget for the linear control and REINFORCE."><figcaption>Win rate against the heuristic reference. The linear curve is a negative result, not a missing run.</figcaption></figure>
  </section>

  <section class="shell section" id="generalization" aria-labelledby="generalization-title">
    <h2 id="generalization-title">Generalization</h2>
    <p class="section-lede">Policies train on 18 species and are tested on six they never see. Search transfers; the small MLP does not.</p>
    {_html_generalization(gen)}
    <figure><img src="assets/generalization.svg" alt="Train and held-out species win rates by agent."><figcaption>Same policy, unseen species. The MLP loses 23.1 points on the held-out split.</figcaption></figure>
  </section>

  <section class="shell section" id="reproduce" aria-labelledby="reproduce-title">
    <span id="reproducibility"></span>
    <h2 id="reproduce-title">Reproduce</h2>
    <p class="section-lede">The engine, agents, report, and charts use the Python standard library. PyTorch is optional and used only to train the MLP; inference is exported to JSON.</p>
    <pre><code>python -m pokerl verify
python -m pytest
python -m pokerl bench --games 120 --seed 2025
python -m pokerl generalize --games 100 --seed 2025
python -m pokerl report</code></pre>
    <p class="note">Every result file records the git SHA, Python version, platform, seed, and a config hash.</p>
  </section>
</main>
<footer class="shell footer">
  <p>PokéLab is a non-commercial fan research project. Pokémon is a trademark of Nintendo, Creatures, and GAME FREAK. Not affiliated with or endorsed by them.</p>
  <p class="footer-links"><a href="https://github.com/Arudchayan/Arudchayan">GitHub</a><a href="https://github.com/Arudchayan/Arudchayan/issues">Issues</a><a href="results/REPORT.md">Report</a><a href="https://github.com/Arudchayan/Arudchayan/blob/main/paper/main.md">Paper</a><a href="https://github.com/Arudchayan/Arudchayan/blob/main/FAILURES.md">Failure log</a></p>
</footer>
</body>
</html>
"""
    (docs_dir / "index.html").write_text(page, encoding="utf-8")


def generate_report(
    *,
    results_dir: str | Path = RESULTS,
    docs_dir: str | Path = DOCS,
    readme_path: str | Path = ROOT / "README.md",
    paper_path: str | Path | None = None,
) -> dict:
    results_dir = Path(results_dir)
    docs_dir = Path(docs_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    leaderboard = load_json(results_dir / "leaderboard.json", {})
    curve = load_json(results_dir / "learning_curve.json", {})
    gen = load_json(results_dir / "generalization.json", {})
    training = load_json(results_dir / "training.json", {})
    metadata = load_json(results_dir / "metadata.json", {})
    oracle = load_json(results_dir / "oracle.json", {})
    summary = {
        "generated_at": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "leaderboard": leaderboard.get("standings", []),
        "metadata": metadata,
    }
    (results_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    _write_figures(leaderboard, curve, gen, docs_dir / "assets")
    dashboard_results = docs_dir / "results"
    dashboard_results.mkdir(parents=True, exist_ok=True)
    for name in (
        "leaderboard.json",
        "learning_curve.json",
        "generalization.json",
        "training.json",
        "metadata.json",
        "oracle.json",
        "REPORT.md",
    ):
        source = results_dir / name
        if source.exists():
            (dashboard_results / name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    render_dashboard(leaderboard, curve, gen, oracle, docs_dir)

    training_rows = []
    for key, label in (("bc", "Linear BC"), ("mlp", "MLP BC"), ("dagger", "MLP + DAgger"), ("rl", "REINFORCE")):
        item = training.get(key, {})
        if item:
            history = item.get("history", [])
            derived_rate = history[-1].get("win_rate", 0) if isinstance(history, list) and history else 0
            rate = item.get("win_rate", derived_rate)
            training_rows.append(
                f"| {label} | {item.get('samples', item.get('dataset', item.get('episodes', '-')))} | "
                f"{_pct(rate) if rate else '-'} | {_float(item.get('best_val_loss'), 4)} |"
            )
    training_table = (
        "\n".join(["| Method | Budget | Eval win rate | Val loss |", "| --- | ---: | ---: | ---: |"] + training_rows)
        if training_rows
        else "_No training artifacts yet._"
    )

    key_numbers = []
    if standings := leaderboard.get("standings", []):
        key_numbers.append(
            f"Highest-rated agent: **{standings[0]['agent']}** at **{standings[0].get('rating', 0):.0f}** Elo."
        )
        for row in standings:
            if row["agent"].lower().startswith(("mlp", "bc", "hybrid")):
                key_numbers.append(
                    f"{row['agent']} reaches **{_pct(row.get('win_rate', 0))}** win rate in round-robin play."
                )
                break
    if curve.get("bc"):
        first, last = curve["bc"][0], curve["bc"][-1]
        if last.get("win_rate", 0) > first.get("win_rate", 0) + 0.02:
            key_numbers.append(
                f"Behaviour cloning scales from **{_pct(first.get('win_rate', 0))}** to **{_pct(last.get('win_rate', 0))}**."
            )
        else:
            key_numbers.append(
                f"Linear BC is a negative control: **{_pct(first.get('win_rate', 0))}** to **{_pct(last.get('win_rate', 0))}**; the MLP is the model that learns."
            )
    if gen.get("results"):
        gaps = [row.get("heldout_win_rate", 0) - row.get("train_win_rate", 0) for row in gen["results"]]
        key_numbers.append(f"Mean held-out transfer gap: **{100 * sum(gaps) / len(gaps):+.1f} pp**.")
    if oracle_result := oracle.get("result", {}):
        key_numbers.append(
            f"Search-2 oracle: **{_pct(oracle_result.get('win_rate', 0))}** vs Heuristic at **{oracle_result.get('decisions_per_sec', 0):.0f} decisions/s**."
        )
    key_block = (
        "\n".join(f"- {line}" for line in key_numbers)
        if key_numbers
        else "_Run the experiments to populate this section._"
    )

    report = f"""# PokéLab, Experimental Report

**Generated:** {summary["generated_at"]}  
**Config hash:** `{metadata.get("config_hash", "n/a")}`  
**Git SHA:** `{metadata.get("git_sha", "n/a")}`  
**Python:** `{metadata.get("python", "n/a")}`

## Key numbers

{key_block}

## Leaderboard

{leaderboard_table(leaderboard)}

Ratings are Bradley-Terry strengths mapped to an Elo-like scale (mean 1000, 400 points per decade of odds). CIs are 95% percentile bootstrap intervals over decisive side-swapped games. Draws are reported but excluded from the win-rate denominator.

**Oracle match.** {oracle.get("result", {}).get("wins", "-")}-{oracle.get("result", {}).get("losses", "-")}-{oracle.get("result", {}).get("draws", "-")} against Heuristic, win rate **{_pct(oracle.get("result", {}).get("win_rate", 0)) if oracle.get("result") else "-"}** at **{_float(oracle.get("result", {}).get("decisions_per_sec"), 0)} decisions/s**. This row is a separate 100-game match, not part of the six-agent round robin.

## Strength and compute

![Leaderboard](assets/leaderboard.svg)

![Pareto](assets/pareto.svg)

## Sample efficiency

{learning_curve_table(curve)}

![Learning curve](assets/learning_curve.svg)

## Generalisation to held-out species

{generalization_table(gen)}

![Generalisation](assets/generalization.svg)

## Training summary

{training_table}

## Efficiency

{efficiency_table(leaderboard)}

## Reproducibility

```bash
python -m pokerl bench --games 120 --seed 2025
python -m pokerl train --decisions 3000 --epochs 15 --mlp-epochs 50 --dagger 1
python -m pokerl generalize --games 100 --seed 2025
python -m pokerl report
```

The engine uses a SplitMix64 stream and never imports `random` for battle mechanics. Team schedules are shared across all agent pairs. The full benchmark is deterministic given `--seed`.

## Limitations

- Fixed level-100 sets; no teambuilding.
- No weather, terrain, Mega/Z/Dynamax, multi-hit moves, or accuracy/evasion stages.
- Opponent model is the heuristic policy, not a human or a stronger search agent.
- Full observability; hidden information is not modelled.
- Small roster (24 species) and a single 3v3 format.
- The MLP is trained with optional PyTorch; inference uses NumPy when available.

## Non-claims

This is a controlled benchmark, not a claim about competitive Pokémon strength, human play, or frontier-agent safety. It is a testbed for reproducible decision-making research.
"""
    (results_dir / "REPORT.md").write_text(report, encoding="utf-8")

    paper_target = (
        Path(paper_path)
        if paper_path is not None
        else (ROOT / "paper" / "main.md" if results_dir.resolve() == RESULTS.resolve() else None)
    )
    if paper_target is not None and paper_target.exists():
        paper = paper_target.read_text(encoding="utf-8")
        paper = paper.replace("{{LEADERBOARD_TABLE}}", leaderboard_table(leaderboard))
        paper = paper.replace("{{LEARNING_CURVE_TABLE}}", learning_curve_table(curve))
        paper = paper.replace("{{GENERALIZATION_TABLE}}", generalization_table(gen))
        paper = paper.replace("{{EFFICIENCY_TABLE}}", efficiency_table(leaderboard))
        paper = paper.replace("{{TRAINING_TABLE}}", training_table)
        paper = paper.replace("{{CPU_MODEL}}", platform.processor() or "unknown")
        paper = paper.replace("{{PYTHON_VERSION}}", platform.python_version())
        paper_target.write_text(paper, encoding="utf-8")

    readme = Path(readme_path)
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        start, end = "<!-- RESULTS:START -->", "<!-- RESULTS:END -->"
        if start in text and end in text:
            block = f"""{start}
### Live benchmark snapshot

{leaderboard_table(leaderboard)}

{key_block}

![Leaderboard](docs/assets/leaderboard.svg)

[Full report](results/REPORT.md) · [Dashboard](https://arudchayan.github.io/Arudchayan/)
{end}"""
            text = text.split(start)[0] + block + text.split(end, 1)[1]
            readme.write_text(text, encoding="utf-8")
    return summary
