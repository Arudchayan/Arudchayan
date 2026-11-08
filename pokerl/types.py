"""The Gen VI+ type chart and small presentation helpers."""

from __future__ import annotations

from collections.abc import Iterable

TYPES: tuple[str, ...] = (
    "normal",
    "fire",
    "water",
    "electric",
    "grass",
    "ice",
    "fighting",
    "poison",
    "ground",
    "flying",
    "psychic",
    "bug",
    "rock",
    "ghost",
    "dragon",
    "dark",
    "steel",
    "fairy",
)

TYPE_INDEX: dict[str, int] = {name: i for i, name in enumerate(TYPES)}

TYPE_EMOJI: dict[str, str] = {
    "normal": "⚪",
    "fire": "🔥",
    "water": "💧",
    "electric": "⚡",
    "grass": "🌿",
    "ice": "🧊",
    "fighting": "🥊",
    "poison": "☠️",
    "ground": "🌍",
    "flying": "🕊️",
    "psychic": "🔮",
    "bug": "🐛",
    "rock": "🪨",
    "ghost": "👻",
    "dragon": "🐉",
    "dark": "🌙",
    "steel": "⚙️",
    "fairy": "✨",
}

TYPE_COLOR: dict[str, str] = {
    "normal": "#9FA19F",
    "fire": "#E62829",
    "water": "#2980EF",
    "electric": "#FAC000",
    "grass": "#3FA129",
    "ice": "#3FD8FF",
    "fighting": "#FF8000",
    "poison": "#9141CB",
    "ground": "#915121",
    "flying": "#81B9EF",
    "psychic": "#EF4179",
    "bug": "#91A119",
    "rock": "#AFA981",
    "ghost": "#704170",
    "dragon": "#5060E1",
    "dark": "#624D4E",
    "steel": "#60A1B8",
    "fairy": "#EF70EF",
}

# Attacking type -> defending type -> multiplier.  Omitted pairs are 1x.
_CHART: dict[str, dict[str, float]] = {
    "normal": {"rock": 0.5, "steel": 0.5, "ghost": 0.0},
    "fire": {
        "fire": 0.5,
        "water": 0.5,
        "grass": 2.0,
        "ice": 2.0,
        "bug": 2.0,
        "rock": 0.5,
        "dragon": 0.5,
        "steel": 2.0,
    },
    "water": {
        "fire": 2.0,
        "water": 0.5,
        "grass": 0.5,
        "ground": 2.0,
        "rock": 2.0,
        "dragon": 0.5,
    },
    "electric": {
        "water": 2.0,
        "electric": 0.5,
        "grass": 0.5,
        "ground": 0.0,
        "flying": 2.0,
        "dragon": 0.5,
    },
    "grass": {
        "fire": 0.5,
        "water": 2.0,
        "grass": 0.5,
        "poison": 0.5,
        "ground": 2.0,
        "flying": 0.5,
        "bug": 0.5,
        "rock": 2.0,
        "dragon": 0.5,
        "steel": 0.5,
    },
    "ice": {
        "fire": 0.5,
        "water": 0.5,
        "grass": 2.0,
        "ice": 0.5,
        "ground": 2.0,
        "flying": 2.0,
        "dragon": 2.0,
        "steel": 0.5,
    },
    "fighting": {
        "normal": 2.0,
        "ice": 2.0,
        "poison": 0.5,
        "flying": 0.5,
        "psychic": 0.5,
        "bug": 0.5,
        "rock": 2.0,
        "ghost": 0.0,
        "dark": 2.0,
        "steel": 2.0,
        "fairy": 0.5,
    },
    "poison": {
        "grass": 2.0,
        "poison": 0.5,
        "ground": 0.5,
        "rock": 0.5,
        "ghost": 0.5,
        "steel": 0.0,
        "fairy": 2.0,
    },
    "ground": {
        "fire": 2.0,
        "electric": 2.0,
        "grass": 0.5,
        "poison": 2.0,
        "flying": 0.0,
        "bug": 0.5,
        "rock": 2.0,
        "steel": 2.0,
    },
    "flying": {
        "electric": 0.5,
        "grass": 2.0,
        "fighting": 2.0,
        "bug": 2.0,
        "rock": 0.5,
        "steel": 0.5,
    },
    "psychic": {
        "fighting": 2.0,
        "poison": 2.0,
        "psychic": 0.5,
        "dark": 0.0,
        "steel": 0.5,
    },
    "bug": {
        "fire": 0.5,
        "grass": 2.0,
        "fighting": 0.5,
        "poison": 0.5,
        "flying": 0.5,
        "psychic": 2.0,
        "ghost": 0.5,
        "dark": 2.0,
        "steel": 0.5,
        "fairy": 0.5,
    },
    "rock": {
        "fire": 2.0,
        "ice": 2.0,
        "fighting": 0.5,
        "ground": 0.5,
        "flying": 2.0,
        "bug": 2.0,
        "steel": 0.5,
    },
    "ghost": {
        "normal": 0.0,
        "psychic": 2.0,
        "ghost": 2.0,
        "dark": 0.5,
    },
    "dragon": {"dragon": 2.0, "steel": 0.5, "fairy": 0.0},
    "dark": {"fighting": 0.5, "psychic": 2.0, "ghost": 2.0, "dark": 0.5, "fairy": 0.5},
    "steel": {
        "fire": 0.5,
        "water": 0.5,
        "electric": 0.5,
        "ice": 2.0,
        "rock": 2.0,
        "steel": 0.5,
        "fairy": 2.0,
    },
    "fairy": {
        "fire": 0.5,
        "fighting": 2.0,
        "poison": 0.5,
        "dragon": 2.0,
        "dark": 2.0,
        "steel": 0.5,
    },
}


def effectiveness(move_type: str, defender_types: Iterable[str]) -> float:
    """Return the damage multiplier for *move_type* against a typing."""
    multiplier = 1.0
    row = _CHART[move_type]
    for defender_type in defender_types:
        multiplier *= row.get(defender_type, 1.0)
    return multiplier


def is_immune(move_type: str, defender_types: Iterable[str]) -> bool:
    return effectiveness(move_type, defender_types) == 0.0


def stab(move_type: str, attacker_types: Iterable[str]) -> float:
    return 1.5 if move_type in attacker_types else 1.0


def type_label(type_name: str) -> str:
    return f"{TYPE_EMOJI.get(type_name, '')}{type_name.upper()}"


def type_badge_markdown(type_name: str) -> str:
    color = TYPE_COLOR.get(type_name, "#888888")
    return (
        f'<span style="display:inline-block;padding:2px 8px;border-radius:999px;'
        f"background:{color};color:#0b0b12;font-weight:700;font-size:12px;"
        f'letter-spacing:.04em">{type_name.upper()}</span>'
    )
