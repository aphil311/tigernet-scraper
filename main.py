#!/usr/bin/env python3
"""
Main entry point for the application.

HOW TO USE THE SCRAPER MODULE:
-----------------------------
1. Import the scraper module:
   from scraper import scrape_url, Scraper

2. Pass a URL to scrape using the convenience function:
   import asyncio

   async def main_logic(url):
       # Simple usage with selectors
       result = await scrape_url(
           url,
           selectors={
               "heading": "h1",
               "content": ".content"
           },
           take_screenshot=True
       )

       if result['status'] == 'success':
           print(f"Scraped: {result['title']}")
           print(f"Data: {result['data']}")
       else:
           print(f"Error: {result['error']}")

3. Or use the Scraper class for more control:
   async def advanced_scrape():
       scraper = Scraper(headless=False)  # Show browser
       await scraper.start()

       # Define custom actions
       async def click_and_scrape(page):
           await page.click("#load-more")
           await page.wait_for_timeout(2000)

       result = await scraper.scrape(
           url,
           custom_actions=click_and_scrape,
           wait_for_selector=".content"
       )
       await scraper.close()

4. Command line usage:
   python main.py --url "https://example.com"
   python main.py --url "https://example.com" --heading "h1" --output results.json
"""

import argparse
import asyncio
import json
import sys

from scraper import scrape_url, Scraper


def main():
    """Main function that processes command-line arguments and runs scraper."""
    parser = argparse.ArgumentParser(
        description="TigerNet Scraper - Tool for scraping and processing data"
    )

    parser.add_argument(
        "--url",
        type=str,
        help="URL to scrape"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path for results (JSON format)"
    )
    parser.add_argument(
        "--screenshot",
        action="store_true",
        help="Take a screenshot of the page"
    )
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Show browser window (non-headless mode)"
    )
    parser.add_argument(
        "--selector",
        action="append",
        metavar="FIELD:SELECTOR",
        help="Add a selector in format 'field:css_selector'. Can be used multiple times. Example: 'title:h1' 'content:.article-body'"
    )

    args = parser.parse_args()

    # If no URL provided, show usage and exit
    if not args.url:
        print(__doc__)
        print("\nERROR: --url is required\n")
        parser.print_help()
        return 1

    # Parse selectors from command line
    selectors = {}
    if args.selector:
        for sel in args.selector:
            if ':' not in sel:
                print(f"Warning: Invalid selector format '{sel}'. Use 'field:selector'")
                continue
            field, selector = sel.split(':', 1)
            selectors[field.strip()] = selector.strip()

    print(f"Starting TigerNet Scraper...")
    print(f"URL: {args.url}")
    print(f"Headless: {not args.visible}")
    print(f"Selectors: {selectors if selectors else '(none - will scrape full page)'}")

    # Run the scraper
    try:
        result = asyncio.run(scrape_url(
            url=args.url,
            headless=not args.visible,
            selectors=selectors if selectors else None,
            take_screenshot=args.screenshot
        ))

        # Output results
        if result['status'] == 'success':
            print(f"\n✓ Scraping completed successfully!")
            print(f"  Title: {result['title']}")
            print(f"  Content length: {len(result['content'])} characters")

            if result['data']:
                print(f"  Extracted data:")
                for field, value in result['data'].items():
                    if value and len(str(value)) > 100:
                        print(f"    {field}: {str(value)[:100]}...")
                    else:
                        print(f"    {field}: {value}")

            if result['screenshot']:
                print(f"  Screenshot: {result['screenshot']}")

            # Save to file if output specified
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\nResults saved to: {args.output}")

            return 0
        else:
            print(f"\n✗ Scraping failed!")
            print(f"  Error: {result['error']}")
            return 1

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
