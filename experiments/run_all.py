"""Run the full reference experiment pipeline.

Usage:
    python experiments/run_all.py

This is deliberately boring: it invokes the same CLI commands documented in the
README, in order, and stops on the first failure.  It exists so a reviewer does
not have to reconstruct the experiment sequence from prose.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS: list[list[str]] = [
    [
        "train",
        "--decisions",
        "3000",
        "--epochs",
        "15",
        "--mlp-epochs",
        "50",
        "--dagger",
        "1",
        "--dagger-decisions",
        "400",
        "--eval-games",
        "80",
        "--seed",
        "2025",
    ],
    [
        "bench",
        "--games",
        "120",
        "--seed",
        "2025",
        "--agents",
        "random",
        "greedy",
        "heuristic",
        "search-1",
        "mlp",
        "dagger",
        "hybrid",
        "--no-report",
    ],
    [
        "eval",
        "--agent",
        "search-2",
        "--opponent",
        "heuristic",
        "--games",
        "100",
        "--seed",
        "2025",
        "--out",
        "results/oracle.json",
    ],
    ["generalize", "--games", "100", "--seed", "2025"],
    ["report"],
    ["dispatch"],
]


def main() -> int:
    log_path = ROOT / "results" / "run.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        for index, args in enumerate(COMMANDS, start=1):
            printable = " ".join(["python", "-m", "pokerl", *args])
            print(f"\n[{index}/{len(COMMANDS)}] {printable}", flush=True)
            log.write(f"\n[{index}/{len(COMMANDS)}] {printable}\n")
            log.flush()
            started = time.perf_counter()
            log.flush()
            result = subprocess.run(
                [sys.executable, "-m", "pokerl", *args],
                cwd=ROOT,
                text=True,
                stdout=log,
                stderr=log,
            )
            log.flush()
            elapsed = time.perf_counter() - started
            if result.returncode != 0:
                print(f"FAILED after {elapsed:.1f}s", file=sys.stderr, flush=True)
                return result.returncode
            print(f"done in {elapsed:.1f}s", flush=True)
    print(f"\nAll experiments complete. Log: {log_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
