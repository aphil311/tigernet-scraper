"""Scraper module for TigerNet."""

import asyncio
from typing import Any, Iterator

from .auth import load_session, login, save_session
from .models import AlumRecord
from .auth import _ensure_screenshot_dir, _take_screenshot


async def search(
    netid: str,
    password: str,
    company: str,
    orgs: list[str],
    site: str = "https://tigernet.princeton.edu/people",
) -> list[AlumRecord]:
    """Search for alumni by company and optional org filters."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Need to login; login() handles navigation
            await login(page, netid, password)
            await save_session(context)  # Persist cookies after successful login

            # Navigate to the site (should be logged in now)
            await page.goto(site, timeout=60000)
            await page.wait_for_load_state("domcontentloaded", timeout=30000)

            # Wait for the Members header to appear, indicating results are fully loaded
            try:
                await page.wait_for_selector("h2:has-text('Members')", timeout=15000)
            except Exception:
                # Fallback: wait for any h2 element (selector might differ)
                try:
                    await page.wait_for_selector("h2", timeout=5000)
                except Exception:
                    # As last resort, short sleep
                    await asyncio.sleep(1)

            await _take_screenshot(page, "05_after_navigate_to_search")

            # TODO: Implement actual search logic: apply filters, paginate, parse records
            return []
        finally:
            await context.close()
            await browser.close()


async def _apply_filters(page: Any, company: str, orgs: list[str] | None) -> None:
    """Apply search filters to the page."""
    pass


async def _paginate(page: Any) -> Iterator[list[AlumRecord]]:
    """Yield per-page batches of records."""
    pass


async def _parse_record(element: Any) -> AlumRecord:
    """Parse a single record element into AlumRecord."""
    pass
