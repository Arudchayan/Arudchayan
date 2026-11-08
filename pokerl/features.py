"""Feature extraction for linear policies and value functions.

The feature map is intentionally hand-designed and small.  It is shared by
behaviour cloning, REINFORCE fine-tuning, and the tabular/linear baselines, so
every reported number uses exactly the same observation interface.
"""

from __future__ import annotations

from collections.abc import Iterable

from .engine import Action, Battle, Pokemon
from .types import TYPE_INDEX, TYPES, effectiveness

TYPE_FEATURES = 18

# Names are useful for debugging, ablation studies, and the paper appendix.
ACTION_FEATURE_NAMES: tuple[str, ...] = (
    (
        "bias",
        "is_move",
        "is_switch",
    )
    + tuple(f"type_{t}" for t in TYPES)
    + (
        "physical",
        "special",
        "status",
        "power",
        "accuracy",
        "priority",
        "contact",
        "recoil",
        "drain",
        "fixed_damage",
        "heal",
        "setup",
        "hazard",
        "clear_hazards",
        "protect",
        "switch_move",
        "stab",
        "effectiveness",
        "expected_damage",
        "can_ko",
        "self_boost",
        "foe_drop",
        "status_chance",
        "pp_fraction",
        "incoming_hp",
        "incoming_type_adv",
        "incoming_speed_adv",
        "incoming_regen",
        "incoming_natural_cure",
        "incoming_status",
    )
)

GLOBAL_FEATURE_NAMES: tuple[str, ...] = (
    (
        "own_hp",
        "opp_hp",
        "hp_diff",
        "own_alive",
        "opp_alive",
        "speed_adv",
        "own_boost",
        "opp_boost",
        "own_status",
        "opp_status",
        "own_hazards",
        "opp_hazards",
        "turn_fraction",
        "own_bench_hp",
        "opp_bench_hp",
        "own_type_adv",
        "opp_type_adv",
        "own_choice",
        "opp_choice",
        "own_regen",
        "opp_regen",
        "own_levitate",
        "opp_levitate",
    )
    + tuple(f"own_type_{t}" for t in TYPES)
    + tuple(f"opp_type_{t}" for t in TYPES)
    + (
        "own_atk",
        "own_def",
        "own_spa",
        "own_spd",
        "own_spe",
        "opp_atk",
        "opp_def",
        "opp_spa",
        "opp_spd",
        "opp_spe",
    )
    + tuple(f"own_status_{s}" for s in ("brn", "par", "psn", "tox", "slp"))
    + tuple(f"opp_status_{s}" for s in ("brn", "par", "psn", "tox", "slp"))
    + tuple(f"own_boost_{s}" for s in ("atk", "def", "spa", "spd", "spe"))
    + tuple(f"opp_boost_{s}" for s in ("atk", "def", "spa", "spd", "spe"))
    + tuple(f"own_item_{s}" for s in ("choice", "life_orb", "leftovers", "sash", "boots"))
    + tuple(f"opp_item_{s}" for s in ("choice", "life_orb", "leftovers", "sash", "boots"))
    + tuple(
        f"own_ability_{s}"
        for s in (
            "levitate",
            "multiscale",
            "technician",
            "magic_guard",
            "regenerator",
            "sturdy",
            "poison_heal",
            "intimidate",
        )
    )
    + tuple(
        f"opp_ability_{s}"
        for s in (
            "levitate",
            "multiscale",
            "technician",
            "magic_guard",
            "regenerator",
            "sturdy",
            "poison_heal",
            "intimidate",
        )
    )
    + (
        "opp_best_damage",
        "own_best_damage",
        "threat_ratio",
        "can_survive",
        "setup_safe",
    )
)

INTERACTION_NAMES: tuple[str, ...] = (
    "power_x_eff",
    "power_x_own_hp",
    "priority_x_speed_deficit",
    "heal_x_missing_hp",
    "setup_x_own_hp",
    "status_x_opp_clean",
    "hazard_x_missing_hazard",
    "switch_x_matchup_delta",
    "damage_x_opp_hp",
    "ko_x_opp_hp",
    "move_x_own_hp",
    "move_x_opp_hp",
    "eff_x_stab",
    "switch_x_incoming_hp",
    "protect_x_missing_hp",
    "protect_x_opp_clean",
    "status_x_missing_hp",
)

FEATURE_NAMES: tuple[str, ...] = ACTION_FEATURE_NAMES + GLOBAL_FEATURE_NAMES + INTERACTION_NAMES
N_FEATURES = len(FEATURE_NAMES)


def _types_effectiveness(move_type: str, defender: Iterable[str]) -> float:
    return effectiveness(move_type, defender)


def _best_effectiveness(attacker: Pokemon, defender: Pokemon) -> float:
    best = 0.0
    for slot in attacker.moves:
        move = slot.move
        if not move.is_damaging:
            continue
        mult = effectiveness(move.type, defender.types)
        if mult > best:
            best = mult
    return min(4.0, best) / 4.0


def _best_incoming_effectiveness(attacker: Pokemon, defender: Pokemon) -> float:
    """Best move effectiveness the *defender* can use against *attacker*."""
    return _best_effectiveness(defender, attacker)


def _status_flag(pokemon: Pokemon) -> float:
    return 1.0 if pokemon.status is not None else 0.0


def _boost_sum(pokemon: Pokemon) -> float:
    return sum(pokemon.boosts.values()) / 12.0


def _bench_hp(battle: Battle, side: int) -> float:
    team = battle.sides[side].team
    active = battle.sides[side].active
    others = [p for i, p in enumerate(team) if i != active]
    if not others:
        return 0.0
    return sum(p.hp_fraction for p in others) / len(others)


def _speed_advantage(
    battle: Battle, side: int, attacker: Pokemon | None = None, defender: Pokemon | None = None
) -> float:
    a = attacker if attacker is not None else battle.active(side)
    d = defender if defender is not None else battle.opponent(side)
    sa = battle.effective_speed(a)
    sd = battle.effective_speed(d)
    if sa + sd == 0:
        return 0.0
    return max(-1.0, min(1.0, (sa - sd) / (sa + sd)))


def _best_damage_fraction(battle: Battle, attacker: Pokemon, defender: Pokemon) -> float:
    best = 0.0
    for slot in attacker.moves:
        move = slot.move
        if not move.is_damaging:
            continue
        damage = battle._damage_formula(attacker, defender, move, crit=False, roll=0.925)
        accuracy = 1.0 if move.accuracy == 0 else move.accuracy / 100.0
        best = max(best, damage * accuracy)
    return min(1.5, best / max(1, defender.max_hp))


def _global_features(battle: Battle, side: int) -> list[float]:
    me = battle.active(side)
    opp = battle.opponent(side)
    own_damage = _best_damage_fraction(battle, me, opp)
    opp_damage = _best_damage_fraction(battle, opp, me)
    base = [
        me.hp_fraction,
        opp.hp_fraction,
        me.hp_fraction - opp.hp_fraction,
        battle.alive_count(side) / 3.0,
        battle.alive_count(1 - side) / 3.0,
        _speed_advantage(battle, side),
        _boost_sum(me),
        _boost_sum(opp),
        _status_flag(me),
        _status_flag(opp),
        float(battle.sides[side].hazards),
        float(battle.sides[1 - side].hazards),
        min(1.0, battle.turn / 100.0),
        _bench_hp(battle, side),
        _bench_hp(battle, 1 - side),
        _best_effectiveness(me, opp),
        _best_incoming_effectiveness(me, opp),
        1.0 if me.item in ("Choice Band", "Choice Specs", "Choice Scarf") else 0.0,
        1.0 if opp.item in ("Choice Band", "Choice Specs", "Choice Scarf") else 0.0,
        1.0 if me.ability == "Regenerator" else 0.0,
        1.0 if opp.ability == "Regenerator" else 0.0,
        1.0 if me.ability == "Levitate" else 0.0,
        1.0 if opp.ability == "Levitate" else 0.0,
    ]
    types = [0.0] * (2 * len(TYPES))
    for t in me.types:
        types[TYPE_INDEX[t]] = 1.0
    for t in opp.types:
        types[len(TYPES) + TYPE_INDEX[t]] = 1.0
    stats = [
        me.stats["atk"] / 200.0,
        me.stats["def"] / 200.0,
        me.stats["spa"] / 200.0,
        me.stats["spd"] / 200.0,
        me.stats["spe"] / 200.0,
        opp.stats["atk"] / 200.0,
        opp.stats["def"] / 200.0,
        opp.stats["spa"] / 200.0,
        opp.stats["spd"] / 200.0,
        opp.stats["spe"] / 200.0,
    ]
    statuses = []
    for status in ("brn", "par", "psn", "tox", "slp"):
        statuses.append(1.0 if me.status == status else 0.0)
    for status in ("brn", "par", "psn", "tox", "slp"):
        statuses.append(1.0 if opp.status == status else 0.0)
    boosts = [me.boosts[k] / 6.0 for k in ("atk", "def", "spa", "spd", "spe")]
    boosts += [opp.boosts[k] / 6.0 for k in ("atk", "def", "spa", "spd", "spe")]
    own_items = [
        1.0 if me.item in ("Choice Band", "Choice Specs", "Choice Scarf") else 0.0,
        1.0 if me.item == "Life Orb" else 0.0,
        1.0 if me.item == "Leftovers" else 0.0,
        1.0 if me.item == "Focus Sash" else 0.0,
        1.0 if me.item == "Heavy-Duty Boots" else 0.0,
    ]
    opp_items = [
        1.0 if opp.item in ("Choice Band", "Choice Specs", "Choice Scarf") else 0.0,
        1.0 if opp.item == "Life Orb" else 0.0,
        1.0 if opp.item == "Leftovers" else 0.0,
        1.0 if opp.item == "Focus Sash" else 0.0,
        1.0 if opp.item == "Heavy-Duty Boots" else 0.0,
    ]
    abilities = (
        "Levitate",
        "Multiscale",
        "Technician",
        "Magic Guard",
        "Regenerator",
        "Sturdy",
        "Poison Heal",
        "Intimidate",
    )
    own_abilities = [1.0 if me.ability == ability else 0.0 for ability in abilities]
    opp_abilities = [1.0 if opp.ability == ability else 0.0 for ability in abilities]
    threat = [
        opp_damage,
        own_damage,
        min(2.0, opp_damage / max(0.05, me.hp_fraction)),
        1.0 if opp_damage < me.hp_fraction else 0.0,
        1.0 if opp_damage < 0.35 else 0.0,
    ]
    return base + types + stats + statuses + boosts + own_items + opp_items + own_abilities + opp_abilities + threat


def _action_specific(
    battle: Battle,
    side: int,
    action: Action,
) -> list[float]:
    me = battle.active(side)
    opp = battle.opponent(side)
    vector = [0.0] * len(ACTION_FEATURE_NAMES)
    vector[0] = 1.0  # bias

    if action.kind == "move":
        vector[1] = 1.0
        if action.index == -1:
            move = None
            power = 50.0
            accuracy = 1.0
            priority = 0.0
            category = "physical"
            move_type = "normal"
            pp_fraction = 0.0
            self_boost = 0.0
            foe_drop = 0.0
            status_chance = 0.0
            contact = 1.0
            recoil = 0.25
            drain = 0.0
            fixed = 0.0
            heal = 0.0
            setup = 0.0
            hazard = 0.0
            clear = 0.0
            protect = 0.0
            switch_move = 0.0
            exp_damage = 0.0
            can_ko = 0.0
        else:
            if action.index < 0 or action.index >= len(me.moves):
                return vector
            slot = me.moves[action.index]
            move = slot.move
            power = float(move.power)
            accuracy = 1.0 if move.accuracy == 0 else move.accuracy / 100.0
            priority = move.priority / 2.0
            category = move.category
            move_type = move.type
            pp_fraction = slot.pp / max(1, move.pp)
            self_boost = sum(delta for _, delta, who in move.stat_changes if who == "self") / 4.0
            foe_drop = -sum(delta for _, delta, who in move.stat_changes if who == "foe") / 4.0
            status_chance = move.secondary_chance if move.secondary else 0.0
            contact = 1.0 if move.contact else 0.0
            recoil = move.recoil
            drain = move.drain
            fixed = 1.0 if move.fixed_damage else 0.0
            heal = 1.0 if move.heal else 0.0
            setup = 1.0 if (move.stat_changes and move.category == "status" and not move.secondary) else 0.0
            hazard = 1.0 if move.hazard else 0.0
            clear = 1.0 if move.clear_hazards else 0.0
            protect = 1.0 if move.protect else 0.0
            switch_move = 1.0 if move.switch else 0.0
            if move.is_damaging and move.id != "gyro-ball" or move.is_damaging:
                exp_damage = min(1.5, battle.estimate_damage_fraction(side, move))
            else:
                exp_damage = 0.0
            can_ko = 1.0 if exp_damage >= opp.hp_fraction and exp_damage > 0 else 0.0

        vector[3 + TYPE_INDEX[move_type]] = 1.0
        vector[21] = 1.0 if category == "physical" else 0.0
        vector[22] = 1.0 if category == "special" else 0.0
        vector[23] = 1.0 if category == "status" else 0.0
        vector[24] = min(1.0, power / 120.0)
        vector[25] = accuracy
        vector[26] = min(1.0, priority / 2.0)
        vector[27] = contact
        vector[28] = min(1.0, recoil)
        vector[29] = min(1.0, drain)
        vector[30] = fixed
        vector[31] = heal
        vector[32] = setup
        vector[33] = hazard
        vector[34] = clear
        vector[35] = protect
        vector[36] = switch_move
        vector[37] = 1.0 if move is not None and move.type in me.types else 0.0
        vector[38] = min(1.0, effectiveness(move_type, opp.types) / 4.0)
        vector[39] = exp_damage
        vector[40] = can_ko
        vector[41] = max(-1.0, min(1.0, self_boost))
        vector[42] = max(-1.0, min(1.0, foe_drop))
        vector[43] = status_chance
        vector[44] = pp_fraction
        # Incoming-switch features are only meaningful for switch actions.
        vector[45:51] = [0.0] * 6
    elif action.kind == "switch":
        vector[2] = 1.0
        team = battle.sides[side].team
        if action.index < 0 or action.index >= len(team):
            return vector
        incoming = team[action.index]
        vector[45] = incoming.hp_fraction
        vector[46] = _best_effectiveness(incoming, opp)
        vector[47] = max(-1.0, min(1.0, _speed_advantage(battle, side, incoming, opp)))
        vector[48] = 1.0 if incoming.ability == "Regenerator" else 0.0
        vector[49] = 1.0 if incoming.ability == "Natural Cure" else 0.0
        vector[50] = 1.0 if incoming.status is not None else 0.0
    return vector


def action_features(battle: Battle, side: int, action: Action, global_part: list[float] | None = None) -> list[float]:
    me = battle.active(side)
    opp = battle.opponent(side)
    action_part = _action_specific(battle, side, action)
    if global_part is None:
        global_part = _global_features(battle, side)
    power = action_part[24]
    eff = action_part[38]
    own_hp = me.hp_fraction
    opp_hp = opp.hp_fraction
    speed_deficit = 1.0 if battle.effective_speed(me) < battle.effective_speed(opp) else 0.0
    missing_hp = 1.0 - own_hp
    clean = 0.0 if opp.status is not None else 1.0
    missing_hazard = 1.0 if battle.sides[1 - side].hazards == 0 else 0.0
    matchup_delta = max(-1.0, min(1.0, action_part[46] - global_part[15])) if action.kind == "switch" else 0.0
    inter = [
        power * eff,
        power * own_hp,
        action_part[26] * speed_deficit,
        action_part[31] * missing_hp,
        action_part[32] * own_hp,
        action_part[43] * clean,
        action_part[33] * missing_hazard,
        matchup_delta,
        action_part[39] * opp_hp,
        action_part[40] * opp_hp,
        action_part[1] * own_hp,
        action_part[1] * opp_hp,
        eff * action_part[37],
        action_part[45] * action_part[2],
        action_part[35] * missing_hp,
        action_part[35] * clean,
        action_part[23] * missing_hp,
    ]
    return action_part + global_part + inter


def feature_matrix(battle: Battle, side: int) -> tuple[list[Action], list[list[float]]]:
    actions = battle.legal_actions(side)
    global_part = _global_features(battle, side)
    return actions, [action_features(battle, side, action, global_part) for action in actions]


def state_key(battle: Battle, side: int) -> tuple:
    """A compact discretisation for tabular baselines."""
    me = battle.active(side)
    opp = battle.opponent(side)
    bench = tuple(
        (p.species.id, min(5, int(p.hp_fraction * 6)))
        for i, p in enumerate(battle.sides[side].team)
        if i != battle.sides[side].active
    )
    return (
        me.species.id,
        min(5, int(me.hp_fraction * 6)),
        me.status or "-",
        tuple(me.boosts.values()),
        min(1, battle.sides[side].hazards),
        opp.species.id,
        min(5, int(opp.hp_fraction * 6)),
        opp.status or "-",
        tuple(opp.boosts.values()),
        min(1, battle.sides[1 - side].hazards),
        bench,
        tuple(
            (p.species.id, min(5, int(p.hp_fraction * 6)))
            for i, p in enumerate(battle.sides[1 - side].team)
            if i != battle.sides[1 - side].active
        ),
        battle.turn // 10,
    )
