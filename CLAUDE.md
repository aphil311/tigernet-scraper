# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (run once or after dependency changes)
uv sync

# Run the project
uv run tigernet-scraper <company> [--orgs <orgs>] [--output <output>]

# Format code (if black is added to dependencies)
uv run black .

# Reinstall package in editable mode (if pyproject.toml changes)
uv pip install -e .
```

### Bash Commands Allowed
- `uv run tigernet-scraper` — run the scraper CLI

## Architecture

This is a Python project using [Playwright](https://playwright.dev/python/) for browser-based scraping with a src-layout structure:

```
tigernet_scraper/
├── main.py             # Entrypoint
├── auth.py             # SSO / session management
├── scraper.py          # Page navigation & extraction logic
├── filters.py          # Query building & filter application
├── exporter.py         # Excel output
├── models.py           # AlumRecord dataclass
└── session.json        # Persisted cookies (gitignored)
```

## API overview
**`main.py`** — parses args, wires everything together, owns the rich console/progress UI

**`auth.py`** - handles authentication (Princeton CAS) flow on the TigerNet website
```python
def load_session(context) -> bool  # loads cookies from session.json, returns True if valid
def login(page, netid, password) -> None  # drives CAS login form
def save_session(context) -> None  # persists cookies after successful login
```

**`scraper.py`** - handles the actual scraping of the website
```python
def search(page, company: str, orgs: list[str] | None) -> list[AlumRecord]
def _apply_filters(page, company, orgs) -> None
def _paginate(page) -> Iterator[list[AlumRecord]]  # yields per-page batches
def _parse_record(element) -> AlumRecord
```

**`filter.py*`** - filters
```python
def build_query(company: str, orgs: list[str] | None) -> dict  # search params
def validate_orgs(orgs: list[str]) -> list[str]  # normalize / warn on unknowns
```

**`exporter.py`** - handles taking the alum objects and exports them to an excel file
```python
def write_excel(records: list[AlumRecord], path: str) -> str  # returns final path
```

**`models.py`** - alum record
```python
@dataclass
class AlumRecord:
    name: str
    class_year: int | None
    degree: str | None
    company: str | None
    title: str | None
    org: str | None        # concentration/dept
    email: str | None
    linkedin: str | None
    location: str | None
```

# Tips and tricks
*@Claude please insert anything here that is useful to you in solving problems in this repository.*
1. Any time you write new code you must run `uv run tigernet-scraper --test Google -m 10` to observe if there are obvious errors in the program. If there are, you must fix them.