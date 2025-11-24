import json
import os
import random

HISTORY_FILE = "data/trainer_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_history(data):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_shiny_odds():
    history = load_history()
    pity_counter = history.get("shiny_pity_counter", 0)

    # Base rate is 1/48 (approx 2%)
    # Pity adds 0.5% per day dry
    base_rate = 1 / 48
    bonus = pity_counter * 0.005

    total_rate = min(0.5, base_rate + bonus) # Cap at 50%
    return total_rate, pity_counter

def record_encounter(is_shiny: bool):
    history = load_history()
    current_pity = history.get("shiny_pity_counter", 0)

    if is_shiny:
        history["shiny_pity_counter"] = 0
        history["shinies_caught"] = history.get("shinies_caught", 0) + 1
        result = "reset"
    else:
        history["shiny_pity_counter"] = current_pity + 1
        result = "incremented"

    save_history(history)
    return result
