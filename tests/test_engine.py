from pokerl.agents import HeuristicAgent, RandomAgent, SearchAgent
from pokerl.dex import MOVES
from pokerl.engine import Action, Battle, make_pokemon, random_battle


def test_calculate_stats_level_100():
    garchomp = make_pokemon("garchomp")
    assert garchomp.max_hp == 357
    assert garchomp.stats["atk"] == 359
    assert garchomp.stats["spe"] == 333
    toxapex = make_pokemon("toxapex")
    assert toxapex.max_hp == 304
    assert toxapex.stats["def"] == 443


def test_ground_immunity():
    battle = Battle(["garchomp"], ["dragonite"], seed=1)
    assert battle.estimate_damage(0, "earthquake") == 0
    assert battle.estimate_damage(0, "dragon-claw") > 0


def test_ability_immunities():
    # Levitate: Gengar is immune to Ground even though Ghost/Poison is not.
    battle = Battle(["gengar"], ["garchomp"], seed=1)
    assert battle.estimate_damage(1, "earthquake") == 0
    # Flash Fire: Heatran absorbs Fire and powers up its own Fire moves.
    battle = Battle(["heatran"], ["garchomp"], seed=1)
    heatran = battle.active(0)
    assert battle.estimate_damage(1, "flamethrower") == 0
    assert battle._ability_immunity(battle.active(1), heatran, MOVES["flamethrower"])
    assert heatran.flash_fire is True
    # Storm Drain: Gastrodon absorbs Water and gains Special Attack.
    battle = Battle(["gastrodon"], ["rotom-wash"], seed=1)
    gastrodon = battle.active(0)
    before = gastrodon.boosts["spa"]
    assert battle._ability_immunity(battle.active(1), gastrodon, MOVES["hydro-pump"])
    assert gastrodon.boosts["spa"] == before + 1
    # Volt Absorb: Zeraora heals from Electric attacks.
    battle = Battle(["zeraora"], ["rotom-wash"], seed=1)
    zeraora = battle.active(0)
    zeraora.hp -= 100
    before = zeraora.hp
    assert battle._ability_immunity(battle.active(1), zeraora, MOVES["volt-switch"])
    assert zeraora.hp > before


def test_rapid_spin_clears_hazards_and_boosts_speed():
    battle = Battle(["excadrill", "skarmory"], ["blissey", "garchomp"], seed=1)
    battle.sides[0].hazards = 1
    excadrill = battle.active(0)
    before = excadrill.boosts["spe"]
    battle.step(Action("move", 2), Action("move", 0))
    assert battle.sides[0].hazards == 0
    assert excadrill.boosts["spe"] == before + 1


def test_status_immunities():
    battle = Battle(["heatran"], ["garchomp"], seed=1)
    heatran = battle.active(0)
    assert battle._apply_status(heatran, "brn", source_move=MOVES["will-o-wisp"]) is False
    garchomp = battle.active(1)
    assert battle._apply_status(garchomp, "par", source_move=MOVES["thunder-wave"]) is False


def test_stealth_rock_hits_switch_in():
    battle = Battle(["metagross", "skarmory"], ["garchomp", "volcarona"], seed=1)
    battle.sides[1].hazards = 1
    battle.sides[1].team[1].item = "none"  # bypass Heavy-Duty Boots to exercise the hazard
    battle._switch(1, 1)
    volcarona = battle.active(1)
    assert volcarona.hp < volcarona.max_hp
    assert volcarona.hp == volcarona.max_hp - volcarona.max_hp // 2


def test_focus_sash_survives_at_full_hp():
    battle = Battle(["alakazam"], ["garchomp"], seed=1)
    zam = battle.active(0)
    battle._apply_damage(battle.active(1), zam, 999, contact=False, move=MOVES["earthquake"])
    assert zam.hp == 1
    assert zam.item == "none"


def test_sturdy_survives_at_full_hp():
    battle = Battle(["skarmory"], ["garchomp"], seed=1)
    skarm = battle.active(0)
    battle._apply_damage(battle.active(1), skarm, 999, contact=False, move=MOVES["stone-edge"])
    assert skarm.hp == 1


def test_leftovers_heal():
    battle = Battle(["blissey"], ["garchomp"], seed=1)
    blissey = battle.active(0)
    blissey.hp -= 100
    before = blissey.hp
    battle._end_of_turn()
    assert blissey.hp > before


def test_choice_lock():
    battle = Battle(["scizor", "skarmory"], ["blissey", "garchomp"], seed=1)
    action = Action("move", 0)
    battle.step(action, Action("move", 0))
    legal = battle.legal_actions(0)
    moves = [a for a in legal if a.kind == "move"]
    assert len(moves) == 1
    assert moves[0].index == 0


def test_switch_clears_boosts_and_choice():
    battle = Battle(["scizor", "skarmory"], ["blissey", "garchomp"], seed=1)
    scizor = battle.active(0)
    scizor.boosts["atk"] = 2
    scizor.choice_locked = "bullet-punch"
    battle._switch(0, 1)
    assert scizor.boosts["atk"] == 0
    assert scizor.choice_locked is None


def test_battle_terminates_and_is_deterministic():
    for seed in range(10):
        b1 = random_battle(seed=seed)
        b2 = random_battle(seed=seed)
        w1 = b1.run(RandomAgent(), RandomAgent())
        w2 = b2.run(RandomAgent(), RandomAgent())
        assert w1 == w2
        assert b1.turn <= 100
        assert b1.log == b2.log


def test_agents_only_take_legal_actions():
    battle = random_battle(seed=99, team_size=3)
    agents = (SearchAgent(depth=1, branch_limit=2), HeuristicAgent())
    while not battle.done:
        a0 = agents[0].act(battle, 0, battle.rng)
        a1 = agents[1].act(battle, 1, battle.rng)
        assert a0 in battle.legal_actions(0)
        assert a1 in battle.legal_actions(1)
        battle.step(a0, a1)
        if battle.turn > 150:
            break


def test_view_shape():
    battle = random_battle(seed=4)
    view = battle.view(0)
    assert view.perspective == 0
    assert view.active.max_hp > 0
    assert len(view.legal_actions) >= 1
    assert len(view.bench) == 2
