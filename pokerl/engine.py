"""A fast, deterministic, singles battle simulator.

Scope (deliberately explicit, because scope is a feature):

* level 100, 1v1 or 3v3 singles;
* fixed competitive sets from :mod:`pokerl.dex`;
* 18 types, STAB, critical hits, accuracy, damage rolls;
* stat stages, burn / poison / toxic / paralysis / sleep;
* Leftovers, Life Orb, Choice items, Focus Sash, Heavy-Duty Boots, Toxic Orb;
* a small set of impactful abilities (Levitate, Intimidate, Multiscale, ...);
* Stealth Rock, Defog, Rapid Spin, U-turn / Volt Switch;
* no weather, terrain, Mega/Z/Dynamax, multi-hit, or items beyond the list.

Those omissions are intentional: the benchmark studies decision quality, not
teambuilding or dex completeness.  They are documented in ``paper/main.md``.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from .dex import (
    ALL_SPECIES,
    NATURES,
    SETS,
    STAT_KEYS,
    Move,
    PokemonSet,
    Species,
    get_move,
    get_species,
)
from .rng import RNG
from .types import effectiveness, stab

CHOICE_ITEMS = {"Choice Band", "Choice Specs", "Choice Scarf"}
HAZARD_ITEM_EXEMPT = {"Heavy-Duty Boots"}
MAX_TURNS = 100

STRUGGLE = Move(
    "struggle",
    "Struggle",
    "normal",
    "physical",
    50,
    0,
    1,
    recoil=0.25,
    contact=True,
)


def _stage_multiplier(stage: int) -> float:
    stage = max(-6, min(6, stage))
    if stage >= 0:
        return (2.0 + stage) / 2.0
    return 2.0 / (2.0 - stage)


def _nature_multiplier(nature: str, stat: str) -> float:
    up, down = NATURES[nature]
    if stat == up and stat != down:
        return 1.1
    if stat == down and stat != up:
        return 0.9
    return 1.0


def calculate_stats(species: Species, pset: PokemonSet, level: int = 100) -> dict[str, int]:
    stats: dict[str, int] = {}
    for stat in STAT_KEYS:
        base = species.base_stats[stat]
        ev = pset.evs.get(stat, 0)
        iv = 31
        if stat == "hp":
            value = (2 * base + iv + ev // 4) * level // 100 + level + 10
        else:
            value = (2 * base + iv + ev // 4) * level // 100 + 5
            value = int(value * _nature_multiplier(pset.nature, stat))
        stats[stat] = value
    return stats


@dataclass(slots=True)
class MoveSlot:
    move: Move
    pp: int

    def clone(self) -> MoveSlot:
        return MoveSlot(self.move, self.pp)


@dataclass(slots=True)
class Pokemon:
    species: Species
    pset: PokemonSet
    level: int
    stats: dict[str, int]
    moves: list[MoveSlot]
    max_hp: int
    hp: int
    ability: str
    item: str
    boosts: dict[str, int] = field(default_factory=lambda: {k: 0 for k in ("atk", "def", "spa", "spd", "spe")})
    status: str | None = None
    status_counter: int = 0
    toxic_counter: int = 0
    choice_locked: str | None = None
    protected: bool = False
    sash_used: bool = False
    flash_fire: bool = False
    fainted: bool = False
    last_move: str | None = None

    @property
    def name(self) -> str:
        return self.species.name

    @property
    def types(self) -> tuple[str, ...]:
        return self.species.types

    @property
    def hp_fraction(self) -> float:
        return 0.0 if self.max_hp <= 0 else self.hp / self.max_hp

    def clone(self) -> Pokemon:
        return Pokemon(
            species=self.species,
            pset=self.pset,
            level=self.level,
            stats=dict(self.stats),
            moves=[slot.clone() for slot in self.moves],
            max_hp=self.max_hp,
            hp=self.hp,
            ability=self.ability,
            item=self.item,
            boosts=dict(self.boosts),
            status=self.status,
            status_counter=self.status_counter,
            toxic_counter=self.toxic_counter,
            choice_locked=self.choice_locked,
            protected=self.protected,
            sash_used=self.sash_used,
            flash_fire=self.flash_fire,
            fainted=self.fainted,
            last_move=self.last_move,
        )

    def pp_of(self, move_id: str) -> int:
        for slot in self.moves:
            if slot.move.id == move_id:
                return slot.pp
        return 0


def make_pokemon(species_or_set: str | PokemonSet, level: int = 100) -> Pokemon:
    pset = SETS[species_or_set] if isinstance(species_or_set, str) else species_or_set
    species = get_species(pset.species)
    stats = calculate_stats(species, pset, level)
    return Pokemon(
        species=species,
        pset=pset,
        level=level,
        stats=stats,
        moves=[MoveSlot(get_move(mid), get_move(mid).pp) for mid in pset.moves],
        max_hp=stats["hp"],
        hp=stats["hp"],
        ability=pset.ability,
        item=pset.item,
    )


@dataclass(slots=True)
class Side:
    team: list[Pokemon]
    active: int = 0
    hazards: int = 0

    @property
    def active_pokemon(self) -> Pokemon:
        return self.team[self.active]

    def alive_indices(self) -> list[int]:
        return [i for i, p in enumerate(self.team) if not p.fainted]

    def alive_count(self) -> int:
        return sum(1 for p in self.team if not p.fainted)

    def hp_fraction(self) -> float:
        total = sum(p.max_hp for p in self.team)
        if total <= 0:
            return 0.0
        return sum(p.hp for p in self.team) / total

    def clone(self) -> Side:
        return Side([p.clone() for p in self.team], self.active, self.hazards)


@dataclass(frozen=True, slots=True)
class Action:
    kind: str  # "move" | "switch"
    index: int
    label: str = ""

    def __post_init__(self) -> None:
        if self.kind not in ("move", "switch"):
            raise ValueError(f"invalid action kind: {self.kind}")


@dataclass(frozen=True, slots=True)
class PokemonView:
    species: str
    name: str
    types: tuple[str, ...]
    hp: int
    max_hp: int
    hp_fraction: float
    status: str | None
    boosts: tuple[int, ...]
    item: str
    ability: str
    moves: tuple[str, ...]
    pp: tuple[int, ...]
    choice_locked: str | None
    fainted: bool
    level: int


@dataclass(frozen=True, slots=True)
class BattleView:
    perspective: int
    turn: int
    active: PokemonView
    opponent: PokemonView
    bench: tuple[PokemonView, ...]
    opponent_bench: tuple[PokemonView, ...]
    hazards: tuple[int, int]
    legal_actions: tuple[Action, ...]
    winner: int | None


@dataclass(frozen=True, slots=True)
class StepResult:
    views: tuple[BattleView, BattleView]
    rewards: tuple[float, float]
    done: bool
    info: dict


def _view(pokemon: Pokemon) -> PokemonView:
    return PokemonView(
        species=pokemon.species.id,
        name=pokemon.species.name,
        types=pokemon.types,
        hp=pokemon.hp,
        max_hp=pokemon.max_hp,
        hp_fraction=pokemon.hp_fraction,
        status=pokemon.status,
        boosts=tuple(pokemon.boosts[k] for k in ("atk", "def", "spa", "spd", "spe")),
        item=pokemon.item,
        ability=pokemon.ability,
        moves=tuple(slot.move.id for slot in pokemon.moves),
        pp=tuple(slot.pp for slot in pokemon.moves),
        choice_locked=pokemon.choice_locked,
        fainted=pokemon.fainted,
        level=pokemon.level,
    )


class Battle:
    """A two-player, turn-based singles battle."""

    __slots__ = ("sides", "rng", "turn", "winner", "log_enabled", "log", "_last_actions")

    def __init__(
        self,
        team0: Sequence[str | PokemonSet],
        team1: Sequence[str | PokemonSet],
        seed: int = 0,
        *,
        log: bool = True,
        max_team_size: int = 6,
    ) -> None:
        if not team0 or not team1:
            raise ValueError("both teams need at least one Pokémon")
        if len(team0) > max_team_size or len(team1) > max_team_size:
            raise ValueError("team too large")
        self.sides = (
            Side([make_pokemon(x) for x in team0]),
            Side([make_pokemon(x) for x in team1]),
        )
        self.rng = RNG(seed)
        self.turn = 0
        self.winner: int | None = None
        self.log_enabled = log
        self.log: list[str] = []
        self._last_actions: tuple[Action | None, Action | None] = (None, None)
        self._entry_effects(0)
        self._entry_effects(1)

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def done(self) -> bool:
        return self.winner is not None

    def active(self, side: int) -> Pokemon:
        return self.sides[side].active_pokemon

    def opponent(self, side: int) -> Pokemon:
        return self.sides[1 - side].active_pokemon

    def alive_count(self, side: int) -> int:
        return self.sides[side].alive_count()

    def legal_actions(self, side: int) -> list[Action]:
        if self.done:
            return []
        me = self.active(side)
        if me.fainted:
            return [
                Action("switch", i, f"Switch {self.sides[side].team[i].name}")
                for i in self.sides[side].alive_indices()
                if i != self.sides[side].active
            ]
        actions: list[Action] = []
        if me.choice_locked:
            slot = next((s for s in me.moves if s.move.id == me.choice_locked), None)
            if slot is not None and slot.pp > 0:
                actions.append(Action("move", me.moves.index(slot), f"{slot.move.name} ({slot.pp} PP)"))
        else:
            for i, slot in enumerate(me.moves):
                if slot.pp > 0:
                    actions.append(Action("move", i, f"{slot.move.name} ({slot.pp} PP)"))
        if not actions:
            actions.append(Action("move", -1, "Struggle"))
        for i in self.sides[side].alive_indices():
            if i != self.sides[side].active:
                actions.append(Action("switch", i, f"Switch {self.sides[side].team[i].name}"))
        return actions

    def view(self, side: int) -> BattleView:
        me_side = self.sides[side]
        opp_side = self.sides[1 - side]
        me = me_side.active_pokemon
        opp = opp_side.active_pokemon
        bench = tuple(_view(p) for i, p in enumerate(me_side.team) if i != me_side.active)
        opp_bench = tuple(_view(p) for i, p in enumerate(opp_side.team) if i != opp_side.active)
        return BattleView(
            perspective=side,
            turn=self.turn,
            active=_view(me),
            opponent=_view(opp),
            bench=bench,
            opponent_bench=opp_bench,
            hazards=(me_side.hazards, opp_side.hazards),
            legal_actions=tuple(self.legal_actions(side)),
            winner=self.winner,
        )

    def clone(self, *, for_search: bool = False) -> Battle:
        other = Battle.__new__(Battle)
        other.sides = (self.sides[0].clone(), self.sides[1].clone())
        other.rng = self.rng.clone()
        other.turn = self.turn
        other.winner = self.winner
        other.log_enabled = False if for_search else self.log_enabled
        other.log = [] if for_search else list(self.log)
        other._last_actions = self._last_actions
        return other

    def rewards(self) -> tuple[float, float]:
        if self.winner is None:
            return (0.0, 0.0)
        if self.winner == -1:
            return (0.0, 0.0)
        return (1.0, -1.0) if self.winner == 0 else (-1.0, 1.0)

    # ------------------------------------------------------------------
    # Stats / damage
    # ------------------------------------------------------------------

    def effective_speed(self, pokemon: Pokemon) -> int:
        value = pokemon.stats["spe"] * _stage_multiplier(pokemon.boosts["spe"])
        if pokemon.item == "Choice Scarf":
            value *= 1.5
        if pokemon.status == "par":
            value *= 0.5
        return max(1, int(value))

    def _effective_attack(self, pokemon: Pokemon, stat: str, crit: bool = False) -> float:
        stage = pokemon.boosts[stat]
        if crit:
            stage = max(0, stage)
        value = pokemon.stats[stat] * _stage_multiplier(stage)
        if stat == "atk" and pokemon.item == "Choice Band":
            value *= 1.5
        if stat == "spa" and pokemon.item == "Choice Specs":
            value *= 1.5
        if stat == "atk" and pokemon.status == "brn":
            value *= 0.5
        return max(1.0, value)

    def _effective_defense(self, pokemon: Pokemon, stat: str, crit: bool = False) -> float:
        stage = pokemon.boosts[stat]
        if crit:
            stage = min(0, stage)
        value = pokemon.stats[stat] * _stage_multiplier(stage)
        return max(1.0, value)

    def _ability_active(self, attacker: Pokemon, defender: Pokemon, ability: str) -> bool:
        return defender.ability == ability and attacker.ability != "Mold Breaker"

    def _damage_formula(
        self,
        attacker: Pokemon,
        defender: Pokemon,
        move: Move,
        *,
        crit: bool,
        roll: float,
    ) -> int:
        if attacker.ability != "Mold Breaker":
            if move.type == "ground" and defender.ability == "Levitate":
                return 0
            if move.type == "fire" and defender.ability == "Flash Fire":
                return 0
            if move.type == "water" and defender.ability == "Storm Drain":
                return 0
            if move.type == "electric" and defender.ability == "Volt Absorb":
                return 0
        if move.fixed_damage:
            if effectiveness(move.type, defender.types) == 0:
                return 0
            return move.fixed_damage

        power = move.power
        if move.gyro:
            atk_spe = max(1, self.effective_speed(attacker))
            def_spe = max(1, self.effective_speed(defender))
            power = max(1, min(150, int(25 * def_spe / atk_spe)))
        if power <= 0:
            return 0

        phys = move.category == "physical"
        if move.psyshock:
            attack = self._effective_attack(attacker, "spa", crit)
            defense = self._effective_defense(defender, "def", crit)
        elif phys:
            attack = self._effective_attack(attacker, "atk", crit)
            defense = self._effective_defense(defender, "def", crit)
        else:
            attack = self._effective_attack(attacker, "spa", crit)
            defense = self._effective_defense(defender, "spd", crit)

        base = ((2.0 * attacker.level / 5.0 + 2.0) * power * attack / defense) / 50.0 + 2.0
        if move.type in attacker.types:
            base *= stab(move.type, attacker.types)
        type_mult = effectiveness(move.type, defender.types)
        if type_mult == 0:
            return 0
        base *= type_mult
        if crit:
            base *= 1.5
        if attacker.item == "Life Orb":
            base *= 1.3
        if attacker.ability == "Technician" and power <= 60:
            base *= 1.5
        if attacker.flash_fire and move.type == "fire":
            base *= 1.5
        if move.knock_off and defender.item and defender.item != "none":
            base *= 1.5
        if self._ability_active(attacker, defender, "Multiscale") and defender.hp == defender.max_hp:
            base *= 0.5
        if self._ability_active(attacker, defender, "Thick Fat") and move.type in ("fire", "ice"):
            base *= 0.5
        if self._ability_active(attacker, defender, "Solid Rock"):
            base *= 0.75
        base *= roll
        return max(1, int(base))

    def estimate_damage(self, side: int, move_or_id: Move | str, *, crit: bool = False) -> int:
        """Average-roll damage estimate, useful for heuristic agents."""
        attacker = self.active(side)
        defender = self.opponent(side)
        move = get_move(move_or_id) if isinstance(move_or_id, str) else move_or_id
        return self._damage_formula(attacker, defender, move, crit=crit, roll=0.925)

    def estimate_damage_fraction(self, side: int, move_or_id: Move | str) -> float:
        defender = self.opponent(side)
        if defender.max_hp <= 0:
            return 0.0
        return self.estimate_damage(side, move_or_id) / defender.max_hp

    # ------------------------------------------------------------------
    # Effects
    # ------------------------------------------------------------------

    def _log(self, message: str) -> None:
        if self.log_enabled and len(self.log) < 4000:
            self.log.append(message)

    def _faint(self, pokemon: Pokemon) -> None:
        if not pokemon.fainted:
            pokemon.fainted = True
            pokemon.hp = 0
            self._log(f"{pokemon.name} fainted!")

    def _apply_stat_changes(
        self,
        source: Pokemon,
        target: Pokemon,
        changes: Iterable[tuple[str, int, str]],
        *,
        from_foe: bool = False,
    ) -> None:
        for stat, delta, who in changes:
            recipient = source if who == "self" else target
            if recipient.fainted:
                continue
            if delta < 0 and from_foe and recipient.ability == "Clear Body" and source.ability != "Mold Breaker":
                self._log(f"{recipient.name}'s Clear Body prevents the stat drop!")
                continue
            old = recipient.boosts[stat]
            new = max(-6, min(6, old + delta))
            if new == old:
                continue
            recipient.boosts[stat] = new
            word = "rose" if delta > 0 else "fell"
            amount = "sharply " if abs(delta) >= 2 else ""
            self._log(f"{recipient.name}'s {stat.upper()} {amount}{word}!")

    def _ability_immunity(self, attacker: Pokemon, defender: Pokemon, move: Move) -> bool:
        if not move.is_damaging or attacker.ability == "Mold Breaker":
            return False
        if move.type == "ground" and defender.ability == "Levitate":
            self._log(f"{defender.name} is immune to Ground moves thanks to Levitate!")
            return True
        if move.type == "fire" and defender.ability == "Flash Fire":
            defender.flash_fire = True
            self._log(f"{defender.name}'s Flash Fire absorbed the attack!")
            return True
        if move.type == "water" and defender.ability == "Storm Drain":
            self._apply_stat_changes(defender, defender, (("spa", 1, "self"),))
            self._log(f"{defender.name}'s Storm Drain absorbed the attack!")
            return True
        if move.type == "electric" and defender.ability == "Volt Absorb":
            healed = self._heal(defender, 1 / 4)
            self._log(f"{defender.name}'s Volt Absorb restored {healed} HP!")
            return True
        return False

    def _apply_status(self, target: Pokemon, status: str, *, source_move: Move | None = None) -> bool:
        status = {"toxic": "tox", "poison": "psn", "burn": "brn", "para": "par", "sleep": "slp"}.get(status, status)
        if target.fainted or target.status is not None:
            return False
        if status == "brn" and "fire" in target.types:
            return False
        if status in ("psn", "tox") and ("poison" in target.types or "steel" in target.types):
            return False
        if status == "par" and source_move is not None and source_move.type == "electric" and "ground" in target.types:
            return False
        if (
            status == "par"
            and source_move is not None
            and source_move.type == "electric"
            and "electric" in target.types
        ):
            return False
        if (
            status == "slp"
            and source_move is not None
            and source_move.id in ("spore", "sleep-powder")
            and "grass" in target.types
        ):
            return False
        if status == "slp" and target.ability == "Sweet Veil":
            return False
        if status == "brn" and target.ability == "Water Veil":
            return False
        target.status = status
        target.status_counter = self.rng.randint(1, 3) if status == "slp" else 0
        target.toxic_counter = 1 if status == "tox" else 0
        label = {
            "brn": "burned",
            "psn": "poisoned",
            "tox": "badly poisoned",
            "par": "paralyzed",
            "slp": "put to sleep",
        }[status]
        self._log(f"{target.name} was {label}!")
        return True

    def _entry_effects(self, side: int) -> None:
        me = self.active(side)
        opp = self.opponent(side)
        if me.fainted:
            return
        hazards = self.sides[side].hazards
        if hazards and me.item not in HAZARD_ITEM_EXEMPT and me.ability != "Magic Guard":
            mult = effectiveness("rock", me.types)
            if mult > 0:
                damage = max(1, int(me.max_hp * mult / 8))
                self._log(f"Stealth Rock hit {me.name} for {damage} damage!")
                self._apply_damage(None, me, damage, contact=False, move=None)
        if me.ability == "Intimidate" and not me.fainted and not opp.fainted:
            if opp.ability == "Clear Body":
                self._log(f"{opp.name}'s Clear Body blocks Intimidate!")
            else:
                self._apply_stat_changes(me, opp, (("atk", -1, "foe"),), from_foe=True)

    def _apply_damage(
        self,
        source: Pokemon | None,
        target: Pokemon,
        amount: int,
        *,
        contact: bool,
        move: Move | None,
    ) -> int:
        if target.fainted or amount <= 0:
            return 0
        if amount >= target.hp and target.hp == target.max_hp:
            if target.ability == "Sturdy" and (source is None or source.ability != "Mold Breaker"):
                amount = target.hp - 1
                self._log(f"{target.name} Sturdy survived the hit!")
            elif target.item == "Focus Sash" and not target.sash_used:
                amount = target.hp - 1
                target.sash_used = True
                target.item = "none"
                self._log(f"{target.name}'s Focus Sash activated!")
        amount = max(0, min(amount, target.hp))
        target.hp -= amount
        if target.hp <= 0:
            self._faint(target)
        if contact and source is not None and not source.fainted and move is not None:
            if target.ability in ("Rough Skin", "Iron Barbs") and source.ability != "Magic Guard":
                recoil = max(1, source.max_hp // 8)
                self._log(f"{target.name}'s {target.ability} hurt {source.name}!")
                self._apply_damage(None, source, recoil, contact=False, move=None)
            if target.ability == "Flame Body" and self.rng.chance(0.30):
                self._apply_status(source, "brn", source_move=move)
        return amount

    def _heal(self, pokemon: Pokemon, fraction: float) -> int:
        if pokemon.fainted:
            return 0
        amount = min(pokemon.max_hp - pokemon.hp, max(1, int(pokemon.max_hp * fraction)))
        if amount <= 0:
            return 0
        pokemon.hp += amount
        return amount

    def _switch(self, side: int, target_index: int) -> None:
        team = self.sides[side].team
        if target_index == self.sides[side].active or team[target_index].fainted:
            return
        outgoing = self.active(side)
        if outgoing.ability == "Regenerator" and not outgoing.fainted:
            healed = self._heal(outgoing, 1 / 3)
            if healed:
                self._log(f"{outgoing.name} regenerated {healed} HP!")
        if outgoing.ability == "Natural Cure":
            outgoing.status = None
            outgoing.status_counter = 0
            outgoing.toxic_counter = 0
        outgoing.choice_locked = None
        outgoing.toxic_counter = 0
        outgoing.boosts = {k: 0 for k in outgoing.boosts}
        outgoing.protected = False
        self.sides[side].active = target_index
        incoming = self.active(side)
        self._log(f"{incoming.name} was sent out!")
        self._entry_effects(side)

    def _handle_faints(self) -> None:
        for side in (0, 1):
            guard = 0
            while self.sides[side].alive_count() > 0 and self.active(side).fainted and guard < 10:
                guard += 1
                replacement = self.sides[side].alive_indices()[0]
                self.sides[side].active = replacement
                incoming = self.active(side)
                self._log(f"{incoming.name} was sent out!")
                self._entry_effects(side)
        self._check_winner()

    def _check_winner(self) -> None:
        if self.winner is not None:
            return
        alive0 = self.sides[0].alive_count()
        alive1 = self.sides[1].alive_count()
        if alive0 == 0 and alive1 == 0:
            self.winner = -1
        elif alive0 == 0:
            self.winner = 1
        elif alive1 == 0:
            self.winner = 0
        elif self.turn >= MAX_TURNS:
            hp0 = self.sides[0].hp_fraction()
            hp1 = self.sides[1].hp_fraction()
            if abs(hp0 - hp1) < 1e-9:
                self.winner = -1
            else:
                self.winner = 0 if hp0 > hp1 else 1

    # ------------------------------------------------------------------
    # Move execution
    # ------------------------------------------------------------------

    def _can_move(self, pokemon: Pokemon) -> bool:
        if pokemon.fainted:
            return False
        if pokemon.status == "slp":
            if pokemon.status_counter > 0:
                pokemon.status_counter -= 1
                self._log(f"{pokemon.name} is fast asleep.")
                return False
            pokemon.status = None
            self._log(f"{pokemon.name} woke up!")
        if pokemon.status == "par" and self.rng.chance(0.25):
            self._log(f"{pokemon.name} is fully paralyzed!")
            return False
        return True

    def _use_move(self, side: int, action: Action, opponent_action: Action) -> None:
        attacker = self.active(side)
        defender = self.opponent(side)
        if attacker.fainted or defender.fainted:
            return
        if not self._can_move(attacker):
            return

        if action.index == -1:
            move = STRUGGLE
            slot = None
        else:
            if action.index < 0 or action.index >= len(attacker.moves):
                return
            slot = attacker.moves[action.index]
            move = slot.move
            if slot.pp <= 0:
                return
            slot.pp -= 1
        attacker.last_move = move.id

        if move.sucker:
            targets_attack = opponent_action.kind == "move" and opponent_action.index >= 0
            if targets_attack:
                target_move = defender.moves[opponent_action.index].move
                targets_attack = target_move.is_damaging
            if not targets_attack:
                self._log(f"{move.name} failed!")
                return

        if defender.protected and (move.is_damaging or (move.secondary is not None and move.category == "status")):
            self._log(f"{defender.name} protected itself!")
            return

        if move.accuracy and self.rng.random() >= move.accuracy / 100.0:
            self._log(f"{attacker.name}'s {move.name} missed!")
            return

        if self._ability_immunity(attacker, defender, move):
            if attacker.item in CHOICE_ITEMS:
                attacker.choice_locked = move.id
            return

        if move.protect:
            attacker.protected = True
            if attacker.item in CHOICE_ITEMS:
                attacker.choice_locked = move.id
            self._log(f"{attacker.name} protected itself!")
            return

        if move.hazard:
            if self.sides[1 - side].hazards == 0:
                self.sides[1 - side].hazards = 1
                self._log(f"Stealth Rock was set on {self.sides[1 - side].active_pokemon.name}'s side!")
            else:
                self._log("But it failed!")
            if attacker.item in CHOICE_ITEMS:
                attacker.choice_locked = move.id
            return

        if move.clear_hazards and move.category == "status":
            if move.id == "defog":
                self.sides[0].hazards = 0
                self.sides[1].hazards = 0
                self._log("The field was cleared of hazards!")
            else:
                self.sides[side].hazards = 0
                self._log(f"{attacker.name} cleared hazards on its side!")
                self._apply_stat_changes(attacker, attacker, (("spe", 1, "self"),))
            if attacker.item in CHOICE_ITEMS:
                attacker.choice_locked = move.id
            return

        if move.haze:
            for p in (attacker, defender):
                p.boosts = {k: 0 for k in p.boosts}
            self._log("All stat changes were eliminated!")
            if attacker.item in CHOICE_ITEMS:
                attacker.choice_locked = move.id
            return

        if move.heal:
            healed = self._heal(attacker, move.heal / 100.0)
            if healed:
                self._log(f"{attacker.name} restored {healed} HP!")
            else:
                self._log("But it failed!")
            if attacker.item in CHOICE_ITEMS:
                attacker.choice_locked = move.id
            return

        if move.stat_changes and move.category == "status":
            self._apply_stat_changes(attacker, defender, move.stat_changes, from_foe=False)
            if move.secondary and self.rng.chance(move.secondary_chance):
                self._apply_status(defender, move.secondary, source_move=move)
            if attacker.item in CHOICE_ITEMS:
                attacker.choice_locked = move.id
            return

        if not move.is_damaging:
            if move.secondary and self.rng.chance(move.secondary_chance):
                self._apply_status(defender, move.secondary, source_move=move)
            if attacker.item in CHOICE_ITEMS:
                attacker.choice_locked = move.id
            return

        # Damaging move.
        crit = self.rng.chance(1 / 24)
        roll = self.rng.uniform(0.85, 1.0)
        damage = self._damage_formula(attacker, defender, move, crit=crit, roll=roll)
        type_mult = effectiveness(move.type, defender.types)
        if type_mult == 0:
            self._log(f"It doesn't affect {defender.name}...")
            if attacker.item in CHOICE_ITEMS:
                attacker.choice_locked = move.id
            return
        if crit:
            self._log("A critical hit!")
        if type_mult > 1:
            self._log("It's super effective!")
        elif type_mult < 1:
            self._log("It's not very effective...")
        dealt = self._apply_damage(attacker, defender, damage, contact=move.contact, move=move)
        if move.knock_off and defender.item != "none":
            removed = defender.item
            defender.item = "none"
            self._log(f"{attacker.name} knocked off {defender.name}'s {removed}!")
        if move.drain and dealt > 0 and not attacker.fainted:
            healed = self._heal(attacker, move.drain)
            if healed:
                self._log(f"{attacker.name} drained {healed} HP!")
        if move.recoil and dealt > 0 and not attacker.fainted and attacker.ability != "Magic Guard":
            recoil = max(1, int(dealt * move.recoil))
            self._log(f"{attacker.name} was damaged by recoil!")
            self._apply_damage(None, attacker, recoil, contact=False, move=None)
        if attacker.item == "Life Orb" and dealt > 0 and not attacker.fainted and attacker.ability != "Magic Guard":
            recoil = max(1, attacker.max_hp // 10)
            self._log(f"{attacker.name} lost some HP to Life Orb!")
            self._apply_damage(None, attacker, recoil, contact=False, move=None)
        if move.secondary and self.rng.chance(move.secondary_chance):
            if move.secondary in ("brn", "psn", "tox", "par", "slp"):
                self._apply_status(defender, move.secondary, source_move=move)
            elif move.secondary.endswith("_down") and not defender.fainted:
                stat = move.secondary[:-5]
                self._apply_stat_changes(attacker, defender, ((stat, -1, "foe"),), from_foe=True)
            elif move.secondary.endswith("_up") and not attacker.fainted:
                stat = move.secondary[:-3]
                self._apply_stat_changes(attacker, attacker, ((stat, 1, "self"),), from_foe=False)
        if move.clear_hazards:
            self.sides[side].hazards = 0
            self._log(f"{attacker.name} cleared hazards on its side!")
            self._apply_stat_changes(attacker, attacker, (("spe", 1, "self"),))
        if move.stat_changes and not attacker.fainted:
            self._apply_stat_changes(attacker, defender, move.stat_changes, from_foe=False)
        if attacker.item in CHOICE_ITEMS:
            attacker.choice_locked = move.id
        if move.switch and not attacker.fainted and self.sides[side].alive_count() > 1:
            candidates = [i for i in self.sides[side].alive_indices() if i != self.sides[side].active]
            if candidates:
                self._switch(side, candidates[0])

    # ------------------------------------------------------------------
    # Turn resolution
    # ------------------------------------------------------------------

    def _validate_action(self, side: int, action: Action) -> None:
        if not any(a.kind == action.kind and a.index == action.index for a in self.legal_actions(side)):
            raise ValueError(f"illegal action for side {side}: {action}")

    def _end_of_turn(self) -> None:
        for side in (0, 1):
            pokemon = self.active(side)
            if pokemon.fainted:
                continue
            if pokemon.item == "Leftovers":
                healed = self._heal(pokemon, 1 / 16)
                if healed:
                    self._log(f"{pokemon.name} restored a little HP with Leftovers!")
            if pokemon.item == "Toxic Orb" and pokemon.status is None:
                self._apply_status(pokemon, "tox")
            if pokemon.status == "brn" and pokemon.ability != "Magic Guard":
                self._apply_damage(None, pokemon, max(1, pokemon.max_hp // 16), contact=False, move=None)
                if pokemon.fainted:
                    continue
            if pokemon.status in ("psn", "tox"):
                if pokemon.ability == "Poison Heal":
                    healed = self._heal(pokemon, 1 / 8)
                    if healed:
                        self._log(f"{pokemon.name} healed with Poison Heal!")
                elif pokemon.ability != "Magic Guard":
                    if pokemon.status == "tox":
                        damage = max(1, pokemon.max_hp * pokemon.toxic_counter // 16)
                        pokemon.toxic_counter = min(15, pokemon.toxic_counter + 1)
                    else:
                        damage = max(1, pokemon.max_hp // 8)
                    self._apply_damage(None, pokemon, damage, contact=False, move=None)
                    if pokemon.fainted:
                        continue
            pokemon.protected = False
        self._handle_faints()

    def step(self, action0: Action, action1: Action) -> StepResult:
        if self.done:
            raise RuntimeError("battle already finished")
        self._validate_action(0, action0)
        self._validate_action(1, action1)
        self.turn += 1
        for side in (0, 1):
            self.active(side).protected = False

        # Switches resolve before moves.  Both sides may switch simultaneously.
        if action0.kind == "switch":
            self._switch(0, action0.index)
        if action1.kind == "switch":
            self._switch(1, action1.index)

        move_actions: list[tuple[int, Action]] = []
        if action0.kind == "move":
            move_actions.append((0, action0))
        if action1.kind == "move":
            move_actions.append((1, action1))

        def sort_key(item: tuple[int, Action]) -> tuple[int, int, float]:
            side, action = item
            move = STRUGGLE if action.index == -1 else self.active(side).moves[action.index].move
            priority = move.priority
            speed = self.effective_speed(self.active(side))
            return (-priority, -speed, self.rng.random())

        move_actions.sort(key=sort_key)
        for side, action in move_actions:
            if self.done:
                break
            if self.active(side).fainted:
                continue
            opponent_action = action1 if side == 0 else action0
            self._use_move(side, action, opponent_action)
            if self.sides[0].alive_count() == 0 or self.sides[1].alive_count() == 0:
                break

        if not self.done:
            self._end_of_turn()
        self._check_winner()
        self._last_actions = (action0, action1)
        return StepResult(
            views=(self.view(0), self.view(1)),
            rewards=self.rewards(),
            done=self.done,
            info={"winner": self.winner, "turns": self.turn},
        )

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def run(self, agent0: object, agent1: object, *, max_decisions: int = 500) -> int | None:
        """Run a full game with objects exposing ``act(battle, side, rng)``."""
        decisions = 0
        while not self.done and decisions < max_decisions:
            a0 = agent0.act(self, 0, self.rng)  # type: ignore[attr-defined]
            a1 = agent1.act(self, 1, self.rng)  # type: ignore[attr-defined]
            self.step(a0, a1)
            decisions += 1
        if not self.done:
            self.winner = -1
        return self.winner


def random_battle(seed: int = 0, team_size: int = 3, pool: Iterable[str] | None = None) -> Battle:
    """Create a battle with two independently sampled teams."""
    from .dex import sample_team

    rng = RNG(seed ^ 0x5EED)
    candidates = list(pool) if pool is not None else list(ALL_SPECIES)
    team0 = sample_team(candidates, team_size, rng)
    team1 = sample_team(candidates, team_size, rng)
    return Battle(team0, team1, seed=seed)


def preset_battle(name0: str, name1: str, seed: int = 0) -> Battle:
    from .dex import PRESET_TEAMS

    return Battle(PRESET_TEAMS[name0], PRESET_TEAMS[name1], seed=seed)
