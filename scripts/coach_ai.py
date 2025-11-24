import random

META_THREATS = [
    {"name": "Landorus-Therian", "type": ["ground", "flying"], "desc": "The Intimidate pivot king."},
    {"name": "Zacian-Crowned", "type": ["fairy", "steel"], "desc": "Speedy physical sweeper."},
    {"name": "Calyrex-Shadow", "type": ["psychic", "ghost"], "desc": "Nuclear special attacker."},
    {"name": "Kyogre", "type": ["water"], "desc": "Rain-boosted Water Spouts."},
    {"name": "Incineroar", "type": ["fire", "dark"], "desc": "VGC support menace."},
]

def analyze_matchup(team_data: list) -> str:
    """
    Analyzes the team against a random meta threat.
    """
    threat = random.choice(META_THREATS)
    threat_name = threat["name"]
    threat_types = threat["type"]

    # Simple counter logic
    counters = []

    type_chart = {
        'water': ['grass', 'electric'],
        'fire': ['water', 'ground', 'rock'],
        'ground': ['water', 'grass', 'ice'],
        'flying': ['electric', 'ice', 'rock'],
        'fairy': ['poison', 'steel'],
        'steel': ['fire', 'fighting', 'ground'],
        'ghost': ['ghost', 'dark'],
        'psychic': ['bug', 'ghost', 'dark'],
        'dark': ['fighting', 'bug', 'fairy'],
    }

    weaknesses = set()
    for t in threat_types:
        if t in type_chart:
            weaknesses.update(type_chart[t])

    for p in team_data:
        p_types = p.get('types', [])
        # Check if pokemon has a type advantage
        has_advantage = False
        for pt in p_types:
            if pt in weaknesses:
                has_advantage = True

        if has_advantage:
            counters.append(p['name'])

    if counters:
        advice = f"Your **{counters[0]}** is a key check here. Switch in safely!"
    else:
        advice = "You lack a direct type counter. Play aggressively or use status moves!"

    return f"**Coach's Corner:** Watch out for **{threat_name}** ({'/'.join(threat_types).upper()}). {threat['desc']} {advice}"
