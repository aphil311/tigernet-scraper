"""Tests for auth module."""

import json
import os

import pytest

from tigernet_scraper.auth import load_session, save_session, SESSION_FILE


@pytest.fixture
def clean_session_file():
    """Ensure session file is removed before and after test."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    yield
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


class MockContext:
    """Simple mock for browser context."""

    def __init__(self):
        self._cookies = []

    def add_cookies(self, cookies):
        self._cookies = cookies

    def cookies(self):
        """Return cookies list (mimics Playwright context.cookies())."""
        return self._cookies


def test_load_session_missing_file(clean_session_file):
    """load_session should return False when session file does not exist."""
    mock_ctx = MockContext()
    result = load_session(mock_ctx)
    assert result is False
    assert mock_ctx._cookies == []


def test_load_session_valid(clean_session_file):
    """load_session should return True and add cookies when file exists and contains valid data."""
    mock_ctx = MockContext()
    dummy_cookies = [{"name": "test", "value": "value", "domain": ".princeton.edu"}]
    with open(SESSION_FILE, "w") as f:
        json.dump(dummy_cookies, f)

    result = load_session(mock_ctx)
    assert result is True
    assert mock_ctx._cookies == dummy_cookies


def test_load_session_invalid_json(clean_session_file):
    """load_session should return False if session file contains invalid JSON."""
    with open(SESSION_FILE, "w") as f:
        f.write("not valid json")

    mock_ctx = MockContext()
    result = load_session(mock_ctx)
    assert result is False
    assert mock_ctx._cookies == []


def test_load_session_empty_file(clean_session_file):
    """load_session should return False if session file is empty."""
    with open(SESSION_FILE, "w") as f:
        f.write("")

    mock_ctx = MockContext()
    result = load_session(mock_ctx)
    assert result is False
    assert mock_ctx._cookies == []


def test_save_session(clean_session_file):
    """save_session should write cookies to session.json."""
    mock_ctx = MockContext()
    dummy_cookies = [
        {"name": "cookie1", "value": "val1", "domain": ".princeton.edu"},
        {"name": "cookie2", "value": "val2", "domain": ".princeton.edu"},
    ]
    mock_ctx._cookies = dummy_cookies

    save_session(mock_ctx)

    assert os.path.exists(SESSION_FILE)
    with open(SESSION_FILE, "r") as f:
        loaded = json.load(f)
    assert loaded == dummy_cookies
