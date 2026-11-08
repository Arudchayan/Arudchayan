import math

from pokerl.engine import random_battle
from pokerl.features import FEATURE_NAMES, N_FEATURES, action_features, feature_matrix, state_key


def test_feature_length_is_consistent():
    assert len(FEATURE_NAMES) == N_FEATURES
    battle = random_battle(seed=3)
    actions, feats = feature_matrix(battle, 0)
    assert len(actions) == len(feats)
    assert all(len(row) == N_FEATURES for row in feats)
    assert all(math.isfinite(value) for row in feats for value in row)


def test_switch_features_are_present():
    battle = random_battle(seed=3)
    actions, feats = feature_matrix(battle, 0)
    switch_idx = next(i for i, action in enumerate(actions) if action.kind == "switch")
    row = feats[switch_idx]
    assert row[2] == 1.0
    assert any(value != 0.0 for value in row[45:51])


def test_state_key_is_hashable_and_stable():
    battle = random_battle(seed=5)
    key = state_key(battle, 0)
    assert isinstance(key, tuple)
    assert key == state_key(battle, 0)
    hash(key)


def test_action_features_accepts_precomputed_global():
    battle = random_battle(seed=6)
    actions, feats = feature_matrix(battle, 1)
    again = action_features(battle, 1, actions[0])
    assert again == feats[0]
