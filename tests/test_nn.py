from pokerl.engine import random_battle
from pokerl.nn import MLPPolicy
from pokerl.rng import RNG


def test_mlp_act_is_legal():
    weights = {
        "w1": [[0.01 * i for i in range(8)]],
        "b1": [0.0],
        "w2": [[1.0]],
        "b2": [0.0],
        "w3": [1.0],
        "b3": [0.0],
    }
    # Use the real feature width by training a tiny valid shape via zeros.
    from pokerl.features import N_FEATURES

    weights = {
        "w1": [[0.0] * N_FEATURES, [0.0] * N_FEATURES],
        "b1": [0.0, 0.0],
        "w2": [[1.0, 1.0]],
        "b2": [0.0],
        "w3": [1.0],
        "b3": [0.0],
    }
    policy = MLPPolicy(weights, {})
    battle = random_battle(seed=13)
    action = policy.act(battle, 0, RNG(5))
    assert action in battle.legal_actions(0)
