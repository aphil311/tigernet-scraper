<div align="center">

# 🐯 TigerNet Scraper

*Asynchronous web scraper for Princeton's TigerNet alumni directory*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![Playwright](https://img.shields.io/badge/playwright-1.40.0-green.svg)](https://playwright.dev/) [![Typer](https://img.shields.io/badge/typer-0.24.1-red.svg)](https://typer.tiangolo.com/) [![UV](https://img.shields.io/badge/uv-package%20manager-purple.svg)](https://github.com/astral-sh/uv) [![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Scrape alumni data from TigerNet with intelligent session management and company filtering.**

</div>

---

## 📖 Table of Contents

- [✨ Features](#-features)
- [🗂️ Project Structure](#️-project-structure)
- [🚀 Installation](#-installation)
- [⚙️ Configuration](#%EF%B8%8F-configuration)
- [💻 Usage](#-usage)
- [🛣️ Roadmap](#-roadmap)
- [📝 License](#-license)

---

## ✨ Features

- **🔐 Smart Authentication** — Reuses existing sessions to avoid repeated logins
- **⚡ Fully Async** — Built with `async`/`await` for maximum performance
- **🏢 Company Filtering** — Optional company ID lookup for targeted searches
- **📸 Automatic Screenshots** — Captures page state at key steps for debugging
- **🍪 Cookie Consent Handling** — Automatically dismisses cookie popups
- **📊 Excel Export** — Exports results to formatted Excel files
- **🔍 Intelligent Waiting** — Waits for actual page content instead of arbitrary delays
- **🧪 Test Mode** — Run non-interactively with `--test` flag and `.env` credentials

---

## 🗂️ Project Structure

```
tigernet-scraper/
├── src/tigernet_scraper/
│   ├── __init__.py
│   ├── main.py              # CLI entrypoint (Typer)
│   ├── auth.py              # Authentication & session management
│   ├── scraper.py           # Core scraping logic
│   ├── company_lookup.py    # Company name → ID mapping
│   ├── utils.py             # Shared utilities (screenshots, etc.)
│   ├── models.py            # Data models (AlumRecord)
│   ├── exporter.py          # Excel export functionality
│   └── data/
│       └── company_ids.json # Company ID lookup table
├── tests/                   # Test suite
├── screenshots/             # Auto-generated screenshots (gitignored)
├── output/                  # Exported Excel files (gitignored)
├── session.json             # Session cookies (gitignored)
├── .env                     # Credentials (gitignored)
├── pyproject.toml           # Project configuration
├── uv.lock                  # Lock file
└── README.md                # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- [UV](https://github.com/astral-sh/uv) package manager (recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/aphil311/tigernet-scraper.git
cd tigernet-scraper

# Install dependencies with UV
uv sync

# That's it! 🎉
```

---

## ⚙️ Configuration

### 1. Create a `.env` file (for test mode)

In the project root, create `.env` with your TigerNet credentials:

```env
NETID=your_netid
PASSWORD=your_password
```

> **Note:** `.env` is gitignored. Never commit your credentials.

### 2. (Optional) Configure Company IDs

Edit `src/tigernet_scraper/data/company_ids.json` to add company name → ID mappings:

```json
{
  "McKinsey": "12345",
  "Google": "67890"
}
```

This enables targeted searches with `?company_ids=<ID>` in the URL.

---

## 💻 Usage

### Basic Usage

```bash
# Interactive mode (prompts for credentials)
uv run tigernet-scraper "Google"

# With a named output
uv run tigernet-scraper "Google" --output results.xlsx

# Test mode (uses .env, no prompts)
uv run tigernet-scraper --test "McKinsey"
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--netid` | Your TigerNet NetID (optional with `--test`) |
| `--password` | Your TigerNet password (optional with `--test`) |
| `--org` | Organization/department filter (can be used multiple times) |
| `--output`, `-o` | Output Excel file path (default: `output/alumni.xlsx`) |
| `--test` | Use credentials from `.env` instead of prompting |

### What It Does

1. Authenticates to TigerNet via Princeton CAS
2. Navigates to the alumni directory
3. Optionally filters by company ID (if mapped in `company_ids.json`)
4. Waits for results to fully load
5. Takes a screenshot for debugging (`screenshots/` directory)
6. Exports alumni records to Excel
7. Saves session cookies for future runs

> **Note:** The actual scraping logic is a placeholder. `alumni.xlsx` will contain zero rows until `_apply_filters`, `_paginate`, and `_parse_record` are implemented in `src/tigernet_scraper/scraper.py`.

---

## 🛣️ Roadmap

- [ ] Implement `_apply_filters()` to input company and org filters on the page
- [ ] Implement `_paginate()` to iterate through paginated results
- [ ] Implement `_parse_record()` to extract `AlumRecord` data from page elements
- [ ] Add rate limiting and anti-bot detection handling
- [ ] Add retry logic for failed requests
- [ ] Add progress bar for long-running scrapes
- [ ] Support exporting to CSV/JSON in addition to Excel
- [ ] Add logging configuration for different verbosity levels
- [ ] Write comprehensive test suite with mocks
- [ ] Add Docker containerization for reproducible runs

---

## 📝 License

MIT License — feel free to use and modify as needed.

---

<div align="center">

**Made with ❤️ using Playwright and Typer**

</div>
