"""Training utilities: search distillation, REINFORCE, and a tabular baseline."""

from __future__ import annotations

import hashlib
import json
import math
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from .agents import (
    Agent,
    HeuristicAgent,
    LinearPolicy,
    PolicyAgent,
    QAgent,
    SearchAgent,
    softmax,
)
from .dex import HELD_OUT_SPECIES, TRAIN_SPECIES
from .engine import Battle, random_battle
from .features import N_FEATURES, feature_matrix, state_key
from .rng import RNG

# ``Softmax`` is not exported from agents; keep the module import surface clean.
try:
    from .agents import softmax
except ImportError:  # pragma: no cover
    softmax = None  # type: ignore


@dataclass(slots=True)
class SearchSample:
    features: list[list[float]]
    targets: list[float]
    chosen: int


@dataclass(slots=True)
class TrainingHistory:
    epochs: list[int]
    train_loss: list[float]
    val_loss: list[float]
    train_accuracy: list[float]
    val_accuracy: list[float]


def config_hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def collect_search_dataset(
    decisions: int = 4000,
    *,
    seed: int = 0,
    search_depth: int = 1,
    branch_limit: int = 3,
    pool: Sequence[str] = TRAIN_SPECIES,
    team_size: int = 3,
    temperature: float = 0.1,
    max_games: int = 4000,
    progress: Callable[[int, int], None] | None = None,
) -> list[SearchSample]:
    """Distil the search agent's action values into a behaviour-cloning dataset.

    The search agent plays both sides across games (alternating), against the
    heuristic opponent.  Every decision with more than one legal action becomes
    a training row with a soft target distribution over actions.
    """
    if softmax is None:  # pragma: no cover
        raise RuntimeError("softmax unavailable")
    rng = RNG(seed ^ 0xA11CE)
    search = SearchAgent(depth=search_depth, branch_limit=branch_limit)
    heuristic = HeuristicAgent()
    samples: list[SearchSample] = []
    games = 0
    t0 = time.perf_counter()
    while len(samples) < decisions and games < max_games:
        battle = random_battle(seed=rng.next_u64(), team_size=team_size, pool=pool)
        search_side = games % 2
        steps = 0
        while not battle.done and steps < 300:
            if search_side == 0:
                actions, feats = feature_matrix(battle, 0)
                if len(actions) > 1:
                    values = search.action_values(battle, 0)
                    target = softmax(values, temperature)
                    chosen = max(range(len(values)), key=lambda i: values[i])
                    samples.append(SearchSample(feats, target, chosen))
                    a0 = actions[chosen]
                else:
                    a0 = actions[0]
                a1 = heuristic.act(battle, 1, rng)
            else:
                a0 = heuristic.act(battle, 0, rng)
                actions, feats = feature_matrix(battle, 1)
                if len(actions) > 1:
                    values = search.action_values(battle, 1)
                    target = softmax(values, temperature)
                    chosen = max(range(len(values)), key=lambda i: values[i])
                    samples.append(SearchSample(feats, target, chosen))
                    a1 = actions[chosen]
                else:
                    a1 = actions[0]
            battle.step(a0, a1)
            steps += 1
        games += 1
        if progress is not None and games % 50 == 0:
            progress(len(samples), games)
    elapsed = time.perf_counter() - t0
    print(f"  collected {len(samples)} decisions from {games} games in {elapsed:.1f}s")
    return samples


def collect_policy_dataset(
    policy: LinearPolicy,
    decisions: int = 400,
    *,
    seed: int = 0,
    search_depth: int = 1,
    branch_limit: int = 3,
    pool: Sequence[str] = TRAIN_SPECIES,
    team_size: int = 3,
    temperature: float = 0.1,
    max_games: int = 2000,
) -> list[SearchSample]:
    """DAgger-style rollouts: visit the learned policy's states, ask search for labels."""
    rng = RNG(seed ^ 0xD16)
    search = SearchAgent(depth=search_depth, branch_limit=branch_limit)
    heuristic = HeuristicAgent()
    samples: list[SearchSample] = []
    games = 0
    while len(samples) < decisions and games < max_games:
        battle = random_battle(seed=rng.next_u64(), team_size=team_size, pool=pool)
        policy_side = games % 2
        steps = 0
        while not battle.done and steps < 300:
            if policy_side == 0:
                actions, feats = feature_matrix(battle, 0)
                if len(actions) > 1:
                    values = search.action_values(battle, 0)
                    target = softmax(values, temperature)
                    chosen = max(range(len(values)), key=lambda i: values[i])
                    samples.append(SearchSample(feats, target, chosen))
                a0 = policy.act(battle, 0, rng)
                a1 = heuristic.act(battle, 1, rng)
            else:
                a0 = heuristic.act(battle, 0, rng)
                actions, feats = feature_matrix(battle, 1)
                if len(actions) > 1:
                    values = search.action_values(battle, 1)
                    target = softmax(values, temperature)
                    chosen = max(range(len(values)), key=lambda i: values[i])
                    samples.append(SearchSample(feats, target, chosen))
                a1 = policy.act(battle, 1, rng)
            battle.step(a0, a1)
            steps += 1
        games += 1
    return samples


def train_dagger(
    initial: LinearPolicy,
    initial_samples: Sequence[SearchSample],
    *,
    iterations: int = 3,
    decisions_per_iteration: int = 400,
    epochs: int = 20,
    lr: float = 0.05,
    seed: int = 0,
    pool: Sequence[str] = TRAIN_SPECIES,
    team_size: int = 3,
    eval_games: int = 80,
) -> tuple[LinearPolicy, list[dict], dict]:
    """Dataset aggregation: retrain on states the current policy actually reaches."""
    from .evaluate import match

    dataset = list(initial_samples)
    policy = initial
    history: list[dict] = []
    for iteration in range(1, iterations + 1):
        new = collect_policy_dataset(
            policy,
            decisions_per_iteration,
            seed=seed + iteration * 101,
            branch_limit=3,
            pool=pool,
            team_size=team_size,
        )
        dataset.extend(new)
        policy, _, _ = train_behavior_cloning(
            dataset,
            epochs=epochs,
            lr=lr,
            seed=seed + iteration,
            initial=policy,
        )
        result = match(
            PolicyAgent(policy, name="BC"),
            HeuristicAgent(),
            eval_games,
            seed=seed + iteration * 37,
            pool=pool,
            team_size=team_size,
        )
        history.append(
            {
                "iteration": iteration,
                "dataset": len(dataset),
                "new_samples": len(new),
                "win_rate": result["win_rate"],
                "wins": result["wins"],
                "losses": result["losses"],
                "draws": result["draws"],
            }
        )
        print(f"  DAgger iter {iteration}: dataset={len(dataset)} win_rate={result['win_rate']:.3f}")
    meta = {
        "method": "dagger",
        "iterations": iterations,
        "decisions_per_iteration": decisions_per_iteration,
        "dataset": len(dataset),
        "seed": seed,
        "features": N_FEATURES,
        "train_species": list(TRAIN_SPECIES),
        "history": history,
    }
    policy.metadata = meta
    return policy, history, meta


def _cross_entropy(policy: LinearPolicy, samples: Sequence[SearchSample]) -> tuple[float, float]:
    if not samples:
        return 0.0, 0.0
    loss = 0.0
    correct = 0
    for sample in samples:
        logits = policy.logits(sample.features)
        probs = softmax(logits)
        loss += -sum(t * math.log(max(p, 1e-12)) for t, p in zip(sample.targets, probs))
        correct += int(max(range(len(probs)), key=lambda i: probs[i]) == sample.chosen)
    return loss / len(samples), correct / len(samples)


def train_behavior_cloning(
    samples: Sequence[SearchSample],
    *,
    epochs: int = 30,
    lr: float = 0.05,
    l2: float = 1e-4,
    seed: int = 0,
    val_fraction: float = 0.12,
    initial: LinearPolicy | None = None,
) -> tuple[LinearPolicy, TrainingHistory, dict]:
    if len(samples) < 10:
        raise ValueError("need at least 10 samples")
    rng = RNG(seed)
    order = list(range(len(samples)))
    rng.shuffle(order)
    val_size = max(1, int(len(samples) * val_fraction))
    val_idx = order[:val_size]
    train_idx = order[val_size:]
    policy = LinearPolicy(list(initial.weights) if initial is not None else [0.0] * N_FEATURES)
    history = TrainingHistory([], [], [], [], [])
    best_val = float("inf")
    best_weights = list(policy.weights)
    best_epoch = 0

    for epoch in range(1, epochs + 1):
        rng.shuffle(train_idx)
        for idx in train_idx:
            sample = samples[idx]
            probs = softmax(policy.logits(sample.features))
            for action, features in enumerate(sample.features):
                coeff = probs[action] - sample.targets[action]
                if abs(coeff) < 1e-10:
                    continue
                for j, value in enumerate(features):
                    if value:
                        policy.weights[j] -= lr * (coeff * value + l2 * policy.weights[j])
        train_loss, train_acc = _cross_entropy(policy, [samples[i] for i in train_idx])
        val_loss, val_acc = _cross_entropy(policy, [samples[i] for i in val_idx])
        history.epochs.append(epoch)
        history.train_loss.append(train_loss)
        history.val_loss.append(val_loss)
        history.train_accuracy.append(train_acc)
        history.val_accuracy.append(val_acc)
        if val_loss < best_val:
            best_val = val_loss
            best_weights = list(policy.weights)
            best_epoch = epoch
        lr *= 0.985
        if epoch == 1 or epoch % 5 == 0:
            print(
                f"  epoch {epoch:3d} train_loss={train_loss:.4f} val_loss={val_loss:.4f} acc={train_acc:.3f}/{val_acc:.3f}"
            )

    policy.weights = best_weights
    meta = {
        "method": "behaviour_cloning",
        "samples": len(samples),
        "train_samples": len(train_idx),
        "val_samples": len(val_idx),
        "epochs": epochs,
        "best_epoch": best_epoch,
        "best_val_loss": best_val,
        "lr": lr,
        "l2": l2,
        "seed": seed,
        "features": N_FEATURES,
        "train_species": list(TRAIN_SPECIES),
        "held_out_species": list(HELD_OUT_SPECIES),
    }
    policy.metadata = meta
    return policy, history, meta


@dataclass
class Adam:
    params: list[float]
    lr: float = 0.01
    beta1: float = 0.9
    beta2: float = 0.999
    eps: float = 1e-8
    m: list[float] | None = None
    v: list[float] | None = None
    t: int = 0

    def __post_init__(self) -> None:
        self.m = [0.0] * len(self.params)
        self.v = [0.0] * len(self.params)

    def step(self, grad: Sequence[float]) -> None:
        self.t += 1
        assert self.m is not None and self.v is not None
        b1 = 1.0 - self.beta1**self.t
        b2 = 1.0 - self.beta2**self.t
        for i, g in enumerate(grad):
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * g
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * g * g
            self.params[i] += self.lr * (self.m[i] / b1) / (math.sqrt(self.v[i] / b2) + self.eps)


def _policy_gradient(
    policy: LinearPolicy,
    trajectory: Sequence[tuple[list[list[float]], int]],
    advantage: float,
) -> list[float]:
    grad = [0.0] * N_FEATURES
    if not trajectory:
        return grad
    for feats, chosen in trajectory:
        probs = softmax(policy.logits(feats))
        expected = [0.0] * N_FEATURES
        for prob, row in zip(probs, feats):
            for j, value in enumerate(row):
                if value:
                    expected[j] += prob * value
        for j, value in enumerate(feats[chosen]):
            if value:
                grad[j] += (value - expected[j]) * advantage
    scale = 1.0 / len(trajectory)
    return [g * scale for g in grad]


def train_reinforce(
    initial: LinearPolicy,
    *,
    episodes: int = 2000,
    seed: int = 0,
    lr: float = 0.02,
    gamma: float = 0.99,
    temperature: float = 1.0,
    opponent: Agent | None = None,
    pool: Sequence[str] = TRAIN_SPECIES,
    team_size: int = 3,
    eval_every: int = 250,
    eval_games: int = 80,
    progress: Callable[[int, float], None] | None = None,
) -> tuple[LinearPolicy, list[dict], dict]:
    """REINFORCE with a moving-average baseline, initialized from BC."""
    from .evaluate import match

    rng = RNG(seed ^ 0xBEEF)
    policy = LinearPolicy(list(initial.weights), dict(initial.metadata))
    policy.name = "RL"
    optimizer = Adam(policy.weights, lr=lr)
    opponent = opponent or HeuristicAgent()
    baseline = 0.0
    history: list[dict] = []
    best_rate = -1.0
    best_weights = list(policy.weights)
    best_episode = 0
    t0 = time.perf_counter()

    for episode in range(1, episodes + 1):
        battle = random_battle(seed=rng.next_u64(), team_size=team_size, pool=pool)
        policy_side = episode % 2
        trajectory: list[tuple[list[list[float]], int]] = []
        while not battle.done and len(trajectory) < 300:
            if policy_side == 0:
                actions, feats = feature_matrix(battle, 0)
                probs = softmax(policy.logits(feats), temperature)
                chosen = _sample_index(probs, rng)
                trajectory.append((feats, chosen))
                a0 = actions[chosen]
                a1 = opponent.act(battle, 1, rng)
            else:
                a0 = opponent.act(battle, 0, rng)
                actions, feats = feature_matrix(battle, 1)
                probs = softmax(policy.logits(feats), temperature)
                chosen = _sample_index(probs, rng)
                trajectory.append((feats, chosen))
                a1 = actions[chosen]
            battle.step(a0, a1)
        reward = battle.rewards()[policy_side]
        advantage = reward - baseline
        baseline = 0.95 * baseline + 0.05 * reward
        grad = _policy_gradient(policy, trajectory, advantage)
        optimizer.step(grad)

        if episode % eval_every == 0 or episode == episodes:
            result = match(
                _PolicyOnly(policy), opponent, eval_games, seed=seed + episode * 17, pool=pool, team_size=team_size
            )
            history.append(
                {
                    "episode": episode,
                    "win_rate": result["win_rate"],
                    "wins": result["wins"],
                    "losses": result["losses"],
                    "draws": result["draws"],
                    "avg_turns": result["avg_turns"],
                    "elapsed_s": round(time.perf_counter() - t0, 2),
                }
            )
            if result["win_rate"] > best_rate:
                best_rate = result["win_rate"]
                best_weights = list(policy.weights)
                best_episode = episode
            if progress is not None:
                progress(episode, result["win_rate"])
            print(
                f"  episode {episode:4d} win_rate={result['win_rate']:.3f} ({result['wins']}-{result['losses']}-{result['draws']})"
            )

    policy.weights = best_weights
    meta = {
        "method": "reinforce",
        "episodes": episodes,
        "best_episode": best_episode,
        "best_win_rate": best_rate,
        "lr": lr,
        "gamma": gamma,
        "seed": seed,
        "features": N_FEATURES,
        "initial_method": initial.metadata.get("method", "unknown"),
        "train_species": list(TRAIN_SPECIES),
        "held_out_species": list(HELD_OUT_SPECIES),
    }
    policy.metadata = meta
    return policy, history, meta


class _PolicyOnly(Agent):
    """Tiny adapter so ``match`` can drive a bare LinearPolicy."""

    def __init__(self, policy: LinearPolicy) -> None:
        self.policy = policy
        self.name = "Policy"

    def act(self, battle: Battle, side: int, rng: RNG):  # type: ignore[override]
        return self.policy.act(battle, side, rng)


def _sample_index(probs: Sequence[float], rng: RNG) -> int:
    roll = rng.random()
    acc = 0.0
    for i, prob in enumerate(probs):
        acc += prob
        if roll <= acc:
            return i
    return len(probs) - 1


def train_qlearning(
    episodes: int = 3000,
    *,
    seed: int = 0,
    alpha: float = 0.15,
    gamma: float = 0.98,
    epsilon_start: float = 0.35,
    epsilon_end: float = 0.02,
    opponent: Agent | None = None,
    pool: Sequence[str] = TRAIN_SPECIES,
    team_size: int = 3,
) -> tuple[QAgent, dict]:
    """Tabular Q-learning on a discretised state (deliberately sample-hungry)."""
    rng = RNG(seed ^ 0x1234)
    q: dict[str, list[float]] = {}
    opponent = opponent or HeuristicAgent()
    wins = 0

    def values_for(battle: Battle, side: int) -> list[float]:
        key = repr(state_key(battle, side))
        if key not in q:
            q[key] = [0.0] * 10
        return q[key]

    for episode in range(1, episodes + 1):
        battle = random_battle(seed=rng.next_u64(), team_size=team_size, pool=pool)
        q_side = episode % 2
        eps = epsilon_start + (epsilon_end - epsilon_start) * (episode / max(1, episodes))
        steps = 0
        while not battle.done and steps < 300:
            if q_side == 0:
                actions = battle.legal_actions(0)
                if rng.random() < eps:
                    a0 = rng.choice(actions)
                else:
                    vals = values_for(battle, 0)
                    a0 = max(actions, key=lambda a: vals[QAgent._action_index(a)])
                a1 = opponent.act(battle, 1, rng)
            else:
                a0 = opponent.act(battle, 0, rng)
                actions = battle.legal_actions(1)
                if rng.random() < eps:
                    a1 = rng.choice(actions)
                else:
                    vals = values_for(battle, 1)
                    a1 = max(actions, key=lambda a: vals[QAgent._action_index(a)])
            prev_key = repr(state_key(battle, q_side))
            prev_values = q.get(prev_key)
            prev_action = a0 if q_side == 0 else a1
            prev_idx = QAgent._action_index(prev_action)
            battle.step(a0, a1)
            reward = battle.rewards()[q_side]
            if prev_values is None:
                prev_values = [0.0] * 10
                q[prev_key] = prev_values
            if battle.done:
                target = reward
            else:
                next_values = values_for(battle, q_side)
                target = reward + gamma * max(next_values)
            prev_values[prev_idx] += alpha * (target - prev_values[prev_idx])
            steps += 1
        wins += int(battle.winner == q_side)

    meta = {
        "method": "tabular_q",
        "episodes": episodes,
        "alpha": alpha,
        "gamma": gamma,
        "epsilon_start": epsilon_start,
        "epsilon_end": epsilon_end,
        "seed": seed,
        "states": len(q),
        "train_win_rate": wins / max(1, episodes),
        "train_species": list(TRAIN_SPECIES),
    }
    agent = QAgent(q, epsilon=0.0)
    return agent, meta


def save_json(path: str | Path, payload: object) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
