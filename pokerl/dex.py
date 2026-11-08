"""Curated, dependency-free Pokédex for the benchmark.

The roster is intentionally small, fully evolved, and competitively coherent.
Every Pokémon ships with one fixed level-100 set (ability, item, nature, EVs,
four moves).  Fixing the sets removes team-building variance from the benchmark
and keeps the research question focused on *decision making*.

Base stats use the conventional short keys: hp, atk, def, spa, spd, spe.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

STAT_KEYS: tuple[str, ...] = ("hp", "atk", "def", "spa", "spd", "spe")
BOOST_KEYS: tuple[str, ...] = ("atk", "def", "spa", "spd", "spe")

NATURES: dict[str, tuple[str, str]] = {
    "Hardy": ("atk", "atk"),
    "Lonely": ("atk", "def"),
    "Brave": ("atk", "spe"),
    "Adamant": ("atk", "spa"),
    "Naughty": ("atk", "spd"),
    "Bold": ("def", "atk"),
    "Docile": ("def", "def"),
    "Relaxed": ("def", "spe"),
    "Impish": ("def", "spa"),
    "Lax": ("def", "spd"),
    "Timid": ("spe", "atk"),
    "Hasty": ("spe", "def"),
    "Serious": ("spe", "spe"),
    "Jolly": ("spe", "spa"),
    "Naive": ("spe", "spd"),
    "Modest": ("spa", "atk"),
    "Mild": ("spa", "def"),
    "Quiet": ("spa", "spe"),
    "Bashful": ("spa", "spa"),
    "Rash": ("spa", "spd"),
    "Calm": ("spd", "atk"),
    "Gentle": ("spd", "def"),
    "Sassy": ("spd", "spe"),
    "Careful": ("spd", "spa"),
    "Quirky": ("spd", "spd"),
}


@dataclass(frozen=True, slots=True)
class Species:
    id: str
    name: str
    types: tuple[str, ...]
    base_stats: Mapping[str, int]
    abilities: tuple[str, ...]
    weight: float = 50.0

    @property
    def bst(self) -> int:
        return sum(self.base_stats.values())


@dataclass(frozen=True, slots=True)
class Move:
    id: str
    name: str
    type: str
    category: str  # physical | special | status
    power: int
    accuracy: int  # 0 means never misses
    pp: int
    priority: int = 0
    contact: bool = False
    secondary: str | None = None
    secondary_chance: float = 0.0
    stat_changes: tuple[tuple[str, int, str], ...] = ()
    heal: int = 0
    recoil: float = 0.0
    drain: float = 0.0
    fixed_damage: int = 0
    switch: bool = False
    hazard: bool = False
    clear_hazards: bool = False
    protect: bool = False
    sucker: bool = False
    gyro: bool = False
    psyshock: bool = False
    knock_off: bool = False
    haze: bool = False

    @property
    def is_damaging(self) -> bool:
        return self.category != "status" and (self.power > 0 or self.fixed_damage > 0 or self.gyro)


@dataclass(frozen=True, slots=True)
class PokemonSet:
    species: str
    ability: str
    item: str
    nature: str
    evs: Mapping[str, int]
    moves: tuple[str, ...]

    def validate(self) -> None:
        if not 1 <= len(self.moves) <= 4:
            raise ValueError(f"{self.species}: expected 1-4 moves")
        if sum(self.evs.values()) > 508:
            raise ValueError(f"{self.species}: EV total exceeds 508")
        for stat, value in self.evs.items():
            if stat not in STAT_KEYS or value < 0 or value > 252 or value % 4:
                raise ValueError(f"{self.species}: invalid EV {stat}={value}")
        if self.nature not in NATURES:
            raise ValueError(f"{self.species}: unknown nature {self.nature}")


# ---------------------------------------------------------------------------
# Moves
# ---------------------------------------------------------------------------


def _m(
    id: str,
    name: str,
    type: str,
    category: str,
    power: int,
    accuracy: int,
    pp: int,
    **kwargs: object,
) -> Move:
    return Move(id, name, type, category, power, accuracy, pp, **kwargs)  # type: ignore[arg-type]


MOVES: dict[str, Move] = {
    # Physical attacks
    "earthquake": _m("earthquake", "Earthquake", "ground", "physical", 100, 100, 10),
    "dragon-claw": _m("dragon-claw", "Dragon Claw", "dragon", "physical", 80, 100, 15, contact=True),
    "stone-edge": _m("stone-edge", "Stone Edge", "rock", "physical", 100, 80, 5),
    "extreme-speed": _m("extreme-speed", "Extreme Speed", "normal", "physical", 80, 100, 5, priority=2, contact=True),
    "meteor-mash": _m(
        "meteor-mash",
        "Meteor Mash",
        "steel",
        "physical",
        90,
        90,
        10,
        contact=True,
        secondary="atk_up",
        secondary_chance=0.20,
    ),
    "bullet-punch": _m("bullet-punch", "Bullet Punch", "steel", "physical", 40, 100, 30, priority=1, contact=True),
    "brave-bird": _m("brave-bird", "Brave Bird", "flying", "physical", 120, 100, 15, contact=True, recoil=1 / 3),
    "iron-head": _m("iron-head", "Iron Head", "steel", "physical", 80, 100, 15, contact=True),
    "knock-off": _m("knock-off", "Knock Off", "dark", "physical", 65, 100, 20, contact=True, knock_off=True),
    "power-whip": _m("power-whip", "Power Whip", "grass", "physical", 120, 85, 10, contact=True),
    "gyro-ball": _m("gyro-ball", "Gyro Ball", "steel", "physical", 0, 100, 5, contact=True, gyro=True),
    "u-turn": _m("u-turn", "U-turn", "bug", "physical", 70, 100, 20, contact=True, switch=True),
    "superpower": _m(
        "superpower",
        "Superpower",
        "fighting",
        "physical",
        120,
        100,
        5,
        contact=True,
        stat_changes=(("atk", -1, "self"), ("def", -1, "self")),
    ),
    "icicle-crash": _m("icicle-crash", "Icicle Crash", "ice", "physical", 85, 90, 10, contact=True),
    "ice-shard": _m("ice-shard", "Ice Shard", "ice", "physical", 40, 100, 30, priority=1),
    "rapid-spin": _m("rapid-spin", "Rapid Spin", "normal", "physical", 50, 100, 40, contact=True, clear_hazards=True),
    "seed-bomb": _m("seed-bomb", "Seed Bomb", "grass", "physical", 80, 100, 15, contact=True),
    "mach-punch": _m("mach-punch", "Mach Punch", "fighting", "physical", 40, 100, 30, priority=1, contact=True),
    "plasma-fists": _m("plasma-fists", "Plasma Fists", "electric", "physical", 100, 100, 15, contact=True),
    "close-combat": _m(
        "close-combat",
        "Close Combat",
        "fighting",
        "physical",
        120,
        100,
        5,
        contact=True,
        stat_changes=(("def", -1, "self"), ("spd", -1, "self")),
    ),
    # Special attacks
    "shadow-ball": _m(
        "shadow-ball",
        "Shadow Ball",
        "ghost",
        "special",
        80,
        100,
        15,
        secondary="spd_down",
        secondary_chance=0.20,
        stat_changes=(("spd", -1, "foe"),),
    ),
    "sludge-bomb": _m(
        "sludge-bomb", "Sludge Bomb", "poison", "special", 90, 100, 10, secondary="poison", secondary_chance=0.30
    ),
    "focus-blast": _m(
        "focus-blast",
        "Focus Blast",
        "fighting",
        "special",
        120,
        70,
        5,
        secondary="spd_down",
        secondary_chance=0.10,
        stat_changes=(("spd", -1, "foe"),),
    ),
    "psychic": _m(
        "psychic",
        "Psychic",
        "psychic",
        "special",
        90,
        100,
        10,
        secondary="spd_down",
        secondary_chance=0.10,
        stat_changes=(("spd", -1, "foe"),),
    ),
    "energy-ball": _m(
        "energy-ball",
        "Energy Ball",
        "grass",
        "special",
        90,
        100,
        10,
        secondary="spd_down",
        secondary_chance=0.10,
        stat_changes=(("spd", -1, "foe"),),
    ),
    "fire-blast": _m(
        "fire-blast", "Fire Blast", "fire", "special", 110, 85, 5, secondary="burn", secondary_chance=0.10
    ),
    "earth-power": _m(
        "earth-power",
        "Earth Power",
        "ground",
        "special",
        90,
        100,
        10,
        secondary="spd_down",
        secondary_chance=0.10,
        stat_changes=(("spd", -1, "foe"),),
    ),
    "volt-switch": _m("volt-switch", "Volt Switch", "electric", "special", 70, 100, 20, switch=True),
    "hydro-pump": _m("hydro-pump", "Hydro Pump", "water", "special", 110, 80, 5),
    "flamethrower": _m(
        "flamethrower", "Flamethrower", "fire", "special", 90, 100, 15, secondary="burn", secondary_chance=0.10
    ),
    "bug-buzz": _m(
        "bug-buzz",
        "Bug Buzz",
        "bug",
        "special",
        90,
        100,
        10,
        secondary="spd_down",
        secondary_chance=0.10,
        stat_changes=(("spd", -1, "foe"),),
    ),
    "giga-drain": _m("giga-drain", "Giga Drain", "grass", "special", 75, 100, 10, drain=0.5),
    "draco-meteor": _m(
        "draco-meteor",
        "Draco Meteor",
        "dragon",
        "special",
        130,
        90,
        5,
        stat_changes=(("spa", -2, "self"),),
    ),
    "dark-pulse": _m("dark-pulse", "Dark Pulse", "dark", "special", 80, 100, 15),
    "scald": _m("scald", "Scald", "water", "special", 80, 100, 15, secondary="burn", secondary_chance=0.30),
    "moonblast": _m(
        "moonblast",
        "Moonblast",
        "fairy",
        "special",
        95,
        100,
        15,
        secondary="spa_down",
        secondary_chance=0.30,
        stat_changes=(("spa", -1, "foe"),),
    ),
    "psyshock": _m("psyshock", "Psyshock", "psychic", "special", 80, 100, 10, psyshock=True),
    # Status / utility
    "swords-dance": _m(
        "swords-dance", "Swords Dance", "normal", "status", 0, 0, 20, stat_changes=(("atk", 2, "self"),)
    ),
    "dragon-dance": _m(
        "dragon-dance",
        "Dragon Dance",
        "dragon",
        "status",
        0,
        0,
        20,
        stat_changes=(("atk", 1, "self"), ("spe", 1, "self")),
    ),
    "roost": _m("roost", "Roost", "flying", "status", 0, 0, 10, heal=50),
    "stealth-rock": _m("stealth-rock", "Stealth Rock", "rock", "status", 0, 0, 20, hazard=True),
    "nasty-plot": _m("nasty-plot", "Nasty Plot", "dark", "status", 0, 0, 20, stat_changes=(("spa", 2, "self"),)),
    "seismic-toss": _m(
        "seismic-toss", "Seismic Toss", "fighting", "physical", 0, 100, 20, fixed_damage=100, contact=True
    ),
    "soft-boiled": _m("soft-boiled", "Soft-Boiled", "normal", "status", 0, 0, 10, heal=50),
    "toxic": _m("toxic", "Toxic", "poison", "status", 0, 90, 10, secondary="toxic", secondary_chance=1.0),
    "protect": _m("protect", "Protect", "normal", "status", 0, 0, 10, priority=4, protect=True),
    "will-o-wisp": _m(
        "will-o-wisp", "Will-O-Wisp", "fire", "status", 0, 85, 15, secondary="burn", secondary_chance=1.0
    ),
    "thunder-wave": _m(
        "thunder-wave", "Thunder Wave", "electric", "status", 0, 90, 20, secondary="para", secondary_chance=1.0
    ),
    "quiver-dance": _m(
        "quiver-dance",
        "Quiver Dance",
        "bug",
        "status",
        0,
        0,
        20,
        stat_changes=(("spa", 1, "self"), ("spd", 1, "self"), ("spe", 1, "self")),
    ),
    "recover": _m("recover", "Recover", "normal", "status", 0, 0, 10, heal=50),
    "haze": _m("haze", "Haze", "ice", "status", 0, 0, 30, haze=True),
    "calm-mind": _m(
        "calm-mind",
        "Calm Mind",
        "psychic",
        "status",
        0,
        0,
        20,
        stat_changes=(("spa", 1, "self"), ("spd", 1, "self")),
    ),
    "spore": _m("spore", "Spore", "grass", "status", 0, 100, 5, secondary="sleep", secondary_chance=1.0),
    "slack-off": _m("slack-off", "Slack Off", "normal", "status", 0, 0, 10, heal=50),
    "defog": _m("defog", "Defog", "flying", "status", 0, 0, 15, clear_hazards=True),
}


# ---------------------------------------------------------------------------
# Species
# ---------------------------------------------------------------------------


def _s(
    id: str,
    name: str,
    types: tuple[str, ...],
    stats: tuple[int, int, int, int, int, int],
    abilities: tuple[str, ...],
    weight: float,
) -> Species:
    return Species(id, name, types, dict(zip(STAT_KEYS, stats)), abilities, weight)


SPECIES: dict[str, Species] = {
    "garchomp": _s(
        "garchomp", "Garchomp", ("dragon", "ground"), (108, 130, 95, 80, 85, 102), ("Rough Skin", "Sand Veil"), 95.0
    ),
    "dragonite": _s(
        "dragonite",
        "Dragonite",
        ("dragon", "flying"),
        (91, 134, 95, 100, 100, 80),
        ("Multiscale", "Inner Focus"),
        210.0,
    ),
    "metagross": _s(
        "metagross", "Metagross", ("steel", "psychic"), (80, 135, 130, 95, 90, 70), ("Clear Body", "Light Metal"), 550.0
    ),
    "gengar": _s(
        "gengar", "Gengar", ("ghost", "poison"), (60, 65, 60, 130, 75, 110), ("Levitate", "Cursed Body"), 40.5
    ),
    "alakazam": _s(
        "alakazam", "Alakazam", ("psychic",), (55, 50, 45, 135, 95, 120), ("Magic Guard", "Synchronize"), 48.0
    ),
    "blissey": _s(
        "blissey", "Blissey", ("normal",), (255, 10, 10, 75, 135, 55), ("Natural Cure", "Serene Grace"), 46.8
    ),
    "skarmory": _s(
        "skarmory", "Skarmory", ("steel", "flying"), (65, 80, 140, 40, 70, 70), ("Sturdy", "Keen Eye"), 50.5
    ),
    "gliscor": _s(
        "gliscor", "Gliscor", ("ground", "flying"), (75, 95, 125, 45, 75, 95), ("Poison Heal", "Hyper Cutter"), 42.5
    ),
    "heatran": _s(
        "heatran", "Heatran", ("fire", "steel"), (91, 90, 106, 130, 106, 77), ("Flash Fire", "Flame Body"), 430.0
    ),
    "rotom-wash": _s(
        "rotom-wash", "Rotom-Wash", ("electric", "water"), (50, 65, 107, 105, 107, 86), ("Levitate",), 0.3
    ),
    "ferrothorn": _s(
        "ferrothorn",
        "Ferrothorn",
        ("grass", "steel"),
        (74, 94, 131, 54, 116, 20),
        ("Iron Barbs", "Anticipation"),
        110.0,
    ),
    "scizor": _s("scizor", "Scizor", ("bug", "steel"), (70, 130, 100, 55, 80, 65), ("Technician", "Swarm"), 118.0),
    "mamoswine": _s(
        "mamoswine", "Mamoswine", ("ice", "ground"), (110, 130, 80, 70, 60, 80), ("Thick Fat", "Oblivious"), 291.0
    ),
    "volcarona": _s(
        "volcarona", "Volcarona", ("bug", "fire"), (85, 60, 65, 135, 105, 100), ("Flame Body", "Swarm"), 46.0
    ),
    "hydreigon": _s("hydreigon", "Hydreigon", ("dark", "dragon"), (92, 105, 90, 125, 90, 98), ("Levitate",), 160.0),
    "toxapex": _s(
        "toxapex", "Toxapex", ("poison", "water"), (50, 63, 152, 53, 142, 35), ("Regenerator", "Merciless"), 14.5
    ),
    "clefable": _s("clefable", "Clefable", ("fairy",), (95, 70, 73, 95, 90, 60), ("Magic Guard", "Unaware"), 40.0),
    "excadrill": _s(
        "excadrill", "Excadrill", ("ground", "steel"), (110, 135, 60, 50, 65, 88), ("Mold Breaker", "Sand Rush"), 40.4
    ),
    "gastrodon": _s(
        "gastrodon", "Gastrodon", ("water", "ground"), (111, 83, 68, 92, 82, 39), ("Storm Drain", "Sticky Hold"), 29.9
    ),
    "breloom": _s(
        "breloom", "Breloom", ("grass", "fighting"), (60, 130, 80, 60, 60, 70), ("Technician", "Poison Heal"), 39.2
    ),
    "zeraora": _s("zeraora", "Zeraora", ("electric",), (88, 112, 75, 102, 80, 143), ("Volt Absorb",), 44.5),
    "slowbro": _s(
        "slowbro", "Slowbro", ("water", "psychic"), (95, 75, 110, 100, 80, 30), ("Regenerator", "Oblivious"), 78.5
    ),
    "landorus-therian": _s(
        "landorus-therian", "Landorus-Therian", ("ground", "flying"), (89, 145, 90, 105, 80, 91), ("Intimidate",), 68.0
    ),
    "corviknight": _s(
        "corviknight", "Corviknight", ("flying", "steel"), (98, 87, 105, 53, 85, 67), ("Pressure", "Mirror Armor"), 75.0
    ),
}


# ---------------------------------------------------------------------------
# Fixed competitive sets
# ---------------------------------------------------------------------------


def _set(
    species: str,
    ability: str,
    item: str,
    nature: str,
    evs: dict[str, int],
    moves: tuple[str, ...],
) -> PokemonSet:
    return PokemonSet(species, ability, item, nature, evs, moves)


SETS: dict[str, PokemonSet] = {
    "garchomp": _set(
        "garchomp",
        "Rough Skin",
        "Life Orb",
        "Jolly",
        {"atk": 252, "def": 4, "spe": 252},
        ("earthquake", "dragon-claw", "stone-edge", "swords-dance"),
    ),
    "dragonite": _set(
        "dragonite",
        "Multiscale",
        "Leftovers",
        "Adamant",
        {"atk": 252, "spd": 4, "spe": 252},
        ("dragon-dance", "dragon-claw", "extreme-speed", "earthquake"),
    ),
    "metagross": _set(
        "metagross",
        "Clear Body",
        "Leftovers",
        "Adamant",
        {"hp": 252, "atk": 252, "def": 4},
        ("meteor-mash", "earthquake", "bullet-punch", "stealth-rock"),
    ),
    "gengar": _set(
        "gengar",
        "Levitate",
        "Life Orb",
        "Timid",
        {"spa": 252, "spd": 4, "spe": 252},
        ("shadow-ball", "sludge-bomb", "focus-blast", "nasty-plot"),
    ),
    "alakazam": _set(
        "alakazam",
        "Magic Guard",
        "Focus Sash",
        "Timid",
        {"spa": 252, "spd": 4, "spe": 252},
        ("psychic", "shadow-ball", "focus-blast", "energy-ball"),
    ),
    "blissey": _set(
        "blissey",
        "Natural Cure",
        "Leftovers",
        "Calm",
        {"hp": 252, "spd": 252, "def": 4},
        ("seismic-toss", "soft-boiled", "toxic", "protect"),
    ),
    "skarmory": _set(
        "skarmory",
        "Sturdy",
        "Leftovers",
        "Impish",
        {"hp": 252, "def": 252, "spd": 4},
        ("brave-bird", "roost", "stealth-rock", "iron-head"),
    ),
    "gliscor": _set(
        "gliscor",
        "Poison Heal",
        "Toxic Orb",
        "Impish",
        {"hp": 252, "def": 252, "spd": 4},
        ("earthquake", "roost", "toxic", "knock-off"),
    ),
    "heatran": _set(
        "heatran",
        "Flash Fire",
        "Leftovers",
        "Calm",
        {"hp": 252, "spd": 252, "spa": 4},
        ("fire-blast", "earth-power", "stealth-rock", "toxic"),
    ),
    "rotom-wash": _set(
        "rotom-wash",
        "Levitate",
        "Leftovers",
        "Bold",
        {"hp": 252, "def": 252, "spa": 4},
        ("volt-switch", "hydro-pump", "will-o-wisp", "thunder-wave"),
    ),
    "ferrothorn": _set(
        "ferrothorn",
        "Iron Barbs",
        "Leftovers",
        "Relaxed",
        {"hp": 252, "def": 252, "spd": 4},
        ("power-whip", "gyro-ball", "stealth-rock", "protect"),
    ),
    "scizor": _set(
        "scizor",
        "Technician",
        "Choice Band",
        "Adamant",
        {"hp": 252, "atk": 252, "spd": 4},
        ("bullet-punch", "u-turn", "knock-off", "superpower"),
    ),
    "mamoswine": _set(
        "mamoswine",
        "Thick Fat",
        "Life Orb",
        "Adamant",
        {"atk": 252, "spd": 4, "spe": 252},
        ("icicle-crash", "earthquake", "ice-shard", "superpower"),
    ),
    "volcarona": _set(
        "volcarona",
        "Flame Body",
        "Heavy-Duty Boots",
        "Timid",
        {"spa": 252, "spd": 4, "spe": 252},
        ("quiver-dance", "flamethrower", "bug-buzz", "giga-drain"),
    ),
    "hydreigon": _set(
        "hydreigon",
        "Levitate",
        "Life Orb",
        "Timid",
        {"spa": 252, "spd": 4, "spe": 252},
        ("draco-meteor", "dark-pulse", "flamethrower", "u-turn"),
    ),
    "toxapex": _set(
        "toxapex",
        "Regenerator",
        "Leftovers",
        "Bold",
        {"hp": 252, "def": 252, "spd": 4},
        ("scald", "recover", "toxic", "haze"),
    ),
    "clefable": _set(
        "clefable",
        "Magic Guard",
        "Leftovers",
        "Bold",
        {"hp": 252, "def": 252, "spd": 4},
        ("moonblast", "soft-boiled", "calm-mind", "flamethrower"),
    ),
    "excadrill": _set(
        "excadrill",
        "Mold Breaker",
        "Life Orb",
        "Jolly",
        {"atk": 252, "spd": 4, "spe": 252},
        ("earthquake", "iron-head", "rapid-spin", "swords-dance"),
    ),
    "gastrodon": _set(
        "gastrodon",
        "Storm Drain",
        "Leftovers",
        "Bold",
        {"hp": 252, "def": 252, "spd": 4},
        ("scald", "earth-power", "recover", "toxic"),
    ),
    "breloom": _set(
        "breloom",
        "Technician",
        "Life Orb",
        "Jolly",
        {"atk": 252, "spd": 4, "spe": 252},
        ("mach-punch", "seed-bomb", "spore", "swords-dance"),
    ),
    "zeraora": _set(
        "zeraora",
        "Volt Absorb",
        "Life Orb",
        "Jolly",
        {"atk": 252, "spd": 4, "spe": 252},
        ("plasma-fists", "close-combat", "knock-off", "volt-switch"),
    ),
    "slowbro": _set(
        "slowbro",
        "Regenerator",
        "Leftovers",
        "Bold",
        {"hp": 252, "def": 252, "spa": 4},
        ("scald", "psyshock", "slack-off", "thunder-wave"),
    ),
    "landorus-therian": _set(
        "landorus-therian",
        "Intimidate",
        "Choice Scarf",
        "Jolly",
        {"atk": 252, "spd": 4, "spe": 252},
        ("earthquake", "stone-edge", "u-turn", "knock-off"),
    ),
    "corviknight": _set(
        "corviknight",
        "Pressure",
        "Leftovers",
        "Impish",
        {"hp": 252, "def": 252, "spd": 4},
        ("brave-bird", "u-turn", "roost", "defog"),
    ),
}


for _set_obj in SETS.values():
    _set_obj.validate()
    if _set_obj.species not in SPECIES:
        raise ValueError(f"unknown species in set: {_set_obj.species}")
    if _set_obj.ability not in SPECIES[_set_obj.species].abilities:
        raise ValueError(f"{_set_obj.species}: ability {_set_obj.ability} not legal")
    for _move_id in _set_obj.moves:
        if _move_id not in MOVES:
            raise ValueError(f"{_set_obj.species}: unknown move {_move_id}")


# A deterministic split for the generalisation experiment.  The held-out
# species never appear while behaviour-cloning data is generated.
HELD_OUT_SPECIES: tuple[str, ...] = (
    "volcarona",
    "hydreigon",
    "toxapex",
    "clefable",
    "zeraora",
    "corviknight",
)
TRAIN_SPECIES: tuple[str, ...] = tuple(s for s in SPECIES if s not in HELD_OUT_SPECIES)
ALL_SPECIES: tuple[str, ...] = tuple(SPECIES)

PRESET_TEAMS: dict[str, tuple[str, ...]] = {
    "sand": ("garchomp", "excadrill", "skarmory"),
    "dragons": ("dragonite", "hydreigon", "garchomp"),
    "steel": ("metagross", "ferrothorn", "corviknight"),
    "balance": ("heatran", "rotom-wash", "clefable"),
    "offense": ("volcarona", "zeraora", "breloom"),
    "stall": ("blissey", "toxapex", "gliscor"),
    "water": ("rotom-wash", "gastrodon", "slowbro"),
    "misc": ("alakazam", "gengar", "scizor"),
}


def sample_team(pool: Iterable[str], size: int, rng: object) -> tuple[str, ...]:
    """Sample *size* distinct species without importing a random module."""
    candidates = list(pool)
    if size > len(candidates):
        raise ValueError("team size exceeds species pool")
    # The caller passes an RNG with .randint; use it for reproducibility.
    chosen: list[str] = []
    while len(chosen) < size:
        idx = rng.randint(0, len(candidates) - 1)  # type: ignore[attr-defined]
        chosen.append(candidates.pop(idx))
    return tuple(chosen)


def get_move(move_id: str) -> Move:
    return MOVES[move_id]


def get_species(species_id: str) -> Species:
    return SPECIES[species_id]


def get_set(species_id: str) -> PokemonSet:
    return SETS[species_id]
