"""Authentication module for TigerNet scraper."""

import asyncio
import json
import os
from typing import Any

from .utils import ensure_screenshot_dir, take_screenshot

SESSION_FILE = "session.json"


async def handle_cookie_popup(page: Any) -> None:
    """Handle cookie consent popups that may appear after login.

    Checks for cookie notice text and clicks the accept button if present.
    Uses async waiting instead of blocking timeouts.
    """
    try:
        # Check for various cookie notice text variations
        cookie_notice_selectors = [
            'text="Our website uses cookies"',
            "text=cookies",
            'text="Cookie"',
            'text="Privacy"',
            'text="We use cookies"',
        ]

        cookie_notice = None
        for selector in cookie_notice_selectors:
            try:
                locator = page.locator(selector)
                if await locator.count() > 0:
                    cookie_notice = locator
                    # Debug: print what we found
                    print(f"Found cookie notice with selector: {selector}")
                    break
            except Exception:
                continue

        if cookie_notice:
            # Look for various accept button text variations
            accept_button_selectors = [
                'button:has-text("Accept all cookies")',
                'button:has-text("Accept All")',
                'button:has-text("Accept")',
                'button:has-text("Agree")',
                'button:has-text("OK")',
                'button:has-text("I Agree")',
                'button:has-text("Accept all")',
            ]

            accept_button = None
            for selector in accept_button_selectors:
                try:
                    locator = page.locator(selector)
                    if await locator.count() > 0:
                        accept_button = locator
                        # Debug: print what we found
                        print(f"Found accept button with selector: {selector}")
                        break
                except Exception:
                    continue

            if accept_button:
                await accept_button.first.click(timeout=5000)
                # Wait for the cookie notice to disappear using async wait
                try:
                    await cookie_notice.wait_for(state="hidden", timeout=2000)
                except Exception:
                    # If hidden state wait fails, fall back to a short sleep
                    await asyncio.sleep(0.5)
                print("Clicked cookie accept button")
            else:
                print("Cookie notice found but no accept button located")
        else:
            # Debug: let's see what text is actually on the page
            # Uncomment the following lines for debugging if needed
            page_content = await page.content()
            if "cookie" in page_content.lower():
                print("Page contains 'cookie' but our selectors didn't match")
            pass
    except Exception as e:
        # If anything goes wrong, silently continue - no cookie popup or already handled
        print(f"Cookie popup handling encountered an error (continuing): {e}")
        pass


async def load_session(context: Any) -> bool:
    """Load cookies from session.json, return True if valid."""
    if not os.path.exists(SESSION_FILE):
        return False

    try:
        with open(SESSION_FILE, "r") as f:
            cookies = json.load(f)

        if not cookies:
            return False

        # Add cookies to context
        await context.add_cookies(cookies)

        # Basic validation: check if we have any TigerNet cookies
        # A more robust check would require a test navigation
        return len(cookies) > 0
    except (json.JSONDecodeError, KeyError):
        return False


async def login(page: Any, netid: str, password: str) -> None:
    """Drive CAS login form to authenticate."""
    # Step 1: Navigate to TigerNet login page with longer timeout
    await page.goto("https://tigernet.princeton.edu/login", timeout=60000)
    await page.wait_for_load_state("domcontentloaded", timeout=30000)
    await take_screenshot(page, "01_login")

    # Step 4: Fill in credentials
    await page.fill("input[name='username']", netid)
    await page.fill("input[name='password']", password)
    await take_screenshot(page, "02_credentials_filled")

    # Step 5: Submit the form
    await page.click("button[id='submitBtn']")
    await take_screenshot(page, "03_after_submit")

    # Step 6: Wait for login to complete - wait for navigation to complete
    await page.wait_for_load_state("domcontentloaded", timeout=60000)
    # Wait for network to be idle after redirect (ensures login fully processes)
    try:
        await page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        # If networkidle times out, the page may still be usable; fall back to a short sleep
        await asyncio.sleep(1)

    # Handle any cookie consent popups that may have appeared
    await handle_cookie_popup(page)
    # await take_screenshot(page, "06_after_login_complete")


async def save_session(context: Any) -> None:
    """Persist cookies after successful login."""
    cookies = await context.cookies()
    with open(SESSION_FILE, "w") as f:
        json.dump(cookies, f, indent=2)
