import os
import json
import sys
import datetime
# Assuming this script is run from repo root
sys.path.append(os.getcwd())

from scripts.battle_engine import BattleEngine

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
    # We need to peek at archetypes.json and pick the current daily one
    # Or just load a fallback for the simulation script independent of the main build
    try:
        with open("data/archetypes.json") as f:
            arcs = json.load(f)
        # Just pick a random strong one for the defense
        # In a real scenario, we'd match the 'active' one
        gym_data = arcs[0]
        gym_names = gym_data['team']

        # We need stats for the engine, but battle_engine uses simple logic mostly
        # Let's mock the dict structure expected by BattleEngine
        gym_team_objs = [{'name': n, 'stats': {'total': 550}} for n in gym_names]

    except Exception as e:
        print(f"Error loading archetypes: {e}")
        return

    # 4. Simulate
    result = BattleEngine.simulate_team_battle(gym_team_objs, team)

    # 5. Save Record
    record = {
        "date": datetime.date.today().isoformat(),
        "challenger": challenger_name,
        "team": team,
        "result": result['score'],
        "winner": result['winner']
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

    print(f"Battle processed. Winner: {result['winner']}")
    # Output for GitHub Action to use in comment
    print(f"::set-output name=battle_log::{result['log'].replace(chr(10), '%0A')}")

if __name__ == "__main__":
    process_challenge()
