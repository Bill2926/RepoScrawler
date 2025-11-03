import requests
import json
from git import Repo
from pathlib import Path
import os
import sys
import time

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # load from environment variable
if not GITHUB_TOKEN:
    print("   ERROR: Please set your GitHub token as an environment variable:")
    print("   export GITHUB_TOKEN='your_token_here'  (Linux/macOS)")
    print("   setx GITHUB_TOKEN \"your_token_here\"   (Windows PowerShell)")
    sys.exit(1)

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


def search_repos(keyword, limit):
    """Search for repositories by keyword."""
    print(f"Searching for repositories with keyword: '{keyword}'...")
    url = f"https://api.github.com/search/repositories?q={keyword}&sort=stars&order=desc&per_page={limit}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(f"GitHub API Error {response.status_code}: {response.text}")
        sys.exit(1)

    data = response.json()
    repos = []
    for repo in data.get("items", []):
        repos.append({
            "name": repo["name"],
            "full_name": repo["full_name"],
            "description": (repo["description"] or "")[:100],
            "language": repo["language"],
            "created_at": repo["created_at"],
            "clone_url": repo["clone_url"],
            "stars": repo["stargazers_count"],
        })
    print(f"Found {len(repos)} repositories.")
    return repos


def save_to_json(repos, filename="repos.json"):
    print(f"💾 Saving repository info to {filename}...")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(repos, f, indent=4, ensure_ascii=False)
    print("JSON saved.")


def clone_repos(repos, base_dir="cloned_repos"):
    # Clone each repository to a local folder
    Path(base_dir).mkdir(exist_ok=True)
    for repo in repos:
        name = repo["name"]
        clone_url = repo["clone_url"]
        local_path = Path(base_dir) / name

        if local_path.exists():
            print(f"Repo '{name}' already exists locally. Skipping.")
            continue

        print(f"⬇Cloning {name}...")
        try:
            Repo.clone_from(clone_url, local_path, depth=1) #depth = 1 to get the lastest git version, not the whole commit history
            print(f"Cloned: {name}")
        except Exception as e:
            print(f"Failed to clone {name}: {e}")
        time.sleep(2)  # pause slightly to avoid overloading GitHub


if __name__ == "__main__":
    keyword = input("Enter keyword to search for repositories: ").strip()
    if not keyword:
        print("Please provide a valid keyword.")
        sys.exit(1)

    repos = search_repos(keyword, limit=100)
    save_to_json(repos)
    clone_repos(repos)
    print("\nDone! Check 'repos.json' and the 'cloned_repos/' folder.")
