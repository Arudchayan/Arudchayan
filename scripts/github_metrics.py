import os
import json
import urllib.request

_FALLBACK = {"total_contributions": 0, "commit_streak": 0, "pull_requests": 0, "code_reviews": 0}

def get_github_stats():
    """
    Fetches GitHub contribution stats using GraphQL API.
    In the sandbox environment (no token), returns mock data.
    """
    token = os.environ.get("GITHUB_TOKEN")

    # No token (sandbox/testing): fall back to representative mock values
    if not token:
        print("⚠️ No GITHUB_TOKEN found. Using mock genetics data.")
        return {**_FALLBACK, "total_contributions": 432, "commit_streak": 12,
                "pull_requests": 15, "code_reviews": 8}

    # GraphQL Query
    query = """
    query($login: String!) {
      user(login: "Arudchayan") {
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

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        payload = json.dumps({"query": query}).encode()
        req = urllib.request.Request("https://api.github.com/graphql", data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            user_data = data.get("data", {}).get("user", {})
            contribs = user_data.get("contributionsCollection", {})

            total_contribs = contribs.get("contributionCalendar", {}).get("totalContributions", 0)
            prs = contribs.get("totalPullRequestContributions", 0)
            reviews = contribs.get("totalPullRequestReviewContributions", 0)

            # Since streak calculation is complex via API, approximate it
            streak = min(total_contribs // 20, 365)

            return {
                "total_contributions": total_contribs,
                "commit_streak": streak,
                "pull_requests": prs,
                "code_reviews": reviews,
            }
    except Exception as e:
        print(f"Exception fetching GitHub stats: {e}")
        return _FALLBACK

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
