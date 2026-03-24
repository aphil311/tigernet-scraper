"""Tests for scraper module."""

from unittest.mock import MagicMock, patch

import pytest

from tigernet_scraper.scraper import search


@pytest.fixture
def mock_playwright():
    """Mock the entire Playwright sync API."""
    with patch("playwright.sync_api.sync_playwright") as mock_sync:
        # Create mocks
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()

        # The object returned by sync_playwright() is used as context manager
        mock_p = MagicMock()
        mock_p.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page

        # Configure context manager behavior
        mock_sync.return_value = mock_p
        mock_p.__enter__ = MagicMock(return_value=mock_p)
        mock_p.__exit__ = MagicMock(return_value=None)

        yield {
            "sync_playwright": mock_sync,
            "p": mock_p,
            "browser": mock_browser,
            "context": mock_context,
            "page": mock_page,
        }


def test_search_success(mock_playwright):
    """Test that search performs login flow and returns empty list."""
    # Mock auth.load_session to return False (force login)
    with patch(
        "tigernet_scraper.scraper.load_session", return_value=False
    ) as mock_load:
        with patch("tigernet_scraper.scraper.login") as mock_login:
            with patch("tigernet_scraper.scraper.save_session") as mock_save:
                result = search(
                    netid="testuser",
                    password="testpass",
                    company="Acme",
                    orgs=[],
                )

                # Verify that load_session was called with context
                mock_load.assert_called_once_with(mock_playwright["context"])
                # Since load_session returned False, login should be called
                mock_login.assert_called_once_with(
                    mock_playwright["page"], "testuser", "testpass"
                )
                # After login, save_session should be called
                mock_save.assert_called_once_with(mock_playwright["context"])
                # search should return empty list (no records yet)
                assert result == []

                # Verify browser was closed
                mock_playwright["context"].close.assert_called_once()
                mock_playwright["browser"].close.assert_called_once()


def test_search_valid_session(mock_playwright):
    """Test that when load_session returns True, login is skipped."""
    with patch("tigernet_scraper.scraper.load_session", return_value=True) as mock_load:
        with patch("tigernet_scraper.scraper.login") as mock_login:
            with patch("tigernet_scraper.scraper.save_session") as mock_save:
                result = search(
                    netid="testuser",
                    password="testpass",
                    company="Acme",
                    orgs=[],
                )
                mock_load.assert_called_once()
                mock_login.assert_not_called()
                # Even if loaded session, we may not need to save because we didn't login
                mock_save.assert_not_called()
                assert result == []
                mock_playwright["context"].close.assert_called_once()
                mock_playwright["browser"].close.assert_called_once()


def test_search_exception_cleanup(mock_playwright):
    """Test that browser resources are cleaned up even on exception."""
    # Simulate login raising an exception
    with patch("tigernet_scraper.scraper.load_session", return_value=False):
        with patch(
            "tigernet_scraper.scraper.login", side_effect=Exception("Login failed")
        ):
            with pytest.raises(Exception, match="Login failed"):
                search(
                    netid="testuser",
                    password="testpass",
                    company="Acme",
                    orgs=[],
                )
            # Still should close resources
            mock_playwright["context"].close.assert_called_once()
            mock_playwright["browser"].close.assert_called_once()
