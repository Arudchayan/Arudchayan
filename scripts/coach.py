import random

from battle_engine import TYPE_CHART

META_TEAMS = [
    {
        "name": "Standard OU Offense",
        "pokemon": ["Landorus-Therian", "Dragapult", "Kingambit", "Great Tusk", "Iron Valiant", "Gholdengo"]
    },
    {
        "name": "Sun Offense",
        "pokemon": ["Torkoal", "Flutter Mane", "Walking Wake", "Roaring Moon", "Lilligant-Hisui", "Great Tusk"]
    },
    {
        "name": "Stall",
        "pokemon": ["Alomomola", "Blissey", "Dondozo", "Clodsire", "Toxapex", "Corviknight"]
    },
    {
        "name": "Hyper Offense",
        "pokemon": ["Ribombee", "Gholdengo", "Dragonite", "Volcarona", "Iron Moth", "Ogerpon-Wellspring"]
    }
]

# Hardcoded estimates for common meta threats: (base speed, types); defaults cover the rest.
META_THREATS = {
    "Landorus-Therian": (91, ["ground", "flying"]),
    "Dragapult": (142, ["dragon", "ghost"]),
    "Kingambit": (50, ["dark", "steel"]),
    "Great Tusk": (87, ["ground", "fighting"]),
    "Iron Valiant": (116, ["fairy", "fighting"]),
    "Gholdengo": (84, ["normal"]),
    "Flutter Mane": (135, ["ghost", "fairy"]),
    "Walking Wake": (109, ["normal"]),
    "Roaring Moon": (119, ["normal"]),
    "Ribombee": (124, ["normal"]),
    "Dragonite": (80, ["normal"]),
    "Volcarona": (100, ["normal"]),
    "Alomomola": (65, ["normal"]),
    "Blissey": (55, ["normal"]),
    "Dondozo": (35, ["normal"]),
    "Clodsire": (20, ["normal"]),
}


def get_coach_advice(user_lead_name, user_lead_types, user_lead_speed):
    meta_team = random.choice(META_TEAMS)
    meta_lead = random.choice(meta_team['pokemon'])

    meta_speed, threat_type_list = META_THREATS.get(meta_lead, (90, ["normal"]))

    advice_intro = f"Simulating matchup vs **{meta_team['name']}** (Threat: **{meta_lead}**)."

    if user_lead_speed > meta_speed:
        speed_note = f"Your **{user_lead_name}** outspeeds {meta_lead} (Base {meta_speed}). Strike first!"
    elif user_lead_speed == meta_speed:
        speed_note = f"Speed tie alert! Both sit around Base {meta_speed}. It's a coin flip."
    else:
        speed_note = f"Careful, **{meta_lead}** is faster (Base {meta_speed}). Consider defensive pivots."

    user_weaknesses = set()
    for t in user_lead_types:
        user_weaknesses.update(TYPE_CHART.get(t, []))

    weakness_note = next(
        (f"Warning: {meta_lead} has STAB **{tt.upper()}** moves that hit you for super-effective damage!"
         for tt in threat_type_list if tt in user_weaknesses),
        "Type matchup looks neutral or favorable. Press the advantage."
    )

    return f"{advice_intro} {speed_note} {weakness_note}"
