# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Install Playwright browsers (required once after uv sync)
uv run playwright install chromium

# Run the scraper
uv run python main.py --url "https://example.com"
uv run python main.py --url "https://example.com" --selector "title:h1" --selector "body:.content" --screenshot --output results.json

# Format code
uv run black .

# Run scraper module directly
uv run python scraper.py "https://example.com"
```

## Architecture

This is a two-file Python project using [Playwright](https://playwright.dev/python/) for browser-based scraping:

- **`scraper.py`** — Core scraping logic. Contains the `Scraper` class (async context manager wrapping a Playwright Chromium browser) and the `scrape_url()` convenience function. The `Scraper.scrape()` method accepts CSS `selectors` dict, an optional `wait_for_selector`, a `custom_actions` async callback for interactive page manipulation, and a `take_screenshot` flag. Results are returned as a dict with keys: `status`, `url`, `title`, `content`, `data`, `screenshot`, `error`.

- **`main.py`** — CLI entry point. Parses `--url`, `--selector FIELD:CSS`, `--output`, `--screenshot`, and `--visible` flags, then delegates to `scrape_url()`. Outputs JSON to a file when `--output` is specified.

The scraper always uses Chromium, sets a 1920×1080 viewport, and mimics a Windows Chrome user-agent string.
