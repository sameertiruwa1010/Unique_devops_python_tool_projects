"""
tests/test_database.py
----------------------
Unit tests for the local command database module.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cmd_ai.database import fuzzy_lookup, load_db, list_all


def test_load_db_returns_dict():
    db = load_db()
    assert isinstance(db, dict)
    assert len(db) > 0


def test_exact_match():
    result = fuzzy_lookup("check disk space")
    assert result is not None
    assert "df" in result


def test_fuzzy_match():
    # "disk space check" should fuzzy-match "check disk space"
    result = fuzzy_lookup("disk space check", threshold=0.5)
    assert result is not None


def test_no_match_returns_none():
    result = fuzzy_lookup("xyzzy completely nonsense query 12345", threshold=0.9)
    assert result is None


def test_list_all_returns_dict():
    all_cmds = list_all()
    assert isinstance(all_cmds, dict)
    assert "check disk space" in all_cmds


def test_find_large_files():
    result = fuzzy_lookup("find large files")
    assert result is not None
    assert "find" in result
    assert "-size" in result
