import random

TYPE_CHART = {
    'normal': ['fighting'],
    'fire': ['water', 'ground', 'rock'],
    'water': ['electric', 'grass'],
    'electric': ['ground'],
    'grass': ['fire', 'ice', 'poison', 'flying', 'bug'],
    'ice': ['fire', 'fighting', 'rock', 'steel'],
    'fighting': ['flying', 'psychic', 'fairy'],
    'poison': ['ground', 'psychic'],
    'ground': ['water', 'grass', 'ice'],
    'flying': ['electric', 'ice', 'rock'],
    'psychic': ['bug', 'ghost', 'dark'],
    'bug': ['fire', 'flying', 'rock'],
    'rock': ['water', 'grass', 'fighting', 'ground', 'steel'],
    'ghost': ['ghost', 'dark'],
    'dragon': ['ice', 'dragon', 'fairy'],
    'dark': ['fighting', 'bug', 'fairy'],
    'steel': ['fire', 'fighting', 'ground'],
    'fairy': ['poison', 'steel'],
}

# Hardcoded estimates for common meta threats: (label, threat, base speed, types).
META_LEADS = [
    ("Standard OU Offense", "Landorus-Therian", 91, ["ground", "flying"]),
    ("Sun Offense", "Torkoal", 20, ["fire"]),
    ("Stall", "Alomomola", 65, ["normal"]),
    ("Hyper Offense", "Ribombee", 124, ["normal"]),
]


def get_coach_advice(user_lead_name, user_lead_types, user_lead_speed):
    meta_name, meta_lead, meta_speed, threat_type_list = random.choice(META_LEADS)

    advice_intro = f"Simulating matchup vs **{meta_name}** (Threat: **{meta_lead}**)."

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
