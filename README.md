## How to use Streamlit UI

The project includes a modern Streamlit frontend for searching and exploring events.

### To launch the Streamlit app:

```sh
pip install streamlit  # if not already installed
streamlit run streamlit_app.py
```

The app will open in your browser (usually at [http://localhost:8501](http://localhost:8501)).

Make sure your FastAPI backend is running (see Quickstart below) so the UI can fetch events.

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
curl -X POST "http://localhost:8000/admin/reingest"
docker build -t aisa25_befriends .
docker run -p 8000:8000 --env-file .env aisa25_befriends
docker pull ghcr.io/<your-username>/aisa25_befriends:latest
docker run -p 8000:8000 --env-file .env ghcr.io/<your-username>/aisa25_befriends:latest
docker pull <your-dockerhub-username>/aisa25_befriends:latest
docker run -p 8000:8000 --env-file .env <your-dockerhub-username>/aisa25_befriends:latest

[![codecov](https://codecov.io/gh/Matleo/AISA25_BeFriends/branch/main/graph/badge.svg)](https://codecov.io/gh/Matleo/AISA25_BeFriends)

# AISA25_BeFriends


**Modern event search backend** with FastAPI, SQLAlchemy, and robust automation.

## Database Schema Notes
- The `events` table uses a **string primary key** (`id: str`), compatible with custom and auto-generated IDs.
- If no `id` is provided, a **UUID is auto-generated** for each event (see `EventORM` in `befriends/catalog/orm.py`).
- All fields use correct types for SQLite (e.g., `String`, `Date`, `DateTime`, `Text`).
- The test/CI setup **removes `events.db` before every run** to ensure a fresh schema and avoid migration issues.

## Why use AISA25_BeFriends?
- Fast, flexible event search API (fuzzy, filters, recency)
- Automated data import (CSV, HTML, API)
- Clean, production-ready code and CI/CD
- Easy to run locally or in Docker

## Quickstart
```sh
git clone git@github.com:Matleo/AISA25_BeFriends.git
cd AISA25_BeFriends
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Edit as needed
uvicorn befriends.app:create_app --host 0.0.0.0 --port 8000 --reload --factory
```

## Features
- **Search API:** Fuzzy, filtered, and ranked event search
- **Persistent DB:** SQLite by default, configurable
- **Automated ingestion:** Pluggable, deduped, validated
- **Streamlit UI:** Modern frontend (see `streamlit_app.py`)
- **Full test suite:** End-to-end and integration tests
- **CI/CD:** Lint, type check, test, coverage, Docker

## API Docs
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Example Endpoints
- `GET /search` — Search events (query, filters)
- `POST /admin/reingest` — Re-import all sources

## Project Structure
```
befriends/   # Main backend code
scripts/     # Data import/utilities
requirements.txt
.env.example
```

## Docker
```sh
docker build -t aisa25_befriends .
docker run -p 8000:8000 --env-file .env aisa25_befriends
```


## Test & Coverage
```sh
pytest
flake8 befriends/
coverage run -m pytest && coverage report -m
```

**Note:** If you change the DB schema, delete `events.db` before running tests to avoid type mismatches. This is automated in CI.

## Contributing
- Fork, branch, and PR as usual
- Run tests and lint before submitting
- Follow PEP8, keep code modular

## Author
Matthias Leopold  
[GitHub](https://github.com/Matleo) | [LinkedIn](https://www.linkedin.com/in/matthias-leopold-0ba93413b/)

## License
MIT
