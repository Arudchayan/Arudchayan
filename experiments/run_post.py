"""Run the post-benchmark evaluation, report, and dispatch stages."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS: list[list[str]] = [
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
    with log_path.open("a", encoding="utf-8") as log:
        log.write("\n=== post-benchmark phase ===\n")
        for index, args in enumerate(COMMANDS, start=1):
            printable = " ".join(["python", "-m", "pokerl", *args])
            print(f"\n[{index}/{len(COMMANDS)}] {printable}", flush=True)
            log.write(f"\n[{index}/{len(COMMANDS)}] {printable}\n")
            log.flush()
            started = time.perf_counter()
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
