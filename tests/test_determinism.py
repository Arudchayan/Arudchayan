from pokerl.agents import HeuristicAgent, RandomAgent, SearchAgent
from pokerl.engine import Battle, random_battle
from pokerl.rng import RNG


def test_full_battle_replay_is_byte_identical():
    logs = []
    for _ in range(2):
        battle = Battle(["garchomp", "skarmory", "rotom-wash"], ["dragonite", "heatran", "toxapex"], seed=77)
        agents = (SearchAgent(depth=1, branch_limit=2), HeuristicAgent())
        rngs = (RNG(1), RNG(2))
        while not battle.done:
            a0 = agents[0].act(battle, 0, rngs[0])
            a1 = agents[1].act(battle, 1, rngs[1])
            battle.step(a0, a1)
        logs.append((battle.winner, battle.turn, battle.log))
    assert logs[0] == logs[1]


def test_clone_does_not_mutate_parent():
    battle = random_battle(seed=12)
    snapshot = (battle.turn, battle.active(0).hp, battle.active(1).hp, battle.rng.state)
    clone = battle.clone(for_search=True)
    clone.step(clone.legal_actions(0)[0], clone.legal_actions(1)[0])
    assert (battle.turn, battle.active(0).hp, battle.active(1).hp, battle.rng.state) == snapshot


def test_seed_changes_outcome_space():
    outcomes = set()
    for seed in range(10):
        battle = random_battle(seed=seed)
        outcomes.add(battle.run(RandomAgent(), RandomAgent()))
    assert len(outcomes) >= 1
