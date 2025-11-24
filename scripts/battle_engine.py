import sys
import os
import json
import random

def run_battle(challenger_team: list, user_team: list):
    """
    Simulates a battle between two teams.
    Returns a log and a winner.
    """
    log = []
    log.append(f"⚔️ **CHALLENGER APPROACHING!**")

    # Simplified logic: Compare total stats
    user_score = 0
    challenger_score = 0

    log.append("---")

    for i in range(min(len(challenger_team), len(user_team))):
        c_mon = challenger_team[i]
        u_mon = user_team[i]

        log.append(f"**Round {i+1}:** {u_mon['name']} vs {c_mon['name']}")

        # Random variance
        u_val = random.randint(80, 120)
        c_val = random.randint(80, 120)

        if u_val > c_val:
            log.append(f"✅ {u_mon['name']} lands a critical hit! (Winner: {u_mon['name']})")
            user_score += 1
        else:
            log.append(f"❌ {c_mon['name']} overpowers the defense! (Winner: {c_mon['name']})")
            challenger_score += 1

    log.append("---")
    if user_score >= challenger_score:
        result = "WIN"
        log.append(f"🏆 **DEFENSE SUCCESSFUL!** ({user_score}-{challenger_score})")
    else:
        result = "LOSS"
        log.append(f"💀 **DEFEATED...** ({user_score}-{challenger_score})")

    return result, "\n".join(log)

if __name__ == "__main__":
    # This script would be called by the GitHub Action parsing the issue body
    print("Battle Engine Ready.")
