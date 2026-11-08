"""Optional neural distillation with PyTorch, exported to dependency-free inference.

Training requires ``torch`` (an optional extra).  The exported JSON contains
plain nested lists, so evaluation and CI never import PyTorch.  This mirrors the
project's runtime philosophy: heavy libraries may *train* a policy, but the
benchmark itself stays reproducible and stdlib-only.
"""

from __future__ import annotations

import contextlib
import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .engine import Action, Battle, random_battle
from .features import N_FEATURES, feature_matrix
from .rng import RNG

MAX_ACTIONS = 6


def _relu(x: float) -> float:
    return x if x > 0.0 else 0.0


@dataclass
class MLPPolicy:
    """Pure-Python inference for a shared-trunk action-value/policy MLP."""

    weights: dict[str, list]
    metadata: dict

    def __post_init__(self) -> None:
        self.w1 = self.weights["w1"]
        self.b1 = self.weights["b1"]
        self.w2 = self.weights["w2"]
        self.b2 = self.weights["b2"]
        self.w3 = self.weights["w3"]
        self.b3 = self.weights["b3"]
        self.hidden1 = len(self.b1)
        self.hidden2 = len(self.b2)
        self.name = "MLP"
        self._np = None
        try:
            import numpy as np

            self._np = {
                "w1": np.asarray(self.w1, dtype=np.float64),
                "b1": np.asarray(self.b1, dtype=np.float64),
                "w2": np.asarray(self.w2, dtype=np.float64),
                "b2": np.asarray(self.b2, dtype=np.float64),
                "w3": np.asarray(self.w3, dtype=np.float64),
                "b3": np.asarray(self.b3, dtype=np.float64),
            }
        except ImportError:  # pragma: no cover - optional acceleration
            self._np = None

    def _logit(self, features: Sequence[float]) -> float:
        h1 = [_relu(sum(w * x for w, x in zip(row, features)) + b) for row, b in zip(self.w1, self.b1)]
        h2 = [_relu(sum(w * x for w, x in zip(row, h1)) + b) for row, b in zip(self.w2, self.b2)]
        return sum(w * x for w, x in zip(self.w3, h2)) + self.b3[0]

    def logits(self, feats: Sequence[Sequence[float]]) -> list[float]:
        if self._np is not None:
            np = __import__("numpy")
            x = np.asarray(feats, dtype=np.float64)
            h1 = np.maximum(x @ self._np["w1"].T + self._np["b1"], 0.0)
            h2 = np.maximum(h1 @ self._np["w2"].T + self._np["b2"], 0.0)
            return (h2 @ self._np["w3"] + self._np["b3"]).tolist()
        return [self._logit(row) for row in feats]

    def probabilities(self, feats: Sequence[Sequence[float]], temperature: float = 1.0) -> list[float]:
        values = self.logits(feats)
        peak = max(values) if values else 0.0
        exps = [math.exp((v - peak) / max(1e-6, temperature)) for v in values]
        total = sum(exps)
        return [e / total for e in exps]

    def act(self, battle: Battle, side: int, rng: RNG, *, sample: bool = False, temperature: float = 1.0) -> Action:
        actions, feats = feature_matrix(battle, side)
        if not actions:
            raise RuntimeError("no legal actions")
        values = self.logits(feats)
        if sample:
            probs = self.probabilities(feats, temperature)
            roll = rng.random()
            acc = 0.0
            for action, prob in zip(actions, probs):
                acc += prob
                if roll <= acc:
                    return action
            return actions[-1]
        return actions[max(range(len(values)), key=lambda i: values[i])]

    def save(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(
                {"version": 1, "n_features": N_FEATURES, "weights": self.weights, "metadata": self.metadata}, indent=2
            )
            + "\n",
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> MLPPolicy:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(payload["weights"], payload.get("metadata", {}))


def train_mlp_dagger(
    initial: object,
    initial_samples: Sequence[object],
    *,
    iterations: int = 2,
    decisions_per_iteration: int = 600,
    epochs: int = 40,
    seed: int = 0,
    eval_games: int = 80,
    pool: Sequence[str] | None = None,
    team_size: int = 3,
) -> MLPTrainingResult:
    """DAgger with the MLP policy as the learner and search as the expert."""
    from .agents import HeuristicAgent
    from .dex import TRAIN_SPECIES
    from .evaluate import match
    from .train import collect_policy_dataset

    pool = pool or TRAIN_SPECIES
    dataset = list(initial_samples)
    policy = initial
    history: list[dict] = []
    for iteration in range(1, iterations + 1):
        new = collect_policy_dataset(
            policy,  # type: ignore[arg-type]
            decisions_per_iteration,
            seed=seed + iteration * 53,
            pool=pool,
            team_size=team_size,
        )
        dataset.extend(new)
        result = train_mlp_bc(dataset, epochs=epochs, seed=seed + iteration)
        policy = result.policy
        evaluation = match(
            policy, HeuristicAgent(), eval_games, seed=seed + iteration * 101, pool=pool, team_size=team_size
        )
        history.append(
            {
                "iteration": iteration,
                "dataset": len(dataset),
                "new_samples": len(new),
                "win_rate": evaluation["win_rate"],
                "wins": evaluation["wins"],
                "losses": evaluation["losses"],
                "draws": evaluation["draws"],
            }
        )
        print(f"  MLP DAgger iter {iteration}: dataset={len(dataset)} win_rate={evaluation['win_rate']:.3f}")
    metadata = {
        "method": "mlp_dagger",
        "iterations": iterations,
        "dataset": len(dataset),
        "seed": seed,
        "history": history,
        "win_rate": history[-1]["win_rate"] if history else 0.0,
        "features": N_FEATURES,
    }
    policy.metadata = metadata
    return MLPTrainingResult(policy, {"history": history}, metadata)


@dataclass(slots=True)
class MLPTrainingResult:
    policy: MLPPolicy
    history: dict
    metadata: dict


def train_mlp_bc(
    samples: Sequence[object],
    *,
    epochs: int = 80,
    hidden1: int = 64,
    hidden2: int = 32,
    lr: float = 1e-3,
    batch_size: int = 64,
    val_fraction: float = 0.12,
    seed: int = 0,
    weight_decay: float = 1e-4,
) -> MLPTrainingResult:
    """Train a shared-trunk MLP policy on soft search targets.

    ``samples`` is a sequence of objects with ``features`` and ``targets``.
    """
    try:
        import torch
        from torch import nn
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("train_mlp_bc requires the optional 'torch' extra") from exc

    torch.manual_seed(seed)
    with contextlib.suppress(Exception):
        torch.set_num_threads(1)
    features = [s.features for s in samples]  # type: ignore[attr-defined]
    targets = [s.targets for s in samples]  # type: ignore[attr-defined]
    n = len(features)
    if n < 10:
        raise ValueError("need at least 10 samples")
    torch_rng = torch.Generator().manual_seed(seed)
    perm = torch.randperm(n, generator=torch_rng).tolist()
    val_size = max(1, int(n * val_fraction))
    val_idx = perm[:val_size]
    train_idx = perm[val_size:]

    max_actions = max(len(x) for x in features)
    x = torch.zeros((n, max_actions, N_FEATURES), dtype=torch.float32)
    y = torch.zeros((n, max_actions), dtype=torch.float32)
    mask = torch.zeros((n, max_actions), dtype=torch.bool)
    for i, (feat_rows, target) in enumerate(zip(features, targets)):
        for j, row in enumerate(feat_rows):
            x[i, j] = torch.tensor(row, dtype=torch.float32)
            y[i, j] = float(target[j])
            mask[i, j] = True

    class Net(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.trunk = nn.Sequential(
                nn.Linear(N_FEATURES, hidden1),
                nn.ReLU(),
                nn.Linear(hidden1, hidden2),
                nn.ReLU(),
                nn.Linear(hidden2, 1),
            )

        def forward(self, batch: torch.Tensor) -> torch.Tensor:
            return self.trunk(batch).squeeze(-1)

    net = Net()
    optimizer = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=weight_decay)
    train_x, train_y, train_mask = x[train_idx], y[train_idx], mask[train_idx]
    val_x, val_y, val_mask = x[val_idx], y[val_idx], mask[val_idx]

    def evaluate(xx, yy, mm) -> tuple[float, float]:
        net.eval()
        with torch.no_grad():
            logits = net(xx)
            logits = logits.masked_fill(~mm, -1e9)
            log_probs = torch.log_softmax(logits, dim=-1)
            loss = -(yy * log_probs).sum(dim=-1).mean().item()
            pred = logits.argmax(dim=-1)
            target = yy.argmax(dim=-1)
            acc = (pred[mm.any(dim=-1)] == target[mm.any(dim=-1)]).float().mean().item()
        return loss, acc

    best_val = float("inf")
    best_state = {k: v.detach().clone() for k, v in net.state_dict().items()}
    history = {"epoch": [], "train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    for epoch in range(1, epochs + 1):
        net.train()
        order = torch.randperm(len(train_idx), generator=torch_rng)
        for start in range(0, len(order), batch_size):
            batch = order[start : start + batch_size]
            logits = net(train_x[batch])
            logits = logits.masked_fill(~train_mask[batch], -1e9)
            log_probs = torch.log_softmax(logits, dim=-1)
            loss = -(train_y[batch] * log_probs).sum(dim=-1).mean()
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(net.parameters(), 5.0)
            optimizer.step()
        val_loss, val_acc = evaluate(val_x, val_y, val_mask)
        train_loss_eval, train_acc = evaluate(train_x, train_y, train_mask)
        history["epoch"].append(epoch)
        history["train_loss"].append(train_loss_eval)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)
        if val_loss < best_val:
            best_val = val_loss
            best_state = {k: v.detach().clone() for k, v in net.state_dict().items()}
        if epoch == 1 or epoch % 10 == 0:
            print(
                f"  mlp epoch {epoch:3d} train_loss={train_loss_eval:.4f} val_loss={val_loss:.4f} acc={train_acc:.3f}/{val_acc:.3f}"
            )

    net.load_state_dict(best_state)
    sd = net.state_dict()
    weights = {
        "w1": sd["trunk.0.weight"].tolist(),
        "b1": sd["trunk.0.bias"].tolist(),
        "w2": sd["trunk.2.weight"].tolist(),
        "b2": sd["trunk.2.bias"].tolist(),
        "w3": sd["trunk.4.weight"].squeeze(0).tolist(),
        "b3": sd["trunk.4.bias"].tolist(),
    }
    metadata = {
        "method": "mlp_behaviour_cloning",
        "samples": n,
        "epochs": epochs,
        "hidden": [hidden1, hidden2],
        "best_val_loss": best_val,
        "val_accuracy": history["val_acc"][history["val_loss"].index(min(history["val_loss"]))],
        "seed": seed,
        "features": N_FEATURES,
    }
    policy = MLPPolicy(weights, metadata)
    return MLPTrainingResult(policy, history, metadata)


def _build_net(weights: dict[str, list]) -> object:
    import torch.nn as nn

    hidden1 = len(weights["b1"])
    hidden2 = len(weights["b2"])
    n_features = len(weights["w1"][0])
    net = nn.Sequential(
        nn.Linear(n_features, hidden1),
        nn.ReLU(),
        nn.Linear(hidden1, hidden2),
        nn.ReLU(),
        nn.Linear(hidden2, 1),
    )
    import torch

    with torch.no_grad():
        net[0].weight.copy_(torch.tensor(weights["w1"]))
        net[0].bias.copy_(torch.tensor(weights["b1"]))
        net[2].weight.copy_(torch.tensor(weights["w2"]))
        net[2].bias.copy_(torch.tensor(weights["b2"]))
        net[4].weight.copy_(torch.tensor(weights["w3"]).unsqueeze(0))
        net[4].bias.copy_(torch.tensor(weights["b3"]))
    return net


def _export_net(net: object) -> dict[str, list]:
    sd = net.state_dict()  # type: ignore[attr-defined]
    return {
        "w1": sd["0.weight"].tolist(),
        "b1": sd["0.bias"].tolist(),
        "w2": sd["2.weight"].tolist(),
        "b2": sd["2.bias"].tolist(),
        "w3": sd["4.weight"].squeeze(0).tolist(),
        "b3": sd["4.bias"].tolist(),
    }


class _TorchAgent:
    def __init__(self, net: object, name: str = "MLP-RL") -> None:
        self.net = net
        self.name = name

    def act(self, battle: Battle, side: int, rng: RNG) -> Action:
        import torch

        actions, feats = feature_matrix(battle, side)
        with torch.no_grad():
            logits = self.net(torch.tensor(feats, dtype=torch.float32)).squeeze(-1)  # type: ignore[operator]
        return actions[int(torch.argmax(logits))]


def train_mlp_reinforce(
    initial: MLPPolicy,
    *,
    episodes: int = 1500,
    seed: int = 0,
    lr: float = 3e-4,
    entropy_coef: float = 0.01,
    opponent: object | None = None,
    pool: Sequence[str] | None = None,
    team_size: int = 3,
    eval_every: int = 250,
    eval_games: int = 80,
) -> MLPTrainingResult:
    """REINFORCE fine-tuning of the distilled MLP against a fixed opponent."""
    try:
        import torch
        from torch import nn
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("train_mlp_reinforce requires the optional 'torch' extra") from exc
    from .agents import HeuristicAgent
    from .dex import TRAIN_SPECIES
    from .evaluate import match

    pool = pool or TRAIN_SPECIES
    opponent = opponent or HeuristicAgent()
    torch.manual_seed(seed)
    with contextlib.suppress(Exception):
        torch.set_num_threads(1)
    net = _build_net(initial.weights)
    optimizer = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-4)  # type: ignore[attr-defined]
    rng = RNG(seed ^ 0x5EED)
    baseline = 0.0
    history: list[dict] = []
    best_rate = -1.0
    best_state = {k: v.detach().clone() for k, v in net.state_dict().items()}  # type: ignore[attr-defined]
    best_episode = 0
    for episode in range(1, episodes + 1):
        battle = random_battle(seed=rng.next_u64(), team_size=team_size, pool=pool)
        policy_side = episode % 2
        log_probs = []
        entropies = []
        while not battle.done:
            if policy_side == 0:
                actions, feats = feature_matrix(battle, 0)
                logits = net(torch.tensor(feats, dtype=torch.float32)).squeeze(-1)  # type: ignore[operator]
                logp = torch.log_softmax(logits, dim=0)
                probs = logp.exp()
                idx = int(torch.multinomial(probs, 1).item())
                log_probs.append(logp[idx])
                entropies.append(-(probs * logp).sum())
                a0 = actions[idx]
                a1 = opponent.act(battle, 1, rng)  # type: ignore[attr-defined]
            else:
                a0 = opponent.act(battle, 0, rng)  # type: ignore[attr-defined]
                actions, feats = feature_matrix(battle, 1)
                logits = net(torch.tensor(feats, dtype=torch.float32)).squeeze(-1)  # type: ignore[operator]
                logp = torch.log_softmax(logits, dim=0)
                probs = logp.exp()
                idx = int(torch.multinomial(probs, 1).item())
                log_probs.append(logp[idx])
                entropies.append(-(probs * logp).sum())
                a1 = actions[idx]
            battle.step(a0, a1)
        reward = battle.rewards()[policy_side]
        advantage = reward - baseline
        baseline = 0.95 * baseline + 0.05 * reward
        if log_probs:
            loss = -(torch.stack(log_probs).sum() * advantage) - entropy_coef * torch.stack(entropies).sum()
            loss = loss / len(log_probs)
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(net.parameters(), 5.0)
            optimizer.step()
        if episode % eval_every == 0 or episode == episodes:
            agent = _TorchAgent(net)
            result = match(agent, opponent, eval_games, seed=seed + episode * 13, pool=pool, team_size=team_size)
            history.append(
                {
                    "episode": episode,
                    "win_rate": result["win_rate"],
                    "wins": result["wins"],
                    "losses": result["losses"],
                    "draws": result["draws"],
                }
            )
            if result["win_rate"] > best_rate:
                best_rate = result["win_rate"]
                best_state = {k: v.detach().clone() for k, v in net.state_dict().items()}
                best_episode = episode
            print(f"  MLP-RL episode {episode:4d} win_rate={result['win_rate']:.3f}")
    net.load_state_dict(best_state)
    policy = MLPPolicy(_export_net(net), {})
    metadata = {
        "method": "mlp_reinforce",
        "episodes": episodes,
        "best_episode": best_episode,
        "best_win_rate": best_rate,
        "lr": lr,
        "entropy_coef": entropy_coef,
        "seed": seed,
        "features": N_FEATURES,
        "history": history,
    }
    policy.metadata = metadata
    return MLPTrainingResult(policy, {"history": history}, metadata)
