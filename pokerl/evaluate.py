"""Evaluation: side-swapped matches, bootstrap CIs, and Bradley-Terry ratings."""

from __future__ import annotations

import math
import time
from collections.abc import Sequence

from .agents import Agent
from .dex import ALL_SPECIES, sample_team
from .engine import Battle
from .rng import RNG


def bootstrap_ci(
    wins: int, n: int, *, resamples: int = 2000, seed: int = 0, alpha: float = 0.05
) -> tuple[float, float]:
    if n <= 0:
        return (0.5, 0.5)
    rng = RNG(seed ^ 0xC1)
    estimates: list[float] = []
    for _ in range(resamples):
        count = 0
        for _ in range(n):
            if rng.random() < wins / n:
                count += 1
        estimates.append(count / n)
    estimates.sort()
    lo = estimates[int((alpha / 2) * resamples)]
    hi = estimates[min(resamples - 1, int((1 - alpha / 2) * resamples))]
    return (lo, hi)


def _play_one(
    agent0: Agent,
    agent1: Agent,
    team0: Sequence[str],
    team1: Sequence[str],
    *,
    seed: int,
    max_decisions: int = 300,
) -> dict:
    battle = Battle(team0, team1, seed=seed)
    rng0 = RNG(seed ^ 0xAA55)
    rng1 = RNG(seed ^ 0x55AA)
    decisions = 0
    t0 = time.perf_counter()
    while not battle.done and decisions < max_decisions:
        a0 = agent0.act(battle, 0, rng0)
        a1 = agent1.act(battle, 1, rng1)
        battle.step(a0, a1)
        decisions += 1
    elapsed = time.perf_counter() - t0
    if not battle.done:
        battle.winner = -1
    return {
        "winner": battle.winner,
        "turns": battle.turn,
        "decisions": decisions,
        "elapsed": elapsed,
        "winner_name": "draw" if battle.winner == -1 else (agent0.name if battle.winner == 0 else agent1.name),
    }


def match(
    agent_a: Agent,
    agent_b: Agent,
    games: int = 200,
    *,
    seed: int = 0,
    pool: Sequence[str] = ALL_SPECIES,
    team_size: int = 3,
    max_decisions: int = 300,
) -> dict:
    """Play a side-swapped match on identical team pairs.

    Each team pair is played twice (A on player 1, then A on player 2), which
    removes first-player and team-composition bias from the comparison.
    """
    if games < 2:
        games = 2
    pairs = games // 2
    extra = games % 2
    wins = losses = draws = 0
    turns = 0
    decisions = 0
    elapsed = 0.0
    total = 0
    for g in range(pairs):
        team_rng = RNG((seed * 1_000_003 + g) & ((1 << 64) - 1))
        team0 = sample_team(pool, team_size, team_rng)
        team1 = sample_team(pool, team_size, team_rng)
        for swapped in (False, True):
            if swapped:
                result = _play_one(
                    agent_b, agent_a, team1, team0, seed=seed * 7919 + g * 31 + 1, max_decisions=max_decisions
                )
                a_won = result["winner"] == 1
                b_won = result["winner"] == 0
            else:
                result = _play_one(
                    agent_a, agent_b, team0, team1, seed=seed * 7919 + g * 31, max_decisions=max_decisions
                )
                a_won = result["winner"] == 0
                b_won = result["winner"] == 1
            if result["winner"] == -1:
                draws += 1
            elif a_won:
                wins += 1
            elif b_won:
                losses += 1
            turns += result["turns"]
            decisions += result["decisions"]
            elapsed += result["elapsed"]
            total += 1
    if extra:
        team_rng = RNG((seed * 1_000_003 + pairs) & ((1 << 64) - 1))
        team0 = sample_team(pool, team_size, team_rng)
        team1 = sample_team(pool, team_size, team_rng)
        result = _play_one(
            agent_a, agent_b, team0, team1, seed=seed * 7919 + pairs * 31 + 2, max_decisions=max_decisions
        )
        if result["winner"] == -1:
            draws += 1
        elif result["winner"] == 0:
            wins += 1
        else:
            losses += 1
        turns += result["turns"]
        decisions += result["decisions"]
        elapsed += result["elapsed"]
        total += 1
    decisive = wins + losses
    win_rate = wins / decisive if decisive else 0.5
    lo, hi = bootstrap_ci(wins, decisive, seed=seed)
    return {
        "agent_a": agent_a.name,
        "agent_b": agent_b.name,
        "games": total,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": win_rate,
        "ci95": [lo, hi],
        "avg_turns": turns / total if total else 0.0,
        "avg_decisions": decisions / total if total else 0.0,
        "games_per_sec": total / elapsed if elapsed > 0 else 0.0,
        "decisions_per_sec": decisions / elapsed if elapsed > 0 else 0.0,
        "elapsed_s": elapsed,
    }


def bradley_terry(names: Sequence[str], results: dict[tuple[int, int], dict]) -> list[float]:
    """Fit Bradley-Terry strengths with the MM algorithm and return Elo-like ratings."""
    n = len(names)
    wins = [[0.0] * n for _ in range(n)]
    total = [[0.0] * n for _ in range(n)]
    for (i, j), result in results.items():
        w = result["wins"] + 0.5 * result["draws"]
        losses = result["losses"] + 0.5 * result["draws"]
        wins[i][j] += w
        wins[j][i] += losses
        total[i][j] += w + losses
        total[j][i] += w + losses
    p = [1.0] * n
    for _ in range(500):
        new = [0.0] * n
        for i in range(n):
            denom = sum(total[i][j] / (p[i] + p[j]) for j in range(n) if j != i and total[i][j] > 0)
            new[i] = sum(wins[i]) / denom if denom > 0 else p[i]
        gm = math.exp(sum(math.log(max(x, 1e-12)) for x in new) / n)
        p = [max(x / gm, 1e-12) for x in new]
    return [400.0 * math.log10(x) + 1000.0 for x in p]


def round_robin(
    agents: Sequence[Agent],
    *,
    games_per_pair: int = 200,
    seed: int = 0,
    pool: Sequence[str] = ALL_SPECIES,
    team_size: int = 3,
    max_decisions: int = 300,
    progress: bool = True,
) -> dict:
    results: dict[tuple[int, int], dict] = {}
    matches = []
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            if progress:
                print(f"  {agents[i].name} vs {agents[j].name} ({games_per_pair} games)...", flush=True)
            r = match(
                agents[i],
                agents[j],
                games_per_pair,
                seed=seed,
                pool=pool,
                team_size=team_size,
                max_decisions=max_decisions,
            )
            results[(i, j)] = r
            matches.append(r)
    names = [a.name for a in agents]
    ratings = bradley_terry(names, results)
    standings = []
    for i, agent in enumerate(agents):
        wins = sum(r["wins"] for (a, b), r in results.items() if a == i)
        wins += sum(r["losses"] for (a, b), r in results.items() if b == i)
        losses = sum(r["losses"] for (a, b), r in results.items() if a == i)
        losses += sum(r["wins"] for (a, b), r in results.items() if b == i)
        draws = sum(r["draws"] for (a, b), r in results.items() if a == i or b == i)
        total = wins + losses
        ci = bootstrap_ci(wins, total, seed=seed + i)
        standings.append(
            {
                "agent": agent.name,
                "rating": round(ratings[i], 1),
                "wins": wins,
                "losses": losses,
                "draws": draws,
                "win_rate": wins / total if total else 0.5,
                "ci95": [ci[0], ci[1]],
            }
        )
    standings.sort(key=lambda row: -row["rating"])
    return {"standings": standings, "matches": matches}


def speed_test(
    agent: Agent, *, games: int = 40, seed: int = 0, pool: Sequence[str] = ALL_SPECIES, team_size: int = 3
) -> dict:
    from .agents import HeuristicAgent

    result = match(agent, HeuristicAgent(), games, seed=seed, pool=pool, team_size=team_size)
    return {
        "agent": agent.name,
        "games": result["games"],
        "decisions_per_sec": result["decisions_per_sec"],
        "games_per_sec": result["games_per_sec"],
        "win_rate": result["win_rate"],
    }
