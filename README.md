# AISA25_BeFriends

AISA25_BeFriends is a modern, production-grade backend for event discovery and search, built with Python 3.11, FastAPI, SQLAlchemy, and a clean architecture approach.

## Features
- **Event Search API**: Advanced search with fuzzy/partial match, filters (date, city, region, price, tags), and recency/relevance ranking
- **Persistent Storage**: SQLAlchemy ORM with SQLite (configurable)
- **Automated Ingestion**: Pluggable connectors, normalization, deduplication, and cronjob support for ingesting events from CSV/HTML
- **Robust Test Suite**: End-to-end and integration tests with pytest
- **Centralized Configuration**: All config via environment variables and `.env` (using `python-dotenv`)
- **Logging & Error Handling**: Production-ready logging and error management
- **Clean Code**: Fully linted and formatted (black, flake8), with no critical or functional lint errors
- **GitHub Integration**: Clean repo, .gitignore, and SSH setup

## Quickstart
1. **Clone the repo**
   ```sh
   git clone git@github.com:Matleo/AISA25_BeFriends.git
   cd AISA25_BeFriends
   ```
2. **Create and activate a virtual environment**
   ```sh
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Configure environment**
   - Copy `.env.example` to `.env` and adjust as needed (see below)
   - Or set environment variables directly

5. **Run the API**
   ```sh
   uvicorn befriends.app:create_app --host 0.0.0.0 --port 8000 --reload --factory
   ```

6. **Run tests**
   ```sh
   pytest
   ```

## Configuration
All configuration is centralized in `befriends/common/config.py` and loaded from environment variables or a `.env` file. Key variables:
- `BEFRIENDS_DB_URL` (default: `sqlite:///events.db`)
- `BEFRIENDS_FEATURES` (comma-separated feature flags)

## Project Structure
```
befriends/
  app.py                # FastAPI app composition root
  common/               # Config, telemetry, shared utils
  domain/               # Event and search models
  catalog/              # ORM and repository
  ingestion/            # Source connectors, normalization, deduplication
  search/               # Search service and ranking
  response/             # UI response formatting
  web/                  # API controllers
scripts/                # Data generation, utilities
requirements.txt        # Pinned dependencies
.env.example            # Example environment config
```

## License
MIT
