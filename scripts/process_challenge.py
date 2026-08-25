import os
import json
import datetime
import random


def process_challenge():
    """
    Parses issue body, runs battle, updates history.
    Intended to be run by GitHub Action.
    """
    # 1. Inputs
    challenger_name = os.environ.get("CHALLENGER_NAME", "Unknown Trainer")
    issue_body = os.environ.get("ISSUE_BODY", "")

    # 2. Parse Team
    # Assumes format: "- Pokemon1\n- Pokemon2..." or just lines
    team = []
    for line in issue_body.splitlines():
        clean = line.strip().replace("- ", "").replace("* ", "")
        if clean and len(clean) < 20: # Sanity check length
            team.append(clean)

    # Validation
    if not team:
        print("No valid team found.")
        return

    team = team[:6] # Cap at 6

    # 3. Load Gym Team (Current Archetype)
    try:
        with open("data/archetypes.json") as f:
            arcs = json.load(f)
        gym_names = arcs[0]['team']
    except Exception as e:
        print(f"Error loading archetypes: {e}")
        return

    # 4. Simulate: coin-flip rounds with a slight edge to the house
    score_gym = score_challenger = 0
    log = ["⚔️ **Battle Start!** Leader Arudchayan vs Challenger!"]
    for i, (gym_mon, chall_name) in enumerate(zip(gym_names[:6], team), start=1):
        log.append(f"🔹 **Round {i}:** {gym_mon} vs {chall_name}!")
        if random.random() < 0.55:
            score_gym += 1
            log.append(f"  > {gym_mon} lands a decisive blow!")
        else:
            score_challenger += 1
            log.append(f"  > {chall_name} breaks through the defenses!")

    if score_gym > score_challenger:
        winner = "Arudchayan"
    elif score_challenger > score_gym:
        winner = "Challenger"
    else:
        winner = "Draw"
    score = f"{score_gym}-{score_challenger}"
    result_line = {
        "Arudchayan": f"🏆 **Gym Leader Wins {score}!**",
        "Challenger": f"🏆 **Challenger Wins {score_challenger}-{score_gym}!**",
        "Draw": "🤝 **It's a Draw!**",
    }[winner]
    log.append(result_line)

    # 5. Save Record
    record = {
        "date": datetime.date.today().isoformat(),
        "challenger": challenger_name,
        "team": team,
        "result": score,
        "winner": winner
    }

    history_file = "data/challengers.json"
    history = []
    if os.path.exists(history_file):
        with open(history_file) as f:
            history = json.load(f)

    history.insert(0, record)
    history = history[:10] # Keep last 10

    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)

    print(f"Battle processed. Winner: {winner}")
    # Output for GitHub Action to use in comment
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"battle_log<<EOF\n" + "\n".join(log) + "\nEOF\n")

if __name__ == "__main__":
    process_challenge()
