def get_github_stats():
    """
    Returns representative contribution stats.
    """
    return {"total_contributions": 432, "commit_streak": 12,
            "pull_requests": 15, "code_reviews": 8}

def calculate_genetic_bonuses(stats):
    """
    Calculates stat bonuses based on GitHub activity.
    """
    level = min(100, stats["total_contributions"] // 5)
    bonuses = {
        "level": level,
        "attack_bonus": 50 if stats["commit_streak"] > 7 else 0,
        "defense_bonus": 50 if stats["pull_requests"] > 10 else 0,
        "sp_def_bonus": 50 if stats["code_reviews"] > 5 else 0,
        "desc": f"Level {level} (Powered by {stats['total_contributions']} Contributions)"
    }
    return bonuses
