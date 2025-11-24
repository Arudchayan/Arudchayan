import os
import json
import datetime
import requests

def get_github_stats(username="Arudchayan", token=None):
    """
    Fetches GitHub contribution stats using GraphQL API.
    In the sandbox environment (no token), returns mock data.
    """
    if not token:
        token = os.environ.get("GITHUB_TOKEN")

    # Mock data for sandbox testing or if no token is present
    if not token:
        print("⚠️ No GITHUB_TOKEN found. Using mock genetics data.")
        return {
            "total_contributions": 432,
            "commit_streak": 12,
            "pull_requests": 15,
            "code_reviews": 8,
            "mock": True
        }

    # GraphQL Query
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
          totalPullRequestContributions
          totalPullRequestReviewContributions
        }
      }
    }
    """

    # We would also calculate streak here, but for simplicity in this script
    # (and to avoid complex paginated queries for commit history),
    # we might approximate or fetch a separate "streak" API if available,
    # or just use the mock logic/simple calc.
    # For this implementation, I'll stick to the metrics easily available.

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"login": username}},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            user_data = data.get("data", {}).get("user", {})
            contribs = user_data.get("contributionsCollection", {})

            total_contribs = contribs.get("contributionCalendar", {}).get("totalContributions", 0)
            prs = contribs.get("totalPullRequestContributions", 0)
            reviews = contribs.get("totalPullRequestReviewContributions", 0)

            # Since streak calculation is complex via API, we will randomize it slightly based on contribs
            # or treat it as a placeholder unless we use a specialized action input.
            # Let's assume a rough estimate:
            streak = min(total_contribs // 20, 365)

            return {
                "total_contributions": total_contribs,
                "commit_streak": streak,
                "pull_requests": prs,
                "code_reviews": reviews,
                "mock": False
            }
        else:
            print(f"Error fetching GitHub stats: {response.status_code}")
            return {
                "total_contributions": 0,
                "commit_streak": 0,
                "pull_requests": 0,
                "code_reviews": 0,
                "mock": True
            }

    except Exception as e:
        print(f"Exception fetching GitHub stats: {e}")
        return {
            "total_contributions": 0,
            "commit_streak": 0,
            "pull_requests": 0,
            "code_reviews": 0,
            "mock": True
        }

def calculate_genetic_bonuses(stats):
    """
    Calculates stat bonuses based on GitHub activity.
    """
    bonuses = {
        "level": min(100, stats["total_contributions"] // 5),
        "attack_bonus": 50 if stats["commit_streak"] > 7 else 0,
        "defense_bonus": 50 if stats["pull_requests"] > 10 else 0,
        "sp_def_bonus": 50 if stats["code_reviews"] > 5 else 0,
        "desc": f"Level {min(100, stats['total_contributions'] // 5)} (Powered by {stats['total_contributions']} Contributions)"
    }
    return bonuses
