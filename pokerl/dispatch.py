"""Deterministic daily dispatch: a small Pokémon-flavoured ritual for the lab."""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from .dex import SETS, SPECIES
from .rng import RNG
from .types import TYPE_EMOJI

ROOT = Path(__file__).resolve().parent.parent
DISPATCH_START = "<!-- DISPATCH:START -->"
DISPATCH_END = "<!-- DISPATCH:END -->"

QUESTS = (
    "Run one ablation you have been avoiding.",
    "Replicate yesterday's seed before changing the code.",
    "Write the failure case first, then the fix.",
    "Check the confidence interval, not just the mean.",
    "Delete a feature and see whether the result survives.",
    "Profile the benchmark before optimizing the model.",
    "Read the held-out split before touching the train set.",
    "Add a regression test for the bug you just fixed.",
)


def _bar(value: int, maximum: int, length: int = 18) -> str:
    filled = int(max(0.0, min(1.0, value / maximum)) * length)
    return "█" * filled + "░" * (length - filled)


def build_dispatch(date: datetime.date | None = None) -> dict:
    date = date or datetime.datetime.now(datetime.UTC).date()
    day = date.toordinal()
    rng = RNG(day ^ 0xD15FA7C)
    species_ids = list(SPECIES)
    rng.shuffle(species_ids)
    species_id = species_ids[0]
    opponent_id = species_ids[1]
    species = SPECIES[species_id]
    opponent = SPECIES[opponent_id]
    quest = rng.choice(QUESTS)
    seed = rng.next_u64()
    return {
        "date": date.isoformat(),
        "day_number": day,
        "species": species_id,
        "species_name": species.name,
        "types": list(species.types),
        "bst": species.bst,
        "opponent": opponent_id,
        "opponent_name": opponent.name,
        "quest": quest,
        "seed": seed,
        "moves": list(SETS[species_id].moves),
    }


def render_dispatch(payload: dict, *, include_header: bool = True) -> str:
    species = SPECIES[payload["species"]]
    types = " ".join(f"{TYPE_EMOJI.get(t, '')}{t.upper()}" for t in species.types)
    stats = species.base_stats
    lines = []
    if include_header:
        lines.append(f"## 🎮 Daily Lab Dispatch — {payload['date']}")
        lines.append("")
    lines.append(f"**Specimen of the day:** **{species.name}** · {types} · BST **{species.bst}**")
    lines.append("")
    lines.append(
        "```text\n"
        + "\n".join(
            f"{stat.upper():>3}: {_bar(stats[stat], 180)} {stats[stat]:>3}"
            for stat in ("hp", "atk", "def", "spa", "spd", "spe")
        )
        + "\n```"
    )
    lines.append("")
    lines.append(f"**Today's experiment:** {payload['quest']}")
    lines.append(f"**Featured matchup:** {species.name} vs {payload['opponent_name']} · seed `{payload['seed']}`")
    lines.append("")
    lines.append(
        "> Run `python -m pokerl demo --seed "
        + str(payload["seed"] % 100000)
        + "` to inspect a reproducible battle from today's seed."
    )
    return "\n".join(lines)


def update_readme(payload: dict, readme_path: str | Path = ROOT / "README.md") -> bool:
    path = Path(readme_path)
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    if DISPATCH_START not in text or DISPATCH_END not in text:
        return False
    block = DISPATCH_START + "\n" + render_dispatch(payload) + "\n" + DISPATCH_END
    before = text.split(DISPATCH_START, 1)[0]
    after = text.split(DISPATCH_END, 1)[1]
    path.write_text(before + block + after, encoding="utf-8")
    return True


def write_dispatch(payload: dict, docs_dir: str | Path = ROOT / "docs") -> Path:
    path = Path(docs_dir) / "dispatch.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def daily_dispatch(*, update_readme_file: bool = True) -> dict:
    payload = build_dispatch()
    write_dispatch(payload)
    if update_readme_file:
        update_readme(payload)
    return payload
