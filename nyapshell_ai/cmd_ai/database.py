"""
cmd_ai/database.py
------------------
Local command knowledge base.
Provides fast fuzzy lookup before hitting the AI API.
"""

import json
import os
from difflib import get_close_matches

DB_PATH = os.path.join(os.path.dirname(__file__), "commands_db.json")


def load_db() -> dict:
    """Load the local command database."""
    with open(DB_PATH, "r") as f:
        return json.load(f)


def fuzzy_lookup(query: str, threshold: float = 0.6) -> str | None:
    """
    Try to find a matching command in the local database
    using fuzzy string matching.

    Returns the command string if found, else None.
    """
    db = load_db()
    keys = list(db.keys())
    matches = get_close_matches(query.lower(), keys, n=1, cutoff=threshold)
    if matches:
        return db[matches[0]]
    return None


def list_all() -> dict:
    """Return the full command database."""
    return load_db()


def add_entry(description: str, command: str) -> None:
    """Add a new entry to the local database."""
    db = load_db()
    db[description.lower()] = command
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)
