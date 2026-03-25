"""Scraper module for TigerNet."""

import asyncio
import re
from typing import Any

from .auth import login, load_session, save_session
from .company_lookup import get_company_id
from .models import AlumRecord
from .utils import take_screenshot
from playwright.async_api import Page


async def search(
    netid: str,
    password: str,
    company: str,
    orgs: list[str],
    site: str = "https://tigernet.princeton.edu",
) -> list[str]:
    """Search for alumni by company and optional org filters. Returns list of user IDs."""
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
                try:
                    await page.wait_for_selector("h2", timeout=5000)
                except Exception:
                    await asyncio.sleep(1)

            # Also wait for profile cards/links to be present
            # Try various selectors for result cards
            card_selectors = [
                '[data-testid*="profile-card"]',
                '[data-testid*="user-card"]',
                ".profile-card",
                ".user-card",
                'a[href*="/users/"]:not([aria-hidden="true"])',
            ]
            for selector in card_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    print(f"Found results with selector: {selector}")
                    break
                except Exception:
                    continue

            await take_screenshot(page, "05_after_navigate_to_search")

            # Extract all user IDs from the results page using Playwright
            links = page.locator('a[href*="/users/"]:not([aria-hidden="true"])')
            count = await links.count()

            user_ids = set()
            pattern = re.compile(r"/users/(\d+)")
            for i in range(count):
                link = links.nth(i)
                href = await link.get_attribute("href")
                if href:
                    match = pattern.search(href)
                    if match:
                        user_ids.add(match.group(1))

            idx = 0
            for id in user_ids:
                if idx == 0:
                    record = await _parse_record(page, site, id)
                    print(f"Sample record for user ID {id}: {record}")
                    idx += 1
                else:
                    break

            print(f"Found {len(user_ids)} user IDs on the page")
            return list(user_ids)

        finally:
            await context.close()
            await browser.close()


async def _apply_filters(page: Any, company: str, orgs: list[str] | None) -> None:
    """Apply search filters to the page."""
    raise NotImplementedError("_apply_filters not yet implemented")


async def _paginate(page: Any) -> list[AlumRecord]:
    """Yield per-page batches of records."""
    raise NotImplementedError("_paginate not yet implemented")


async def _parse_record(page: Page, site: str, user_id: str) -> AlumRecord:
    """Extract alumni data from an individual profile page."""
    await page.goto(f"{site}/users/{user_id}", timeout=60000)

    # Wait for experiences section to load
    await page.wait_for_selector(
        '[data-testid="block-experiences-experience"]', timeout=60000
    )

    # Extract name
    name = await page.locator('[data-testid="user-profile-header-v2"] h3').inner_text()

    await take_screenshot(page, f"10_after_navigate_to_profile_{user_id}")

    # Use JavaScript to extract email, class_year, student_activities, experiences
    extracted = await page.evaluate("""() => {
        const data = {
            email: null,
            class_year: null,
            student_activities: null,
            experiences: []
        };

        // 1. Find email in Contact block - look for label "Email" or "Contact"
        const labels = document.querySelectorAll('[class*="sc-51dca075-2"]');
        for (const label of labels) {
            const text = label.textContent.trim().toLowerCase();
            const row = label.closest('[class*="sc-51dca075-0"]');
            if (!row) continue;

            // Email: look for "email" in label
            if (text.includes("email")) {
                const mailto = row.querySelector('a[href^="mailto:"]');
                if (mailto) {
                    data.email = mailto.href.replace(/^mailto:/, '').split('?')[0];
                }
            }

            // Class Year: label contains "class" and "year"
            if (text.includes("class") && text.includes("year")) {
                const badge = row.querySelector('[data-testid="display-attribute-select"]');
                if (badge) data.class_year = badge.textContent.trim();
            }

            // Student Activities
            if (text.includes("student activities")) {
                const container = row.parentElement;
                if (container) {
                    const siblings = container.querySelectorAll(':scope > [class*="bbQgfJ"]');
                    const acts = [];
                    for (const sib of siblings) {
                        const badge = sib.querySelector('[data-testid="display-attribute-select"]');
                        if (badge) acts.push(badge.textContent.trim());
                    }
                    if (acts.length) data.student_activities = acts.join(", ");
                }
            }
        }

        // 2. Extract work experiences
        const expBlock = document.querySelector('[data-testid="block-experiences-experience"]');
        if (expBlock) {
            const cards = expBlock.querySelectorAll('[class*="LggnV"]');
            data.experiences = Array.from(cards).map(card => {
                const parts = card.querySelectorAll('[class*="gLbFu"]');
                const title = parts[0]?.textContent.trim() || "";
                const company = parts[1]?.textContent.trim() || "";
                return title + " at " + company;
            }).filter(e => e); // remove empty
        }

        return data;
    }""")

    email = extracted.get("email")
    class_year = extracted.get("class_year")
    student_activities = extracted.get("student_activities")
    experiences = extracted.get("experiences", [])
    experience = ", ".join(experiences) if experiences else None

    return AlumRecord(
        name=name,
        class_year=class_year,
        degree=None,
        company=None,
        title=None,
        org=student_activities,
        email=email,
        linkedin=None,
        location=None,
    )
