# RepoScrawler

A basic Python crawler script to get repository information and clone them to your local machine.

## 📋 Overview

This tool allows you to:
- Search GitHub repositories by keyword
- Retrieve repository metadata (name, description, stars, language, etc.)
- Save repository information to a JSON file
- Clone repositories locally for offline access

## 🔧 Requirements

### Prerequisites

- **Python 3.6+**
- **Git** installed and accessible from command line

### Python Dependencies
```bash
pip install requests gitpython
```

**Required packages:**
- `requests` - For GitHub API calls
- `gitpython` - For cloning repositories
- `pathlib` - (Built-in) For file path handling
- `json`, `os`, `sys`, `time` - (Built-in) Standard library modules

## 🔑 GitHub Token Setup

This script requires a GitHub Personal Access Token to authenticate API requests.

### Creating a GitHub Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → **Tokens (classic)**
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Repo Search Tool")
4. Select scopes: `public_repo` (minimum required)
5. Generate and copy your token

### Setting the Token

**⚠️ SECURITY WARNING:** Never hardcode tokens in your script. Always use environment variables.

**Linux/macOS:**
```bash
export GITHUB_TOKEN='your_token_here'
```

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN="your_token_here"
```

**Windows (Command Prompt):**
```cmd
set GITHUB_TOKEN=your_token_here
```

> **Note:** For permanent setup, add the token to your system's environment variables or use a `.env` file with a package like `python-dotenv`.

## 🚀 Usage

1. **Run the script:**
```bash
   python git_scraper.py
```

2. **Enter your search keyword** when prompted:
```
   Enter keyword to search for repositories: machine-learning
```

3. **Wait for completion.** The script will:
   - Search for up to 100 repositories matching your keyword
   - Save metadata to `repos.json`
   - Clone repositories to `cloned_repos/` folder

## 📂 Output

### `repos.json`
Contains metadata for all found repositories:
```json
[
    {
        "name": "repo-name",
        "full_name": "owner/repo-name",
        "description": "Repository description...",
        "language": "Python",
        "created_at": "2023-01-15T10:30:00Z",
        "clone_url": "https://github.com/owner/repo-name.git",
        "stars": 1234
    }
]
```

### `cloned_repos/` folder
Contains cloned repositories, each in its own subdirectory.

## ⚙️ Configuration

You can modify these parameters in the code:

| Parameter | Location | Default | Description |
|-----------|----------|---------|-------------|
| Search limit | `search_repos()` call | `100` | Max repositories per search (GitHub limit: 100) |
| Clone directory | `clone_repos()` call | `"cloned_repos"` | Base directory for cloned repos |
| Clone depth | `Repo.clone_from()` | `depth=1` | Shallow clone (latest commit only) |
| Rate limit delay | `time.sleep()` | `2` seconds | Pause between clone operations |

## ⚠️ Limitations

- **GitHub API rate limits:** 
  - Authenticated: 5,000 requests/hour
  - Each search and clone operation counts toward this limit
- **Search results:** Maximum 100 repositories per search (GitHub API limitation)
- **Clone operations:** Includes a 2-second delay between clones to avoid overwhelming GitHub

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "ERROR: Please set your GitHub token" | Set the `GITHUB_TOKEN` environment variable |
| "GitHub API Error 401" | Your token is invalid or expired - generate a new one |
| "GitHub API Error 403" | Rate limit exceeded - wait an hour or check token permissions |
| "Failed to clone [repo]" | Check internet connection, verify Git is installed, or try a smaller repo |
