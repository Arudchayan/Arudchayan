import random
import json
import os

# Mock data for GitHub stats since we can't access the real API in this environment
# In a real scenario, this would fetch from GitHub GraphQL API
MOCK_CONTRIBUTION_DATA = {
    "total_commits": 432,
    "pull_requests": 45,
    "issues_opened": 28,
    "code_reviews": 156,
    "stars_earned": 89,
    "longest_streak": 14
}

class GitHubGenetics:
    @staticmethod
    def get_stats():
        """
        Returns contribution stats.
        In production, this should fetch from GitHub API using GITHUB_TOKEN.
        """
        # Logic to determine multipliers
        # Commit count -> Attack/SpAtk boost
        # PRs -> Defense boost
        # Reviews -> SpDef boost
        # Streak -> Speed boost
        # Issues -> HP boost

        data = MOCK_CONTRIBUTION_DATA

        return {
            "atk_iv": min(31, int(data["total_commits"] / 20)),
            "def_iv": min(31, int(data["pull_requests"] / 2)),
            "spa_iv": min(31, int(data["total_commits"] / 20)),
            "spd_iv": min(31, int(data["code_reviews"] / 5)),
            "spe_iv": min(31, int(data["longest_streak"] * 2)),
            "hp_iv": min(31, int(data["issues_opened"])),
            "level": min(100, int(data["total_commits"] / 10) + 50),
            "title": GitHubGenetics._get_title(data)
        }

    @staticmethod
    def _get_title(data):
        commits = data["total_commits"]
        if commits > 1000: return "Legendary Contributor"
        if commits > 500: return "Grandmaster Dev"
        if commits > 100: return "Elite Coder"
        return "Trainer"

    @staticmethod
    def apply_genetics(pokemon_stats: dict, genetics: dict) -> dict:
        """
        Modifies base stats based on 'Genetics' (GitHub Stats).
        We treat GitHub stats as IVs (Individual Values) that boost the base.
        """
        new_stats = pokemon_stats.copy()

        # Apply IVs (0-31 boost)
        new_stats['hp'] = new_stats.get('hp', 0) + genetics['hp_iv']
        new_stats['attack'] = new_stats.get('attack', 0) + genetics['atk_iv']
        new_stats['defense'] = new_stats.get('defense', 0) + genetics['def_iv']
        new_stats['special-attack'] = new_stats.get('special-attack', 0) + genetics['spa_iv']
        new_stats['special-defense'] = new_stats.get('special-defense', 0) + genetics['spd_iv']
        new_stats['speed'] = new_stats.get('speed', 0) + genetics['spe_iv']

        return new_stats
