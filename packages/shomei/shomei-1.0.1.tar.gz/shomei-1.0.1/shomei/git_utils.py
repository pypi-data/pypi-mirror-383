"""Git repository operations for shōmei."""

import subprocess
from datetime import datetime


def get_git_user_email():
    """
    Get the current git user email from git config.

    Returns:
        str or None: The git user email if found, None otherwise
    """
    try:
        result = subprocess.run(['git', 'config', 'user.email'],
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_repo_name():
    """
    Figure out the name of the current git repository.

    Extracts the repo name from the git remote origin URL.

    Returns:
        str: The repository name, or "unknown-repo" if not found
    """
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'],
                              capture_output=True, text=True, check=True)
        url = result.stdout.strip()
        # extract repo name from URLs like: https://github.com/user/repo.git
        return url.split('/')[-1].replace('.git', '')
    except subprocess.CalledProcessError:
        return "unknown-repo"


def get_commits_by_author(email):
    """
    Get all commits by a specific author email (just hashes and dates).

    Args:
        email: The author email to filter commits by

    Returns:
        list: List of dicts with 'hash' and 'date' keys
              Example: [{'hash': 'abc123', 'date': datetime(...)}, ...]
    """
    try:
        result = subprocess.run([
            'git', 'log', '--author', email, '--pretty=format:%H|%ad|%s', '--date=iso'
        ], capture_output=True, text=True, check=True)

        commits = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line and line.strip():
                parts = line.split('|', 2)
                if len(parts) >= 2:
                    commit_hash, date_str = parts[0], parts[1]
                    # parse the ISO date (format: "2025-01-09 10:30:45 +0100")
                    # remove timezone, then replace first space with T
                    clean_date = date_str.strip().split('+')[0].strip().replace(' ', 'T', 1)
                    date = datetime.fromisoformat(clean_date)
                    commits.append({'hash': commit_hash, 'date': date})

        return commits
    except subprocess.CalledProcessError:
        return []
