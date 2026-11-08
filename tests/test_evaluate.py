from pokerl.agents import GreedyAgent, HeuristicAgent, RandomAgent
from pokerl.dex import ALL_SPECIES
from pokerl.evaluate import bootstrap_ci, bradley_terry, match, round_robin, speed_test


def test_bootstrap_ci_bounds():
    lo, hi = bootstrap_ci(7, 10, resamples=200, seed=1)
    assert 0.0 <= lo <= 0.7 <= hi <= 1.0


def test_match_counts_and_side_swap():
    result = match(HeuristicAgent(), RandomAgent(), 20, seed=3, pool=ALL_SPECIES)
    assert result["games"] == 20
    assert result["wins"] + result["losses"] + result["draws"] == 20
    assert 0.0 <= result["win_rate"] <= 1.0
    assert result["decisions_per_sec"] > 0


def test_bradley_terry_orders_dominant_agent():
    names = ["A", "B"]
    results = {(0, 1): {"wins": 10, "losses": 0, "draws": 0}}
    ratings = bradley_terry(names, results)
    assert ratings[0] > ratings[1]


def test_round_robin_small():
    result = round_robin([HeuristicAgent(), RandomAgent()], games_per_pair=10, seed=4, progress=False)
    assert len(result["standings"]) == 2
    assert result["standings"][0]["rating"] >= result["standings"][1]["rating"]
    assert len(result["matches"]) == 1


def test_speed_test():
    result = speed_test(GreedyAgent(), games=10, seed=5)
    assert result["games"] == 10
    assert result["decisions_per_sec"] > 0
