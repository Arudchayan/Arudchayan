"""Agent zoo: random, greedy, heuristic, search, linear policy, and hybrids."""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from pathlib import Path

from .engine import Action, Battle, Pokemon
from .features import N_FEATURES, feature_matrix, state_key
from .rng import RNG
from .types import effectiveness


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def softmax(values: Sequence[float], temperature: float = 1.0) -> list[float]:
    if not values:
        return []
    temperature = max(1e-6, temperature)
    scaled = [v / temperature for v in values]
    peak = max(scaled)
    exps = [math.exp(v - peak) for v in scaled]
    total = sum(exps)
    if total <= 0 or not math.isfinite(total):
        return [1.0 / len(values)] * len(values)
    return [e / total for e in exps]


def best_effectiveness(attacker: Pokemon, defender: Pokemon) -> float:
    best = 0.0
    for slot in attacker.moves:
        move = slot.move
        if not move.is_damaging:
            continue
        mult = effectiveness(move.type, defender.types)
        if move.type in attacker.types:
            mult *= 1.5
        best = max(best, mult)
    return best


def _speed_term(battle: Battle, user: Pokemon, foe: Pokemon) -> float:
    su = battle.effective_speed(user)
    sf = battle.effective_speed(foe)
    return (su - sf) / max(1, su + sf)


def matchup_score(battle: Battle, user: Pokemon, foe: Pokemon) -> float:
    offense = best_effectiveness(user, foe)
    defense = best_effectiveness(foe, user)
    return 1.15 * offense - 1.0 * defense + 0.55 * _speed_term(battle, user, foe) + 0.35 * user.hp_fraction


def _boost_total(pokemon: Pokemon) -> int:
    return sum(pokemon.boosts.values())


def heuristic_evaluation(battle: Battle, side: int) -> float:
    """Positional value in roughly [-2, 2], from ``side``'s perspective."""
    me_side = battle.sides[side]
    opp_side = battle.sides[1 - side]
    me = battle.active(side)
    opp = battle.opponent(side)
    own_hp = me_side.hp_fraction()
    opp_hp = opp_side.hp_fraction()
    own_alive = me_side.alive_count()
    opp_alive = opp_side.alive_count()
    own_bench = sum(p.hp_fraction for i, p in enumerate(me_side.team) if i != me_side.active)
    opp_bench = sum(p.hp_fraction for i, p in enumerate(opp_side.team) if i != opp_side.active)
    score = 1.55 * (own_hp - opp_hp)
    score += 0.55 * (own_alive - opp_alive)
    score += 0.12 * (_boost_total(me) - _boost_total(opp))
    score += 0.18 * (own_bench - opp_bench)
    score += 0.28 * matchup_score(battle, me, opp)
    if me.status is not None:
        score -= 0.12
    if opp.status is not None:
        score += 0.12
    if me_side.hazards:
        score -= 0.10
    if opp_side.hazards:
        score += 0.10
    if me.ability == "Regenerator":
        score += 0.05
    if opp.ability == "Regenerator":
        score -= 0.05
    return score


def heuristic_scores(battle: Battle, side: int) -> list[float]:
    """Score every legal action.  Higher is better."""
    me = battle.active(side)
    opp = battle.opponent(side)
    actions = battle.legal_actions(side)
    my_speed = battle.effective_speed(me)
    opp_speed = battle.effective_speed(opp)
    current_matchup = matchup_score(battle, me, opp)
    scores: list[float] = []

    for action in actions:
        if action.kind == "switch":
            incoming = battle.sides[side].team[action.index]
            incoming_matchup = matchup_score(battle, incoming, opp)
            score = 20.0 * (incoming_matchup - current_matchup) - 4.0
            score += 10.0 * (1.0 - me.hp_fraction) if me.hp_fraction < 0.35 else 0.0
            if incoming.ability == "Regenerator":
                score += 3.0
            if incoming.status is not None:
                score -= 4.0
            scores.append(score)
            continue

        if action.index == -1:
            scores.append(2.0)
            continue
        slot = me.moves[action.index]
        move = slot.move
        if move.is_damaging:
            accuracy = 1.0 if move.accuracy == 0 else move.accuracy / 100.0
            expected = battle.estimate_damage_fraction(side, move) * accuracy
            score = 100.0 * expected
            if expected >= opp.hp_fraction:
                score += 75.0
            if move.priority and opp_speed > my_speed:
                score += 14.0
            if move.contact and opp.ability in ("Rough Skin", "Iron Barbs"):
                score -= 11.0
            if move.recoil:
                score -= 10.0 * move.recoil
            if move.secondary in ("brn", "psn", "tox", "par", "slp") and opp.status is None:
                score += 9.0 * move.secondary_chance
            if move.knock_off and opp.item != "none":
                score += 8.0
            if move.secondary and move.secondary.endswith("_down") and opp.status is None:
                score += 4.0 * move.secondary_chance
            if move.switch:
                bench = [
                    p for i, p in enumerate(battle.sides[side].team) if i != battle.sides[side].active and not p.fainted
                ]
                if bench:
                    best = max(matchup_score(battle, p, opp) for p in bench)
                    score += 10.0 * (best - current_matchup)
            for _, delta, who in move.stat_changes:
                if who == "self" and delta < 0:
                    score -= 6.0 * abs(delta)
            scores.append(score)
            continue

        # Status / utility moves.
        score = 0.0
        if move.heal:
            if me.hp_fraction < 0.62:
                score += 85.0 * (1.0 - me.hp_fraction)
            else:
                score -= 18.0
        if move.protect:
            score += 22.0 if me.hp_fraction < 0.35 else -8.0
        if move.hazard:
            score += 38.0 if battle.sides[1 - side].hazards == 0 and battle.alive_count(1 - side) > 1 else -12.0
        if move.clear_hazards:
            score += 34.0 if battle.sides[side].hazards else -8.0
        if move.haze:
            score += 34.0 if _boost_total(opp) > 0 else -10.0
        if move.stat_changes and not move.hazard:
            positive = sum(delta for _, delta, who in move.stat_changes if who == "self" and delta > 0)
            negative = sum(delta for _, delta, who in move.stat_changes if who == "self" and delta < 0)
            if positive:
                if me.hp_fraction > 0.55 and opp.hp_fraction > 0.2:
                    score += 13.0 * positive
                else:
                    score -= 4.0
                if _boost_total(me) >= 8:
                    score -= 25.0
            score -= 7.0 * abs(negative)
        if move.secondary in ("brn", "psn", "tox", "par", "slp"):
            if opp.status is not None:
                score -= 15.0
            else:
                if move.secondary == "slp":
                    score += 62.0
                elif move.secondary == "tox":
                    score += 42.0 + 18.0 * opp.hp_fraction
                elif move.secondary == "brn":
                    score += 36.0 if opp.stats["atk"] >= opp.stats["spa"] else 22.0
                elif move.secondary == "par":
                    score += 32.0 if opp_speed > my_speed else 16.0
                elif move.secondary == "psn":
                    score += 20.0
        if move.switch and not move.is_damaging:
            bench = [
                p for i, p in enumerate(battle.sides[side].team) if i != battle.sides[side].active and not p.fainted
            ]
            if bench:
                best = max(matchup_score(battle, p, opp) for p in bench)
                score += 12.0 * (best - current_matchup)
        scores.append(score)
    return scores


class Agent:
    name = "agent"

    def act(self, battle: Battle, side: int, rng: RNG) -> Action:
        raise NotImplementedError

    def reset(self) -> None:
        pass


class RandomAgent(Agent):
    name = "Random"

    def act(self, battle: Battle, side: int, rng: RNG) -> Action:
        return rng.choice(battle.legal_actions(side))


class GreedyAgent(Agent):
    name = "Greedy"

    def act(self, battle: Battle, side: int, rng: RNG) -> Action:
        actions = battle.legal_actions(side)
        best = None
        best_score = -1.0
        for action in actions:
            if action.kind == "move" and action.index >= 0:
                move = battle.active(side).moves[action.index].move
                score = battle.estimate_damage_fraction(side, move) if move.is_damaging else 0.0
                score *= 1.0 if move.accuracy == 0 else move.accuracy / 100.0
            else:
                score = 0.0
            if score > best_score:
                best_score = score
                best = action
        assert best is not None
        return best


class HeuristicAgent(Agent):
    name = "Heuristic"

    def __init__(self, noise: float = 0.0) -> None:
        self.noise = noise

    def act(self, battle: Battle, side: int, rng: RNG) -> Action:
        actions = battle.legal_actions(side)
        scores = heuristic_scores(battle, side)
        if self.noise:
            scores = [s + rng.uniform(-self.noise, self.noise) for s in scores]
        best_idx = max(range(len(scores)), key=lambda i: (scores[i], -i))
        return actions[best_idx]


class SearchAgent(Agent):
    """Expectimax search with a heuristic opponent model.

    ``depth=1`` means: try each of my actions, let the opponent respond
    according to the heuristic distribution, evaluate the resulting position.
    ``depth=2`` adds one more ply and is substantially slower.
    """

    def __init__(self, depth: int = 1, branch_limit: int = 6, opponent_temperature: float = 18.0) -> None:
        self.depth = depth
        self.branch_limit = branch_limit
        self.opponent_temperature = opponent_temperature
        self.name = f"Search-{depth}"

    def _opponent_distribution(self, battle: Battle, side: int) -> tuple[list[Action], list[int], list[float]]:
        opp_actions = battle.legal_actions(1 - side)
        opp_scores = heuristic_scores(battle, 1 - side)
        order = sorted(range(len(opp_actions)), key=lambda i: -opp_scores[i])[: self.branch_limit]
        probs = softmax([opp_scores[i] for i in order], self.opponent_temperature)
        return opp_actions, order, probs

    def _value(self, battle: Battle, side: int, depth: int) -> float:
        if battle.done:
            return battle.rewards()[side]
        if depth <= 0:
            return heuristic_evaluation(battle, side)
        my_actions = battle.legal_actions(side)
        opp_actions, order, probs = self._opponent_distribution(battle, side)
        best = -1e9
        for action in my_actions:
            value = 0.0
            for idx, prob in zip(order, probs):
                child = battle.clone(for_search=True)
                if side == 0:
                    child.step(action, opp_actions[idx])
                else:
                    child.step(opp_actions[idx], action)
                value += prob * self._value(child, side, depth - 1)
            if value > best:
                best = value
        return best

    def action_values(self, battle: Battle, side: int) -> list[float]:
        actions = battle.legal_actions(side)
        if len(actions) == 1:
            return [1.0]
        opp_actions, order, probs = self._opponent_distribution(battle, side)
        return [self._value_action(battle, side, action, opp_actions, order, probs) for action in actions]

    def _value_action(
        self,
        battle: Battle,
        side: int,
        action: Action,
        opp_actions: list[Action] | None = None,
        order: list[int] | None = None,
        probs: list[float] | None = None,
    ) -> float:
        if opp_actions is None or order is None or probs is None:
            opp_actions, order, probs = self._opponent_distribution(battle, side)
        total = 0.0
        for idx, prob in zip(order, probs):
            child = battle.clone(for_search=True)
            if side == 0:
                child.step(action, opp_actions[idx])
            else:
                child.step(opp_actions[idx], action)
            total += prob * self._value(child, side, self.depth - 1)
        return total

    def act(self, battle: Battle, side: int, rng: RNG) -> Action:
        actions = battle.legal_actions(side)
        if len(actions) == 1:
            return actions[0]
        values = self.action_values(battle, side)
        tie = heuristic_scores(battle, side)
        best_idx = max(range(len(values)), key=lambda i: (values[i], tie[i], -i))
        return actions[best_idx]


class LinearPolicy:
    """A linear softmax policy over the shared feature map."""

    def __init__(self, weights: Sequence[float] | None = None, metadata: dict | None = None) -> None:
        self.weights = list(weights) if weights is not None else [0.0] * N_FEATURES
        if len(self.weights) != N_FEATURES:
            raise ValueError(f"expected {N_FEATURES} weights, got {len(self.weights)}")
        self.metadata = metadata or {}

    def logits(self, feats: Sequence[Sequence[float]]) -> list[float]:
        return [_dot(self.weights, row) for row in feats]

    def probabilities(self, feats: Sequence[Sequence[float]], temperature: float = 1.0) -> list[float]:
        return softmax(self.logits(feats), temperature)

    def act(self, battle: Battle, side: int, rng: RNG, *, sample: bool = False, temperature: float = 1.0) -> Action:
        actions, feats = feature_matrix(battle, side)
        if not actions:
            raise RuntimeError("no legal actions")
        if sample and temperature > 0:
            probs = self.probabilities(feats, temperature)
            roll = rng.random()
            acc = 0.0
            for action, prob in zip(actions, probs):
                acc += prob
                if roll <= acc:
                    return action
            return actions[-1]
        logits = self.logits(feats)
        return actions[max(range(len(actions)), key=lambda i: logits[i])]

    def save(self, path: str | Path) -> None:
        payload = {"version": 1, "n_features": N_FEATURES, "weights": self.weights, "metadata": self.metadata}
        Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> LinearPolicy:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(payload["weights"], payload.get("metadata", {}))


class PolicyAgent(Agent):
    def __init__(
        self, policy: LinearPolicy, name: str = "Policy", sample: bool = False, temperature: float = 1.0
    ) -> None:
        self.policy = policy
        self.name = name
        self.sample = sample
        self.temperature = temperature

    def act(self, battle: Battle, side: int, rng: RNG) -> Action:
        return self.policy.act(battle, side, rng, sample=self.sample, temperature=self.temperature)


class HybridAgent(Agent):
    """Use the learned policy as a prior, then search over its top actions."""

    def __init__(self, policy: LinearPolicy, depth: int = 1, top_k: int = 3) -> None:
        self.policy = policy
        self.search = SearchAgent(depth=depth)
        self.top_k = top_k
        self.name = f"Hybrid-{depth}"

    def act(self, battle: Battle, side: int, rng: RNG) -> Action:
        actions, feats = feature_matrix(battle, side)
        if len(actions) == 1:
            return actions[0]
        logits = self.policy.logits(feats)
        order = sorted(range(len(actions)), key=lambda i: -logits[i])[: self.top_k]
        best = actions[order[0]]
        best_value = -1e9
        for idx in order:
            value = self.search._value_action(battle, side, actions[idx])
            if value > best_value:
                best_value = value
                best = actions[idx]
        return best


class QAgent(Agent):
    """Tabular Q baseline; keys are stable reprs of the discretised state."""

    def __init__(self, q: dict[str, list[float]] | None = None, epsilon: float = 0.0) -> None:
        self.q = q or {}
        self.epsilon = epsilon
        self.name = "Tabular-Q"

    @staticmethod
    def _key(battle: Battle, side: int) -> str:
        return repr(state_key(battle, side))

    @staticmethod
    def _action_index(action: Action) -> int:
        return action.index if action.kind == "move" else 4 + action.index

    def values(self, battle: Battle, side: int) -> list[float]:
        return self.q.get(self._key(battle, side), [0.0] * 10)

    def act(self, battle: Battle, side: int, rng: RNG) -> Action:
        actions = battle.legal_actions(side)
        if self.epsilon and rng.random() < self.epsilon:
            return rng.choice(actions)
        values = self.values(battle, side)
        return max(actions, key=lambda a: values[self._action_index(a)])

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps({"version": 1, "q": self.q}, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> QAgent:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(payload["q"])


def agent_from_name(name: str, policy_path: str | Path | None = None) -> Agent:
    name = name.lower()
    if name == "random":
        return RandomAgent()
    if name == "greedy":
        return GreedyAgent()
    if name == "heuristic":
        return HeuristicAgent()
    if name.startswith("search"):
        depth = int(name.split("-")[1]) if "-" in name else 1
        return SearchAgent(depth=depth)
    if name in ("policy", "bc", "rl") and policy_path is not None:
        return PolicyAgent(LinearPolicy.load(policy_path), name=name.upper())
    if name.startswith("hybrid") and policy_path is not None:
        depth = int(name.split("-")[1]) if "-" in name else 1
        return HybridAgent(LinearPolicy.load(policy_path), depth=depth)
    raise ValueError(f"unknown agent: {name}")
