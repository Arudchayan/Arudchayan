"""Command-line interface for PokéLab."""

from __future__ import annotations

import argparse
import datetime
import json
import platform
import subprocess
from collections.abc import Sequence
from pathlib import Path

from .agents import (
    Agent,
    GreedyAgent,
    HeuristicAgent,
    HybridAgent,
    LinearPolicy,
    PolicyAgent,
    QAgent,
    RandomAgent,
    SearchAgent,
)
from .dex import ALL_SPECIES, HELD_OUT_SPECIES, TRAIN_SPECIES
from .dispatch import daily_dispatch, render_dispatch
from .engine import Battle, random_battle
from .evaluate import match, round_robin
from .reporting import generate_report
from .rng import RNG
from .train import (
    collect_search_dataset,
    config_hash,
    save_json,
    train_behavior_cloning,
    train_qlearning,
    train_reinforce,
)

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "artifacts"
RESULTS = ROOT / "results"


def _policy_path(name: str) -> Path:
    return ARTIFACTS / name


def _load_policy_if_exists(path: Path) -> LinearPolicy | None:
    if path.exists():
        return LinearPolicy.load(path)
    return None


def _load_mlp_if_exists(path: Path):
    if not path.exists():
        return None
    try:
        from .nn import MLPPolicy

        return MLPPolicy.load(path)
    except Exception:
        return None


def build_agents(
    names: Sequence[str] | None = None,
    *,
    include_search: bool = True,
    quick: bool = False,
) -> list[Agent]:
    named: list[Agent] = []
    if names:
        for name in names:
            key = name.lower()
            if key == "random":
                named.append(RandomAgent())
            elif key == "greedy":
                named.append(GreedyAgent())
            elif key == "heuristic":
                named.append(HeuristicAgent())
            elif key == "search":
                named.append(SearchAgent(depth=2 if not quick else 1, branch_limit=3))
            elif key == "search-1":
                named.append(SearchAgent(depth=1, branch_limit=3))
            elif key == "search-2":
                named.append(SearchAgent(depth=2, branch_limit=3))
            elif key in ("bc", "linear"):
                policy = _load_policy_if_exists(_policy_path("policy_bc.json"))
                if policy:
                    named.append(PolicyAgent(policy, name="Linear BC"))
            elif key in ("mlp", "mlp-bc"):
                policy = _load_mlp_if_exists(_policy_path("policy_mlp.json"))
                if policy:
                    named.append(PolicyAgent(policy, name="MLP BC"))
            elif key in ("dagger", "mlp-dagger"):
                policy = _load_mlp_if_exists(_policy_path("policy_dagger.json"))
                if policy:
                    named.append(PolicyAgent(policy, name="MLP+DAgger"))
            elif key in ("rl", "reinforce"):
                policy = _load_policy_if_exists(_policy_path("policy_rl.json"))
                if policy:
                    named.append(PolicyAgent(policy, name="REINFORCE"))
            elif key == "hybrid":
                policy = _load_mlp_if_exists(_policy_path("policy_mlp.json"))
                if policy:
                    named.append(HybridAgent(policy, depth=1, top_k=3))
            elif key == "q":
                path = _policy_path("q_table.json")
                if path.exists():
                    named.append(QAgent.load(path))
            else:
                raise SystemExit(f"Unknown agent: {name}")
        return named

    named = [RandomAgent(), GreedyAgent(), HeuristicAgent()]
    if include_search and not quick:
        named.append(SearchAgent(depth=1, branch_limit=3))
    mlp = _load_mlp_if_exists(_policy_path("policy_mlp.json"))
    if mlp:
        named.append(PolicyAgent(mlp, name="MLP BC"))
        named.append(HybridAgent(mlp, depth=1, top_k=3))
    bc = _load_policy_if_exists(_policy_path("policy_bc.json"))
    if bc:
        named.append(PolicyAgent(bc, name="Linear BC"))
    dagger = _load_mlp_if_exists(_policy_path("policy_dagger.json"))
    if dagger:
        named.append(PolicyAgent(dagger, name="MLP+DAgger"))
    rl = _load_policy_if_exists(_policy_path("policy_rl.json"))
    if rl:
        named.append(PolicyAgent(rl, name="REINFORCE"))
    q_path = _policy_path("q_table.json")
    if q_path.exists():
        named.append(QAgent.load(q_path))
    return named


def _git_sha() -> str:
    try:
        return (
            subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=5
            ).stdout.strip()
            or "unknown"
        )
    except Exception:
        return "unknown"


def _metadata(seed: int, extra: dict | None = None) -> dict:
    return {
        "generated_at": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC"),
        "git_sha": _git_sha(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "seed": seed,
        "config_hash": config_hash({"seed": seed, **(extra or {})}),
    }


def cmd_demo(args: argparse.Namespace) -> int:
    if args.team0 and args.team1:
        team0 = tuple(args.team0.split(","))
        team1 = tuple(args.team1.split(","))
        battle = Battle(team0, team1, seed=args.seed)
    elif args.team0 or args.team1:
        raise SystemExit("--team0 and --team1 must be provided together")
    else:
        battle = random_battle(seed=args.seed)
    agents = build_agents(["heuristic", "search-1"], include_search=True, quick=False)
    agent0 = agents[0]
    agent1 = agents[1]
    rng0, rng1 = RNG(args.seed ^ 0x1111), RNG(args.seed ^ 0x2222)
    while not battle.done:
        a0 = agent0.act(battle, 0, rng0)
        a1 = agent1.act(battle, 1, rng1)
        if args.verbose:
            print(
                f"Turn {battle.turn + 1}: {battle.active(0).name} {a0.kind}:{a0.index} | {battle.active(1).name} {a1.kind}:{a1.index}"
            )
        battle.step(a0, a1)
    print(f"PokeLab demo · seed {args.seed}")
    print(
        f"{' / '.join(battle.sides[0].team[0].types)} {battle.sides[0].team[0].name} vs {battle.sides[1].team[0].name}"
    )
    print(
        f"Winner: {'draw' if battle.winner == -1 else battle.sides[battle.winner].active_pokemon.name} after {battle.turn} turns"
    )
    if args.verbose:
        print("\n".join(battle.log))
    if args.json:
        print(
            json.dumps({"seed": args.seed, "winner": battle.winner, "turns": battle.turn, "log": battle.log}, indent=2)
        )
    return 0


def cmd_bench(args: argparse.Namespace) -> int:
    games = args.games if args.games % 2 == 0 else args.games + 1
    agents = build_agents(args.agents, quick=args.quick)
    if len(agents) < 2:
        raise SystemExit("Need at least two runnable agents (train artifacts missing?)")
    print(f"Benchmarking {len(agents)} agents · {games} games/pair · seed {args.seed}")
    result = round_robin(
        agents,
        games_per_pair=games,
        seed=args.seed,
        pool=ALL_SPECIES,
        team_size=args.team_size,
    )
    metadata = _metadata(args.seed, {"agents": [a.name for a in agents], "games": games, "team_size": args.team_size})
    output = {
        "standings": result["standings"],
        "matches": result["matches"],
        "metadata": metadata,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    save_json(RESULTS / "leaderboard.json", output)
    save_json(RESULTS / "metadata.json", metadata)
    print("\nStandings")
    print("| Agent | Elo | W–L–D | Win rate | 95% CI |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for row in result["standings"]:
        ci = row.get("ci95", [0, 0])
        print(
            f"| {row['agent']} | {row['rating']:.0f} | {row['wins']}–{row['losses']}–{row['draws']} | {100 * row['win_rate']:.1f}% | [{100 * ci[0]:.1f}, {100 * ci[1]:.1f}] |"
        )
    if not args.no_report:
        generate_report()
        print("\nWrote results/leaderboard.json, results/REPORT.md, docs/assets/*.svg")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    agents = build_agents([args.agent, args.opponent], quick=args.quick)
    if len(agents) < 2:
        raise SystemExit("Could not build both agents")
    result = match(agents[0], agents[1], args.games, seed=args.seed, pool=ALL_SPECIES, team_size=args.team_size)
    payload = {
        "agent": args.agent,
        "opponent": args.opponent,
        "result": result,
        "metadata": _metadata(args.seed, {"games": args.games}),
    }
    if args.out:
        save_json(args.out, payload)
    print(json.dumps(payload, indent=2))
    return 0


def cmd_train(args: argparse.Namespace) -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    print(f"Collecting {args.decisions} search-labelled decisions...")
    samples = collect_search_dataset(
        args.decisions,
        seed=args.seed,
        search_depth=args.search_depth,
        branch_limit=args.branch_limit,
        pool=TRAIN_SPECIES,
        team_size=args.team_size,
    )
    payload: dict = {"metadata": _metadata(args.seed, {"decisions": args.decisions})}
    curve_bc = []
    budgets = sorted({min(len(samples), b) for b in (500, 1000, 2000, 4000, len(samples)) if b <= len(samples)})
    for budget in budgets:
        print(f"\nLinear BC · {budget} decisions")
        policy, history, meta = train_behavior_cloning(samples[:budget], epochs=args.epochs, seed=args.seed)
        result = match(
            PolicyAgent(policy, name="Linear BC"),
            HeuristicAgent(),
            args.eval_games,
            seed=args.seed + 11,
            pool=TRAIN_SPECIES,
            team_size=args.team_size,
        )
        curve_bc.append(
            {"samples": budget, "win_rate": result["win_rate"], "wins": result["wins"], "losses": result["losses"]}
        )
        payload["bc"] = {
            "samples": budget,
            "epochs": args.epochs,
            "win_rate": result["win_rate"],
            "wins": result["wins"],
            "losses": result["losses"],
            "best_val_loss": meta.get("best_val_loss"),
            "history": {
                "epochs": history.epochs,
                "train_loss": history.train_loss,
                "val_loss": history.val_loss,
                "train_accuracy": history.train_accuracy,
                "val_accuracy": history.val_accuracy,
            },
        }
        policy.save(ARTIFACTS / "policy_bc.json")

    print("\nTraining MLP BC...")
    try:
        from .nn import train_mlp_bc

        mlp_result = train_mlp_bc(samples, epochs=args.mlp_epochs, seed=args.seed)
        mlp_result.policy.save(ARTIFACTS / "policy_mlp.json")
        mlp_eval = match(
            mlp_result.policy,
            HeuristicAgent(),
            args.eval_games,
            seed=args.seed + 12,
            pool=TRAIN_SPECIES,
            team_size=args.team_size,
        )
        payload["mlp"] = {
            "samples": len(samples),
            "epochs": args.mlp_epochs,
            "win_rate": mlp_eval["win_rate"],
            "wins": mlp_eval["wins"],
            "losses": mlp_eval["losses"],
            "best_val_loss": mlp_result.metadata.get("best_val_loss"),
        }
        print(f"MLP BC win rate: {mlp_eval['win_rate']:.3f}")
    except Exception as exc:
        print(f"MLP training unavailable: {exc}")

    if args.dagger:
        print(f"\nDAgger · {args.dagger} iterations")
        try:
            from .nn import train_mlp_dagger

            dagger_result = train_mlp_dagger(
                _load_mlp_if_exists(ARTIFACTS / "policy_mlp.json"),
                samples,
                iterations=args.dagger,
                decisions_per_iteration=args.dagger_decisions,
                epochs=args.mlp_epochs // 2,
                seed=args.seed + 1,
                eval_games=args.eval_games,
            )
            dagger_result.policy.save(ARTIFACTS / "policy_dagger.json")
            payload["dagger"] = {**dagger_result.metadata}
        except Exception as exc:
            print(f"DAgger unavailable: {exc}")

    if args.reinforce:
        print(f"\nREINFORCE · {args.reinforce} episodes")
        base = _load_policy_if_exists(ARTIFACTS / "policy_bc.json") or LinearPolicy()
        policy, history, meta = train_reinforce(
            base,
            episodes=args.reinforce,
            seed=args.seed + 2,
            eval_games=args.eval_games,
            pool=TRAIN_SPECIES,
            team_size=args.team_size,
        )
        policy.save(ARTIFACTS / "policy_rl.json")
        payload["rl"] = {**meta, "history": history}

    if args.q_episodes:
        print(f"\nTabular Q · {args.q_episodes} episodes")
        q_agent, meta = train_qlearning(
            args.q_episodes, seed=args.seed + 3, pool=TRAIN_SPECIES, team_size=args.team_size
        )
        q_agent.save(ARTIFACTS / "q_table.json")
        q_eval = match(
            q_agent,
            HeuristicAgent(),
            args.eval_games,
            seed=args.seed + 13,
            pool=TRAIN_SPECIES,
            team_size=args.team_size,
        )
        payload["q"] = {**meta, "win_rate": q_eval["win_rate"], "wins": q_eval["wins"], "losses": q_eval["losses"]}

    save_json(RESULTS / "training.json", payload)
    save_json(RESULTS / "learning_curve.json", {"bc": curve_bc, "rl": payload.get("rl", {}).get("history", [])})
    print("\nSaved artifacts and results/training.json")
    return 0


def cmd_generalize(args: argparse.Namespace) -> int:

    agents: list[tuple[str, Agent]] = [
        ("Heuristic", HeuristicAgent()),
        ("Search-1", SearchAgent(depth=1, branch_limit=3)),
    ]
    mlp = _load_mlp_if_exists(ARTIFACTS / "policy_mlp.json")
    if mlp:
        agents.append(("MLP BC", PolicyAgent(mlp, name="MLP BC")))
        agents.append(("Hybrid-1", HybridAgent(mlp, depth=1, top_k=3)))
    dagger = _load_mlp_if_exists(ARTIFACTS / "policy_dagger.json")
    if dagger:
        agents.append(("MLP+DAgger", PolicyAgent(dagger, name="MLP+DAgger")))
    rows = []
    for name, agent in agents:
        print(f"Generalisation · {name}")
        train_result = match(
            agent, HeuristicAgent(), args.games, seed=args.seed, pool=TRAIN_SPECIES, team_size=args.team_size
        )
        held_result = match(
            agent,
            HeuristicAgent(),
            args.games,
            seed=args.seed + 1,
            pool=HELD_OUT_SPECIES,
            team_size=min(args.team_size, len(HELD_OUT_SPECIES)),
        )
        rows.append(
            {
                "agent": name,
                "train_win_rate": train_result["win_rate"],
                "heldout_win_rate": held_result["win_rate"],
                "train_games": train_result["games"],
                "heldout_games": held_result["games"],
            }
        )
        print(f"  train={train_result['win_rate']:.3f} heldout={held_result['win_rate']:.3f}")
    save_json(
        RESULTS / "generalization.json", {"results": rows, "metadata": _metadata(args.seed, {"games": args.games})}
    )
    generate_report()
    print("Wrote results/generalization.json")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    summary = generate_report()
    print(json.dumps({k: summary[k] for k in ("generated_at",)}, indent=2))
    print("Wrote results/REPORT.md, docs/assets/*.svg, and refreshed the README block.")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    from .agents import HeuristicAgent, SearchAgent

    ok = True
    for seed in range(8):
        b1 = random_battle(seed=seed)
        b2 = random_battle(seed=seed)
        agents = [HeuristicAgent(), SearchAgent(depth=1, branch_limit=2)]
        r1 = b1.run(agents[0], agents[1])
        r2 = b2.run(agents[0], agents[1])
        same = r1 == r2 and b1.turn == b2.turn and b1.log == b2.log
        ok &= same
        print(f"seed {seed}: winner={r1} turns={b1.turn} deterministic={same}")
    print("OK" if ok else "FAILED")
    return 0 if ok else 1


def cmd_dispatch(args: argparse.Namespace) -> int:
    payload = daily_dispatch(update_readme_file=not args.no_readme)
    text = render_dispatch(payload)
    print(text.encode("ascii", "replace").decode("ascii"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pokerl", description="PokéLab: a reproducible Pokémon battle benchmark.")
    parser.add_argument("--version", action="version", version="pokerl 1.0.0")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run one battle with a turn log")
    demo.add_argument("--seed", type=int, default=7)
    demo.add_argument("--team0")
    demo.add_argument("--team1")
    demo.add_argument("--verbose", action="store_true")
    demo.add_argument("--json", action="store_true")
    demo.set_defaults(func=cmd_demo)

    bench = sub.add_parser("bench", help="run the round-robin benchmark")
    bench.add_argument("--games", type=int, default=120)
    bench.add_argument("--seed", type=int, default=2025)
    bench.add_argument("--team-size", type=int, default=3)
    bench.add_argument("--agents", nargs="*", help="agent names: random greedy heuristic search-1 bc mlp hybrid q")
    bench.add_argument("--quick", action="store_true")
    bench.add_argument("--no-report", action="store_true")
    bench.set_defaults(func=cmd_bench)

    ev = sub.add_parser("eval", help="run a single head-to-head match")
    ev.add_argument("--agent", default="heuristic")
    ev.add_argument("--opponent", default="random")
    ev.add_argument("--games", type=int, default=200)
    ev.add_argument("--seed", type=int, default=0)
    ev.add_argument("--team-size", type=int, default=3)
    ev.add_argument("--quick", action="store_true")
    ev.add_argument("--out", help="write the result JSON to this path")
    ev.set_defaults(func=cmd_eval)

    train = sub.add_parser("train", help="distil search, train baselines, and save artifacts")
    train.add_argument("--decisions", type=int, default=4000)
    train.add_argument("--epochs", type=int, default=25)
    train.add_argument("--mlp-epochs", type=int, default=60)
    train.add_argument("--dagger", type=int, default=0)
    train.add_argument("--dagger-decisions", type=int, default=600)
    train.add_argument("--reinforce", type=int, default=0)
    train.add_argument("--q-episodes", type=int, default=0)
    train.add_argument("--search-depth", type=int, default=1)
    train.add_argument("--branch-limit", type=int, default=3)
    train.add_argument("--eval-games", type=int, default=100)
    train.add_argument("--seed", type=int, default=2025)
    train.add_argument("--team-size", type=int, default=3)
    train.set_defaults(func=cmd_train)

    gen = sub.add_parser("generalize", help="measure held-out species transfer")
    gen.add_argument("--games", type=int, default=100)
    gen.add_argument("--seed", type=int, default=2025)
    gen.add_argument("--team-size", type=int, default=3)
    gen.set_defaults(func=cmd_generalize)

    report = sub.add_parser("report", help="regenerate report and figures")
    report.set_defaults(func=cmd_report)

    verify = sub.add_parser("verify", help="check determinism and basic invariants")
    verify.set_defaults(func=cmd_verify)

    dispatch = sub.add_parser("dispatch", help="write the deterministic daily dispatch")
    dispatch.add_argument("--no-readme", action="store_true")
    dispatch.set_defaults(func=cmd_dispatch)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
