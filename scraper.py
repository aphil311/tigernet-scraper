#!/usr/bin/env python3
"""
Web scraping module using Playwright.

This module provides a boilerplate for web scraping with Playwright.
It includes:
- Async scraping functionality
- Browser context management
- Error handling
- Screenshot capability for debugging

Usage:
    from scraper import scrape_url

    # Async usage:
    import asyncio
    result = asyncio.run(scrape_url("https://example.com"))

    # Or use Scraper class directly:
    scraper = Scraper()
    result = scraper.scrape("https://example.com")
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Scraper:
    """
    A Playwright-based web scraper with async support.

    Attributes:
        headless: Whether to run browser in headless mode (default: True)
        timeout: Default timeout in milliseconds (default: 30000)
        screenshot_dir: Directory to save screenshots (default: "./screenshots")
    """

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 30000,
        screenshot_dir: str = "./screenshots"
    ):
        """
        Initialize the scraper.

        Args:
            headless: Run browser in headless mode
            timeout: Default timeout in milliseconds
            screenshot_dir: Directory path for saving screenshots
        """
        self.headless = headless
        self.timeout = timeout
        self.screenshot_dir = screenshot_dir
        self.playwright = None
        self.browser: Optional[Browser] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self) -> None:
        """Start the Playwright browser instance."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        logger.info("Browser started successfully")

    async def close(self) -> None:
        """Close the browser and cleanup resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")

    async def create_context(self) -> BrowserContext:
        """
        Create a new browser context.

        Returns:
            BrowserContext: A new browser context
        """
        if not self.browser:
            raise RuntimeError("Browser not started. Call start() first or use async context manager.")

        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        return context

    async def scrape(
        self,
        url: str,
        selectors: Optional[Dict[str, str]] = None,
        wait_for_selector: Optional[str] = None,
        take_screenshot: bool = False,
        custom_actions: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Scrape a URL and extract data.

        Args:
            url: The URL to scrape
            selectors: Dictionary of {field_name: css_selector} for data extraction
            wait_for_selector: CSS selector to wait for before extracting (optional)
            take_screenshot: Whether to save a screenshot (default: False)
            custom_actions: Optional async function that takes (page) and performs custom actions

        Returns:
            Dictionary containing:
                - 'status': 'success' or 'error'
                - 'url': The scraped URL
                - 'title': Page title
                - 'content': Full page HTML content
                - 'data': Extracted data based on selectors
                - 'screenshot': Path to screenshot if taken
                - 'error': Error message if status is 'error'
        """
        result: Dict[str, Any] = {
            'status': 'error',
            'url': url,
            'title': '',
            'content': '',
            'data': {},
            'screenshot': None,
            'error': 'Unknown error occurred'
        }

        try:
            if not self.browser:
                await self.start()

            context = await self.create_context()
            page = await context.new_page()

            # Set default timeout
            page.set_default_timeout(self.timeout)

            logger.info(f"Navigating to: {url}")
            response = await page.goto(url, wait_until='domcontentloaded')

            if not response or not response.ok:
                result['error'] = f"Failed to load page: {response.status if response else 'No response'}"
                return result

            # Wait for specific selector if provided
            if wait_for_selector:
                logger.info(f"Waiting for selector: {wait_for_selector}")
                await page.wait_for_selector(wait_for_selector, timeout=self.timeout)

            # Execute custom actions if provided
            if custom_actions:
                logger.info("Executing custom actions...")
                await custom_actions(page)

            # Extract data based on selectors
            if selectors:
                logger.info("Extracting data using selectors...")
                for field, selector in selectors.items():
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            result['data'][field] = await element.text_content()
                        else:
                            result['data'][field] = None
                            logger.warning(f"Selector not found: {selector}")
                    except Exception as e:
                        logger.warning(f"Error extracting '{field}': {e}")
                        result['data'][field] = None

            # Get page content
            result['title'] = await page.title()
            result['content'] = await page.content()

            # Take screenshot if requested
            if take_screenshot:
                import os
                os.makedirs(self.screenshot_dir, exist_ok=True)
                safe_url = url.replace('://', '_').replace('/', '_').replace('?', '_')[:50]
                screenshot_path = f"{self.screenshot_dir}/{safe_url}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                result['screenshot'] = screenshot_path
                logger.info(f"Screenshot saved: {screenshot_path}")

            result['status'] = 'success'
            result['error'] = None

            await context.close()

        except Exception as e:
            logger.error(f"Scraping error: {e}", exc_info=True)
            result['error'] = str(e)

        return result


async def scrape_url(
    url: str,
    headless: bool = True,
    selectors: Optional[Dict[str, str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to scrape a URL without managing the Scraper instance.

    Args:
        url: The URL to scrape
        headless: Whether to run browser in headless mode
        selectors: Dictionary of {field_name: css_selector} for data extraction
        **kwargs: Additional arguments passed to Scraper.scrape()

    Returns:
        Dictionary with scraping results (same as Scraper.scrape())

    Example:
        result = await scrape_url(
            "https://example.com",
            selectors={
                "heading": "h1",
                "content": ".content p"
            }
        )
    """
    async with Scraper(headless=headless) as scraper:
        return await scraper.scrape(url, selectors=selectors, **kwargs)


if __name__ == "__main__":
    # Example usage when run directly
    import sys

    async def example():
        """Example scraping function."""
        url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"

        result = await scrape_url(
            url,
            selectors={
                "title": "title",
                "main_heading": "h1",
                "first_paragraph": "p"
            },
            take_screenshot=True
        )

        if result['status'] == 'success':
            print(f"Title: {result['title']}")
            print(f"Extracted data: {result['data']}")
            if result['screenshot']:
                print(f"Screenshot: {result['screenshot']}")
        else:
            print(f"Error: {result['error']}")

    asyncio.run(example())
