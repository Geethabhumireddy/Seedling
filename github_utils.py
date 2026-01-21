"""
GitHub API utilities for fetching and parsing issues.

This module handles all GitHub API interactions, including issue fetching,
comment retrieval, and error handling for network requests.
"""

import requests
import os


def fetch_github_issue(repo_url: str, issue_number: int) -> dict:
    """
    Fetch a GitHub issue and its comments from the GitHub API.
    
    Args:
        repo_url: Full GitHub repository URL (e.g., https://github.com/facebook/react)
        issue_number: Issue number to fetch
        
    Returns:
        Dictionary containing:
        - "title": Issue title
        - "body": Issue description
        - "comments": Concatenated comment text
        - "error": Error message if fetching fails
        
    Handles edge cases:
        - Missing comments (issues with no discussion)
        - Long issue bodies (truncated gracefully by API)
        - Rate limiting (returns API error)
        - Invalid repository URLs
    """
    try:
        # Parse repository owner and name from URL
        owner, repo = repo_url.replace("https://github.com/", "").split("/")[:2]

        # Setup headers with GitHub token if available (for higher rate limits)
        headers = {}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"

        # GitHub API endpoints
        issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        comments_url = f"{issue_url}/comments"

        # Fetch issue details and comments
        issue_resp = requests.get(issue_url, headers=headers, timeout=10)
        comments_resp = requests.get(comments_url, headers=headers, timeout=10)

        if issue_resp.status_code != 200:
            return {"error": f"GitHub API error: {issue_resp.status_code}"}

        # Parse JSON responses
        issue = issue_resp.json()
        comments = comments_resp.json() if comments_resp.status_code == 200 else []

        # Combine comments into single text (handles empty comment case)
        comments_text = "\n".join([c.get("body", "") for c in comments]) if comments else ""

        return {
            "title": issue.get("title", ""),
            "body": issue.get("body", ""),
            "comments": comments_text
        }

    except ValueError:
        return {"error": "Invalid GitHub URL format"}
    except requests.exceptions.Timeout:
        return {"error": "Request timeout - GitHub server took too long"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}
