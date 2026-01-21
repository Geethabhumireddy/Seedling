"""
Caching utility for analysis results.

Implements local file-based caching to reduce redundant API calls
and provide faster repeat analyses.
"""

import json
import os
from pathlib import Path
from typing import Optional


CACHE_DIR = Path(".cache")


def _ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(exist_ok=True)


def _get_cache_key(repo_url: str, issue_number: int) -> str:
    """Generate a unique cache key for an issue."""
    return f"{repo_url.replace('/', '_').replace(':', '')}_issue_{issue_number}.json"


def get_cached_analysis(repo_url: str, issue_number: int) -> Optional[dict]:
    """
    Retrieve cached analysis result if available.
    
    Args:
        repo_url: GitHub repository URL
        issue_number: Issue number
        
    Returns:
        Cached analysis dict, or None if not cached
    """
    _ensure_cache_dir()
    cache_file = CACHE_DIR / _get_cache_key(repo_url, issue_number)
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    return None


def cache_analysis(repo_url: str, issue_number: int, result: dict):
    """
    Store analysis result in cache.
    
    Args:
        repo_url: GitHub repository URL
        issue_number: Issue number
        result: Analysis result to cache
    """
    _ensure_cache_dir()
    cache_file = CACHE_DIR / _get_cache_key(repo_url, issue_number)
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(result, f, indent=2)
    except Exception:
        pass  # Silently fail cache write


def clear_cache():
    """Clear all cached analyses."""
    if CACHE_DIR.exists():
        for file in CACHE_DIR.glob("*.json"):
            file.unlink()
