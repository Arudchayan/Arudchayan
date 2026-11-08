import json

from pokerl.reporting import generate_report


def test_generate_report_with_fixture(tmp_path):
    results = tmp_path / "results"
    docs = tmp_path / "docs"
    results.mkdir()
    leaderboard = {
        "standings": [
            {
                "agent": "Search-1",
                "rating": 1100.0,
                "wins": 60,
                "losses": 40,
                "draws": 0,
                "win_rate": 0.6,
                "ci95": [0.5, 0.7],
            },
            {
                "agent": "Heuristic",
                "rating": 1000.0,
                "wins": 50,
                "losses": 50,
                "draws": 0,
                "win_rate": 0.5,
                "ci95": [0.4, 0.6],
            },
        ],
        "matches": [
            {
                "agent_a": "Search-1",
                "agent_b": "Heuristic",
                "wins": 60,
                "losses": 40,
                "draws": 0,
                "decisions_per_sec": 300.0,
            }
        ],
    }
    (results / "leaderboard.json").write_text(json.dumps(leaderboard), encoding="utf-8")
    (results / "learning_curve.json").write_text(
        json.dumps({"bc": [{"samples": 500, "win_rate": 0.4}], "rl": []}), encoding="utf-8"
    )
    (results / "generalization.json").write_text(
        json.dumps({"results": [{"agent": "MLP BC", "train_win_rate": 0.5, "heldout_win_rate": 0.45}]}),
        encoding="utf-8",
    )
    (results / "training.json").write_text(
        json.dumps({"bc": {"samples": 500, "win_rate": 0.4, "best_val_loss": 1.0}}), encoding="utf-8"
    )
    (results / "metadata.json").write_text(
        json.dumps({"config_hash": "abc", "git_sha": "def", "python": "3.12"}), encoding="utf-8"
    )
    readme = tmp_path / "README.md"
    readme.write_text("<!-- RESULTS:START -->\nold\n<!-- RESULTS:END -->\n", encoding="utf-8")
    summary = generate_report(results_dir=results, docs_dir=docs, readme_path=readme)
    assert summary["generated_at"]
    assert (results / "REPORT.md").exists()
    assert (docs / "assets" / "leaderboard.svg").exists()
    assert (docs / "assets" / "pareto.svg").exists()
    assert "Search-1" in (results / "REPORT.md").read_text(encoding="utf-8")
    assert "Search-1" in readme.read_text(encoding="utf-8")
