"""Scraper module for TigerNet."""

from typing import Any, Iterator

from .auth import load_session, login, save_session
from .models import AlumRecord


def search(
    netid: str,
    password: str,
    company: str,
    orgs: list[str],
    site: str = "https://tigernet.princeton.edu",
) -> list[AlumRecord]:
    """Search for alumni by company and optional org filters."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Need to login; login() handles navigation
            login(page, netid, password)
            save_session(context)

            # Navigate to the site (should be logged in now)
            page.goto(site)
            # TODO: Implement actual search logic: apply filters, paginate, parse records
            return []
        finally:
            context.close()
            browser.close()


def _apply_filters(page: Any, company: str, orgs: list[str] | None) -> None:
    """Apply search filters to the page."""
    pass


def _paginate(page: Any) -> Iterator[list[AlumRecord]]:
    """Yield per-page batches of records."""
    pass


def _parse_record(element: Any) -> AlumRecord:
    """Parse a single record element into AlumRecord."""
    pass
