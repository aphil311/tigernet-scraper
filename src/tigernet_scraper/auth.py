"""Authentication module for TigerNet scraper."""

import json
import os
from datetime import datetime
from typing import Any

SESSION_FILE = "session.json"
SCREENSHOT_DIR = "screenshots"


def _ensure_screenshot_dir() -> None:
    """Create screenshots directory if it doesn't exist."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def _take_screenshot(page: Any, name: str) -> str:
    """Take a screenshot and save it with timestamp."""
    _ensure_screenshot_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{SCREENSHOT_DIR}/{timestamp}_{name}.png"
    page.screenshot(path=filename)
    return filename


def handle_cookie_popup(page: Any) -> None:
    """Handle cookie consent popups that may appear after login.

    Checks for cookie notice text and clicks the accept button if present.
    """
    try:
        # Check for various cookie notice text variations
        cookie_notice_selectors = [
            'text="Our website uses cookies"',
            'text=cookies',
            'text="Cookie"',
            'text="Privacy"',
            'text="We use cookies"'
        ]

        cookie_notice = None
        for selector in cookie_notice_selectors:
            try:
                locator = page.locator(selector)
                if locator.count > 0:
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
                'button:has-text("Accept all")'
            ]

            accept_button = None
            for selector in accept_button_selectors:
                try:
                    locator = page.locator(selector)
                    if locator.count > 0:
                        accept_button = locator
                        # Debug: print what we found
                        print(f"Found accept button with selector: {selector}")
                        break
                except Exception:
                    continue

            if accept_button:
                accept_button.first.click(timeout=5000)
                # Wait for the cookie notice to disappear
                page.wait_for_timeout(2000)
                print("Clicked cookie accept button")
            else:
                print("Cookie notice found but no accept button located")
        else:
            # Debug: let's see what text is actually on the page
            # Uncomment the following lines for debugging if needed
            page_content = page.content()
            if "cookie" in page_content.lower():
                print("Page contains 'cookie' but our selectors didn't match")
                # print(f"Page title: {page.content()}")
            pass
    except Exception as e:
        # If anything goes wrong, silently continue - no cookie popup or already handled
        print(f"Cookie popup handling encountered an error (continuing): {e}")
        pass


def load_session(context: Any) -> bool:
    """Load cookies from session.json, return True if valid."""
    if not os.path.exists(SESSION_FILE):
        return False

    try:
        with open(SESSION_FILE, "r") as f:
            cookies = json.load(f)

        if not cookies:
            return False

        # Add cookies to context
        context.add_cookies(cookies)

        # Basic validation: check if we have any TigerNet cookies
        # A more robust check would require a test navigation
        return len(cookies) > 0
    except (json.JSONDecodeError, KeyError):
        return False


def login(page: Any, netid: str, password: str) -> None:
    """Drive CAS login form to authenticate."""
    # Step 1: Navigate to TigerNet login page with longer timeout
    page.goto("https://tigernet.princeton.edu/login", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    _take_screenshot(page, "01_login")

    # Step 4: Fill in credentials
    page.fill("input[name='username']", netid)
    page.fill("input[name='password']", password)
    _take_screenshot(page, "02_credentials_filled")

    # Step 5: Submit the form
    page.click("button[id='submitBtn']")
    _take_screenshot(page, "03_after_submit")

    # Step 6: Wait for login to complete with more generous timeout
    page.wait_for_load_state("domcontentloaded", timeout=60000)
    # Extra wait for potential redirects and dynamic content
    page.wait_for_timeout(3000)
    page.goto("https://tigernet.princeton.edu/people", timeout=60000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    page.wait_for_timeout(10000)
    # Handle any cookie consent popups that may have appeared
    handle_cookie_popup(page)
    _take_screenshot(page, "06_after_login_complete")


def save_session(context: Any) -> None:
    """Persist cookies after successful login."""
    cookies = context.cookies()
    with open(SESSION_FILE, "w") as f:
        json.dump(cookies, f, indent=2)
