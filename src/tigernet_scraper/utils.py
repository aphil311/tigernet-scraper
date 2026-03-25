"""Utility functions for TigerNet scraper."""

from datetime import datetime
from pathlib import Path

SCREENSHOT_DIR = Path("screenshots")


def ensure_screenshot_dir() -> None:
    """Create screenshots directory if it doesn't exist."""
    SCREENSHOT_DIR.mkdir(exist_ok=True)


async def take_screenshot(page, name: str) -> str:
    """Take a screenshot and save it with a timestamp."""
    ensure_screenshot_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = SCREENSHOT_DIR / f"{timestamp}_{name}.png"
    await page.screenshot(path=str(filename))
    return str(filename)
