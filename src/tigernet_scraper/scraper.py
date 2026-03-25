"""Scraper module for TigerNet."""

import asyncio
from typing import Any

from .auth import login, load_session, save_session
from .company_lookup import get_company_id
from .models import AlumRecord
from .utils import take_screenshot


async def search(
    netid: str,
    password: str,
    company: str,
    orgs: list[str],
    site: str = "https://tigernet.princeton.edu",
) -> list[AlumRecord]:
    """Search for alumni by company and optional org filters."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Try to load existing session first
            if not await load_session(context):
                # No valid session, need to login
                await login(page, netid, password)
                await save_session(context)  # Persist cookies after successful login

            # Determine target URL with company ID if available
            company_id = get_company_id(company)
            if company_id:
                print(f"Found company ID for '{company}': {company_id}")
                # Build URL with company_ids query parameter
                base_url = site.rstrip("/")
                target_url = f"{base_url}/people?company_ids={company_id}"
            else:
                print(
                    f"Company ID not found for '{company}'. Navigating to {site} without filter."
                )
                target_url = site

            # Navigate to the target page
            await page.goto(target_url, timeout=60000)
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

            await take_screenshot(page, "05_after_navigate_to_search")

            # TODO: Implement actual search logic: apply filters, paginate, parse records
            return []
        finally:
            await context.close()
            await browser.close()


async def _apply_filters(page: Any, company: str, orgs: list[str] | None) -> None:
    """Apply search filters to the page."""
    raise NotImplementedError("_apply_filters not yet implemented")


async def _paginate(page: Any) -> list[AlumRecord]:
    """Yield per-page batches of records."""
    raise NotImplementedError("_paginate not yet implemented")


async def _parse_record(element: Any) -> AlumRecord:
    """Parse a single record element into AlumRecord."""
    raise NotImplementedError("_parse_record not yet implemented")
