from pokerl.agents import (
    GreedyAgent,
    HeuristicAgent,
    HybridAgent,
    LinearPolicy,
    QAgent,
    RandomAgent,
    SearchAgent,
    heuristic_scores,
    softmax,
)
from pokerl.engine import random_battle
from pokerl.features import N_FEATURES
from pokerl.nn import MLPPolicy
from pokerl.rng import RNG


def test_basic_agents_return_legal_actions():
    battle = random_battle(seed=7)
    for agent in (RandomAgent(), GreedyAgent(), HeuristicAgent(), SearchAgent(depth=1, branch_limit=2)):
        action = agent.act(battle, 0, RNG(1))
        assert action in battle.legal_actions(0)


def test_heuristic_scores_align_with_actions():
    battle = random_battle(seed=8)
    actions = battle.legal_actions(0)
    scores = heuristic_scores(battle, 0)
    assert len(actions) == len(scores)
    assert all(isinstance(s, float) for s in scores)


def test_softmax():
    probs = softmax([1.0, 1.0, 1.0], 1.0)
    assert abs(sum(probs) - 1.0) < 1e-9
    assert all(abs(p - 1 / 3) < 1e-9 for p in probs)
    peaked = softmax([10.0, 0.0], 1.0)
    assert peaked[0] > peaked[1]


def test_linear_policy_roundtrip(tmp_path):
    policy = LinearPolicy([0.001 * i for i in range(N_FEATURES)])
    path = tmp_path / "policy.json"
    policy.save(path)
    loaded = LinearPolicy.load(path)
    assert loaded.weights == policy.weights
    battle = random_battle(seed=9)
    assert loaded.act(battle, 0, RNG(2)) in battle.legal_actions(0)


def test_q_agent_roundtrip(tmp_path):
    battle = random_battle(seed=10)
    key = repr(__import__("pokerl.features", fromlist=["state_key"]).state_key(battle, 0))
    q = {key: [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
    agent = QAgent(q)
    path = tmp_path / "q.json"
    agent.save(path)
    loaded = QAgent.load(path)
    assert loaded.q == q
    assert loaded.act(battle, 0, RNG(3)) in battle.legal_actions(0)


def test_mlp_policy_forward_and_roundtrip(tmp_path):
    # 2 -> 2 -> 1 with deliberately simple weights.
    weights = {
        "w1": [[1.0, 0.0], [0.0, 1.0]],
        "b1": [0.0, 0.0],
        "w2": [[1.0, 1.0]],
        "b2": [0.0],
        "w3": [1.0],
        "b3": [0.0],
    }
    policy = MLPPolicy(weights, {"test": True})
    assert policy.logits([[1.0, 2.0], [3.0, 4.0]]) == [3.0, 7.0]
    path = tmp_path / "mlp.json"
    policy.save(path)
    loaded = MLPPolicy.load(path)
    assert loaded.logits([[1.0, 2.0]]) == [3.0]


def test_hybrid_agent_runs_one_decision():
    battle = random_battle(seed=11)
    policy = LinearPolicy([0.0] * N_FEATURES)
    agent = HybridAgent(policy, depth=1, top_k=2)
    action = agent.act(battle, 0, RNG(4))
    assert action in battle.legal_actions(0)
