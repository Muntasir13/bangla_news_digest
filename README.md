# Bangla News Digest

A production-style multi-site news scraper that fetches news articles from online Bangla news portals, normalizes and saves content, and produces human-friendly `.docx` reports.

Primary audiences:

- Head of Equity Research
- Data Engineers
- Project Managers
- Data Analysts.

## Table of Contents

1.  [Overview](#overview)
2.  [Current Feature List](#current-feature-list)
3.  [Future Planned Feature List](#future-planned-feature-list)
4.  [Architecture](#architecture)
5.  [Quick Start (local)](#quick-start-local)
6.  [Cron Job (Single Server)](#cron-job-single-server)
7.  [Configuration](#configuration)
8.  [Running the Scraper](#running-the-scraper)
9.  [Output & Storage](#output--storage)
10. [Logging & Monitoring](#logging--monitoring)
11. [Secrets & Security](#secrets--security)
12. [Adding a New Website](#adding-a-new-website)
13. [Troubleshooting](#troubleshooting)
14. [Releases](#releases)
15. [License & Privacy](#license--privacy)

## Overview

This project scrapes news content from configured websites, extracts article bodies, performs light normalization/validation, and exports human-readable `.docx` reports using DocxTemplate.

Website List:

[Will be added soon]

Goals:

- Reliable multi-site scraping
- Clean separation of concerns (Scrapers, WebDriver Adapter, Pipelines)
- Production-ready logging and storage (local for now; DB integration planned)

## Current Feature List

- Multi-site scrapers for all websites (site-specific scraper classes).
- Template Method + Bridge pattern for scrapers + WebDriver adapters.
- WebDriver management with `webdriver-manager` (Chrome & Firefox).
- Docx export using `docxtpl` (template-based `.docx` generation).
- Post-processing to convert plaintext URLs to real hyperlinks (keeps style).
- Logging: JSON formatting + daily rotation (TimedRotatingFileHandler).
- Pipelines that validate, normalize, deduplicate and save results (local storage).
- Utilities: YAML site configs, helpers, CLI runner.
- DB integration (SQL) for longer-term storage.
- CI (GitHub Actions): lint → unit test (just webdriver adapter).
- LLM prompt for NewsFlash summary bullet points generation (manual intervention).

## Future Planned Feature List

- Test module
- CI (GitHub Actions): CI (GitHub Actions) → build/push → deploy.
- Full test-suite coverage (pytest + Selenium integration tests).
- Docker image build + single-server docker-compose deployment examples.
- Config management with **Hydra** (hydra-core) for composable, overrideable configs and easy experiment sweeps. Hydra will unify global config, site-specific configs, driver settings, logging, and deployment overrides into a single composable config system.

## Architecture

High-level architecture and class diagrams are in `ARCHITECTURE.md` (flow chart + class diagram). The README contains runnable examples; the architecture doc contains visuals and rationale for design decisions.

**Path:** [ARCHITECTURE.md](docs/architecture.md)

## Quick Start (local)

> Works on Windows / macOS / Linux.

### Pre-requisites

- Python 3.13+ (recommended)
- Chrome and/or Firefox installed (Chrome preferred)
- `poetry` and optional Docker

### Setup (venv)

```bash
# create venv
poetry install
source venv/bin/activate    # macOS/Linux
.venv\Scripts\Activate.ps1       # Windows
```

### Local run

```bash
python runner.py
```

## Cron Job (Single Server)

Cron Job is going to performed once a server can be assigned for this project.

## Configuration

- Site-specific YAMLs: config/sites/[site1].yaml, [site2].yaml, ... Each YAML contains website name, url, and site specific selectors.

- Global config: config/default.yaml (webdriver, output, log and resource location)

- Environment variables: list below (store in .env or Docker secrets)

Important env Variables (example):

```ini
# Email
HOST=smtp.example.com
PORT=587
USER=...
PASSWORD=...
```

### Future: Hydra-based config management (planned)

We will add `hydra-core` to manage configuration composition, overrides, and multi-run sweeps. Benefits:

- Compose global + site + environment configs (`conf/config.yaml`, `conf/sites/*.yaml`, `conf/env/*.yaml`)
- Runtime overrides (e.g. `python runner.py driver=chrome headless=false`)
- Structured configs (dataclasses / OmegaConf) for stronger validation
- Automatic working-directory and output logging for runs (outputs stored under `outputs/<timestamp>/`)
- Easy multi-run sweeps for testing different rate limits / concurrency / scraping schedules

Planned layout (config directory):

- conf/
  - default.yaml
- sites/
  - site1.yaml
  - site2.yaml
- logger.yaml

## Running the Scraper

- `runner.py` is the primary entrypoint
- `src/` contains the project source code
- `db/` contains the code for CRUD operations in an SQL database.
- `news_scrapers/` contain the scraper code for each website. Template methodology used for code design.
- `utils/` contain the utility codes
- `webdriver_bridge/` contains the Selenium Driver layer and the Adapter layer code. The Adapter layer and the site scrapers are connected through Bridge methodology.

Examples:

```bash
python runner.py
```

## Output & Storage

Project output files are saved at `output/`.

Raw: `output/raw`
Processed: `output/processed/`

The raw folder contains the news data in JSON format. The processed folder contains the data in the intended DOCX format. DOCX reports are saved with filenames like `news_data_YYYY-MM-DD.docx`. Filename can be configured in `runner.py`

## Logging & Monitoring

Logs are JSON structured and written to `logs/` (daily rotated). Sentry may be integrated via `SENTRY_DSN` for viewing and filtering logs (but highly unlikely).

## Secrets & Security

**Do not** commit secrets. Use one of:

- `.env` (local dev only) + add to `.gitignore`
- Docker secrets (production)
- GitHub Secrets (CI) / Vault (for GitHub schedular)

Store at minimum:

- SMTP credentials
- DB credentials
- SSH deploy key (for server deployments) (if implemented)
- SENTRY_DSN (if implemented)

Example `.env` code is given in [Configuration](#configuration)

## Adding a New Website

1. Add config/sites/[newsite].yaml (name, url, selectors).
2. Create src/news_scrapers/[newsite]\_scraper.py implementing SiteScraper(BaseScraper) (override parse methods following Template Method).
3. Add a small unit test in tests/news*scrapers/test*[newsite]\_scraper.py — mock network.
4. Register the site in the runner file.
5. Run `python -m pytest tests/news_scrapers/test_[newsite]_scraper.py
`

## Troubleshooting

- **Driver issues:** ensure webdriver-manager can reach the internet; run `python -c "from webdriver_manager.chrome import ChromeDriverManager; print(ChromeDriverManager().install())"` to debug.
- **Cloudflare / bot protection:** For better cloudflare bypass, use Chrome. undetected-chromedriver has been implemented to help this cause.
- **Links in docx not clickable:** We post-process docx to convert plaintext URLs to hyperlinks. If styles change after clicking, check the `FollowedHyperlink` style in the template.

## Releases

## License & Privacy

This repository is private to the Equity Research Team of IDLC Securities Limited (IDLCSL), and by extension to the parent company IDLC Finance Limited (IDLC). No public license included.
