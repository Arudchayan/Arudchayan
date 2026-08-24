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

def simulate_team_battle(gym_team, challenger_team_names):
    """
    Simulates a 6v6 battle.
    gym_team: List of Dicts (Full Pokemon Data)
    challenger_team_names: List of strings (just names)
    """
    score_gym = 0
    score_challenger = 0
    log = []

    log.append(f"⚔️ **Battle Start!** Leader Arudchayan vs Challenger!")

    # We limit to 6v6 or smaller
    limit = min(len(gym_team), len(challenger_team_names))

    for i in range(limit):
        gym_mon = gym_team[i]
        # Mock challenger mon stats since we only have names
        chall_name = challenger_team_names[i]

        # Simple Logic:
        # 1. Base Win Chance (50/50)
        # 2. Gym Mon Bonus: Higher BST/Level/Genetics -> +20%
        # 3. Challenger Bonus: If name is "Legendary" or pseudo -> +10%
        # (Keeping it text-based and fun)

        gym_power = sum(gym_mon.get('stats', {}).values()) or 500
        chall_power = 500 # Average assumption

        # Check for pseudo/legendary keywords in challenger name
        if any(x in chall_name.lower() for x in ['mewtwo', 'rayquaza', 'arceus', 'eternatus', 'zacian']):
            chall_power += 150
        if any(x in chall_name.lower() for x in ['dragonite', 'tyranitar', 'metagross', 'garchomp']):
            chall_power += 80

        # Random Variance
        gym_roll = gym_power * random.uniform(0.8, 1.2)
        chall_roll = chall_power * random.uniform(0.8, 1.2)

        log.append(f"🔹 **Round {i+1}:** {gym_mon['name']} vs {chall_name}!")

        if gym_roll >= chall_roll:
            score_gym += 1
            outcome = f"{gym_mon['name']} lands a decisive blow!"
        else:
            score_challenger += 1
            outcome = f"{chall_name} breaks through the defenses!"

        log.append(f"  > {outcome}")

    # Final Result
    if score_gym > score_challenger:
        result = f"🏆 **Gym Leader Wins {score_gym}-{score_challenger}!**"
        winner = "Arudchayan"
    elif score_challenger > score_gym:
        result = f"🏆 **Challenger Wins {score_challenger}-{score_gym}!**"
        winner = "Challenger"
    else:
        result = "🤝 **It's a Draw!**"
        winner = "Draw"

    log.append(result)

    return {
        "winner": winner,
        "score": f"{score_gym}-{score_challenger}",
        "log": "\n".join(log)
    }
