"""Fill the README headline placeholders from committed result JSON.

This keeps the front page tied to evidence.  If a result file is missing, the
placeholder is left untouched so the gap is visible rather than guessed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def load(name: str) -> dict:
    path = RESULTS / name
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def test_count() -> int:
    return sum(
        len(re.findall(r"^def test_", path.read_text(encoding="utf-8"), flags=re.MULTILINE))
        for path in (ROOT / "tests").glob("test_*.py")
    )


def main() -> int:
    leaderboard = load("leaderboard.json")
    oracle = load("oracle.json")
    training = load("training.json")
    generalization = load("generalization.json")
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    replacements: dict[str, str] = {}

    matches = leaderboard.get("matches", [])
    search_match = next(
        (m for m in matches if m.get("agent_a") == "Search-1" and m.get("agent_b") == "Heuristic"),
        None,
    )
    reverse = False
    if search_match is None:
        search_match = next(
            (m for m in matches if m.get("agent_a") == "Heuristic" and m.get("agent_b") == "Search-1"),
            None,
        )
        reverse = search_match is not None
    if search_match:
        win_rate = 1.0 - search_match["win_rate"] if reverse else search_match["win_rate"]
        replacements["{{SEARCH1_WIN}}"] = pct(win_rate)
        replacements["{{SEARCH1_SPEED}}"] = f"{search_match['decisions_per_sec']:.0f}"
    oracle_result = oracle.get("result", {})
    if oracle_result:
        replacements["{{SEARCH2_WIN}}"] = pct(oracle_result["win_rate"])
        replacements["{{SEARCH2_SPEED}}"] = f"{oracle_result['decisions_per_sec']:.0f}"
    mlp = training.get("mlp", {})
    if mlp:
        replacements["{{MLP_WIN}}"] = pct(mlp.get("win_rate", 0))
    dagger = training.get("dagger", {})
    if dagger:
        replacements["{{DAGGER_WIN}}"] = pct(dagger.get("win_rate", 0))
    rows = generalization.get("results", [])
    if rows:
        gaps = [row.get("heldout_win_rate", 0) - row.get("train_win_rate", 0) for row in rows]
        replacements["{{HELDOUT_GAP}}"] = f"{100 * sum(gaps) / len(gaps):+.1f} pp"
    speeds = [m.get("decisions_per_sec", 0) for m in matches]
    if speeds:
        replacements["{{ENGINE_SPEED}}"] = f"{max(speeds):,.0f}"
    replacements["{{TEST_COUNT}}"] = str(test_count())

    for key, value in replacements.items():
        readme = readme.replace(key, value)
    readme_path.write_text(readme, encoding="utf-8")
    for key, value in replacements.items():
        print(f"{key} -> {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
