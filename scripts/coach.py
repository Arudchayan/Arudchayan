import random

class Coach:
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

    TYPE_CHART = {
        'normal': {'weak': ['fighting'], 'resist': [], 'immune': ['ghost']},
        'fire': {'weak': ['water', 'ground', 'rock'], 'resist': ['fire', 'grass', 'ice', 'bug', 'steel', 'fairy'], 'immune': []},
        'water': {'weak': ['electric', 'grass'], 'resist': ['fire', 'water', 'ice', 'steel'], 'immune': []},
        'electric': {'weak': ['ground'], 'resist': ['electric', 'flying', 'steel'], 'immune': []},
        'grass': {'weak': ['fire', 'ice', 'poison', 'flying', 'bug'], 'resist': ['water', 'electric', 'grass', 'ground'], 'immune': []},
        'ice': {'weak': ['fire', 'fighting', 'rock', 'steel'], 'resist': ['ice'], 'immune': []},
        'fighting': {'weak': ['flying', 'psychic', 'fairy'], 'resist': ['bug', 'rock', 'dark'], 'immune': []},
        'poison': {'weak': ['ground', 'psychic'], 'resist': ['grass', 'fighting', 'poison', 'bug', 'fairy'], 'immune': []},
        'ground': {'weak': ['water', 'grass', 'ice'], 'resist': ['poison', 'rock'], 'immune': ['electric']},
        'flying': {'weak': ['electric', 'ice', 'rock'], 'resist': ['grass', 'fighting', 'bug'], 'immune': ['ground']},
        'psychic': {'weak': ['bug', 'ghost', 'dark'], 'resist': ['fighting', 'psychic'], 'immune': []},
        'bug': {'weak': ['fire', 'flying', 'rock'], 'resist': ['grass', 'fighting', 'ground'], 'immune': []},
        'rock': {'weak': ['water', 'grass', 'fighting', 'ground', 'steel'], 'resist': ['normal', 'fire', 'poison', 'flying'], 'immune': []},
        'ghost': {'weak': ['ghost', 'dark'], 'resist': ['poison', 'bug'], 'immune': ['normal', 'fighting']},
        'dragon': {'weak': ['ice', 'dragon', 'fairy'], 'resist': ['fire', 'water', 'electric', 'grass'], 'immune': []},
        'dark': {'weak': ['fighting', 'bug', 'fairy'], 'resist': ['ghost', 'dark'], 'immune': ['psychic']},
        'steel': {'weak': ['fire', 'fighting', 'ground'], 'resist': ['normal', 'grass', 'ice', 'flying', 'psychic', 'bug', 'rock', 'dragon', 'steel', 'fairy'], 'immune': ['poison']},
        'fairy': {'weak': ['poison', 'steel'], 'resist': ['fighting', 'bug', 'dark'], 'immune': ['dragon']},
    }

    @staticmethod
    def get_coach_advice(user_lead_name, user_lead_types, user_lead_speed):
        meta_team = random.choice(Coach.META_TEAMS)
        meta_lead = random.choice(meta_team['pokemon']) # Pick a random threat from the meta team

        # Simplified speed tier check (hardcoded estimates for common meta threats)
        meta_speeds = {
            "Landorus-Therian": 91, "Dragapult": 142, "Kingambit": 50, "Great Tusk": 87,
            "Iron Valiant": 116, "Gholdengo": 84, "Flutter Mane": 135, "Walking Wake": 109,
            "Roaring Moon": 119, "Ribombee": 124, "Dragonite": 80, "Volcarona": 100,
            "Alomomola": 65, "Blissey": 55, "Dondozo": 35, "Clodsire": 20
        }

        meta_speed = meta_speeds.get(meta_lead, 90) # Default to 90 if unknown

        advice_intro = f"Simulating matchup vs **{meta_team['name']}** (Threat: **{meta_lead}**)."

        speed_note = ""
        if user_lead_speed > meta_speed:
            speed_note = f"Your **{user_lead_name}** outspeeds {meta_lead} (Base {meta_speed}). Strike first!"
        elif user_lead_speed == meta_speed:
            speed_note = f"Speed tie alert! Both sit around Base {meta_speed}. It's a coin flip."
        else:
            speed_note = f"Careful, **{meta_lead}** is faster (Base {meta_speed}). Consider defensive pivots."

        # Type Analysis
        weakness_note = ""
        user_weaknesses = set()
        for t in user_lead_types:
            user_weaknesses.update(Coach.TYPE_CHART.get(t, {}).get('weak', []))

        # Very rough inference of threat type (since we don't fetch meta data)
        # This is hardcoded for the demo to save API calls
        threat_types = {
            "Landorus-Therian": ["ground", "flying"],
            "Dragapult": ["dragon", "ghost"],
            "Kingambit": ["dark", "steel"],
            "Great Tusk": ["ground", "fighting"],
            "Flutter Mane": ["ghost", "fairy"],
            "Iron Valiant": ["fairy", "fighting"]
        }

        threat_type_list = threat_types.get(meta_lead, ["normal"])

        danger = False
        for tt in threat_type_list:
            if tt in user_weaknesses:
                danger = True
                weakness_note = f"Warning: {meta_lead} has STAB **{tt.upper()}** moves that hit you for super-effective damage!"
                break

        if not danger:
            weakness_note = "Type matchup looks neutral or favorable. Press the advantage."

        return f"{advice_intro} {speed_note} {weakness_note}"
