# TigerNet Scraper

A simple web scraper for TigerNet built with Playwright and Typer.

## Project Structure

```
tigernet-scraper/
├── src/
│   └── tigernet_scraper/
│       ├── __init__.py
│       └── main.py          # CLI entry point
├── tests/                   # Test files (to be added)
├── pyproject.toml           # Project dependencies
├── uv.lock                 # Locked dependencies
├── README.md               # This file
└── CLAUDE.md               # Claude Code instructions
```

## Roadmap

- [x] Basic CLI with Typer
- [ ] Implement Playwright browser automation
- [ ] Add URL scraping logic
- [ ] Support CSS selectors for targeted extraction
- [ ] Add screenshot capability
- [ ] JSON output formatting
- [ ] Error handling and retries
- [ ] Unit tests

## Installation

```bash
# Install dependencies with uv
uv sync

# Install Playwright browsers (one-time setup)
uv run playwright install chromium
```

## Usage

```bash
# Basic usage with required company argument
uv run python main.py "CompanyName"

# With optional organizations
uv run python main.py "CompanyName" -o "Org1" -o "Org2"

# Show help
uv run python main.py --help
```

## Output

The scraper outputs results to stdout by default. Use `--output` (when implemented) to save to a file.
