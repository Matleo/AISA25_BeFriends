[![codecov](https://codecov.io/gh/Matleo/AISA25_BeFriends/branch/main/graph/badge.svg)](https://codecov.io/gh/Matleo/AISA25_BeFriends)

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

## API Documentation

This project uses FastAPI, which provides automatic interactive API docs:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Main Endpoints
- `GET /search` — Search for events. Query params: `query_text`, `date_from`, `date_to`, `city`, `region`, `category`, `tags`, `price_min`, `price_max`
- `POST /admin/reingest` — Trigger re-ingestion of all sources (admin)

Example request:
```sh
curl -X GET "http://localhost:8000/search?query_text=music&city=Berlin"
curl -X POST "http://localhost:8000/admin/reingest"
```

See the interactive docs for full parameter and response details.

---

## Contribution & Development

Contributions are welcome! To get started:

1. **Fork the repository** and clone your fork.
2. **Create a new branch** for your feature or fix:
   ```sh
   git checkout -b my-feature
   ```
3. **Install dependencies** and set up your environment (see Quickstart above).
4. **Run tests and linting** before submitting:
   ```sh
   pytest
   flake8 befriends/
   ```
5. **Submit a pull request** with a clear description of your changes.

### Development Guidelines
- Follow PEP8 and use `black` and `flake8` for formatting/linting.
- Write unit and integration tests for new features.
- Keep code modular and maintain clean architecture boundaries.
- Document public APIs and major changes in the README or a `CHANGELOG.md`.

---

## Test Coverage Reporting

This project supports test coverage reporting using `coverage.py`.

### How to Run Coverage Locally
1. Install coverage:
   ```sh
   pip install coverage
   ```
2. Run tests with coverage:
   ```sh
   coverage run -m pytest
   coverage report -m
   coverage html  # (optional) generates an HTML report in htmlcov/
   ```
3. Check the terminal output or open `htmlcov/index.html` in your browser for a detailed report.

### Coverage Badge (Optional)
- Integrate with [Codecov](https://codecov.io/) or [Coveralls](https://coveralls.io/) for automatic coverage badges on GitHub.
- Add the badge markdown to the top of your README after setting up the service.

Example badge (Codecov):
```
[![codecov](https://codecov.io/gh/Matleo/AISA25_BeFriends/branch/main/graph/badge.svg)](https://codecov.io/gh/Matleo/AISA25_BeFriends)
```

---

## Docker Usage

You can run this project as a Docker container.

### Build and Run Locally
```sh
# Build the image
docker build -t aisa25_befriends .

# Run the container
# (Expose port 8000 and mount your .env if needed)
docker run -p 8000:8000 --env-file .env aisa25_befriends
```

### Pull from GitHub Container Registry
```sh
docker pull ghcr.io/<your-username>/aisa25_befriends:latest
docker run -p 8000:8000 --env-file .env ghcr.io/<your-username>/aisa25_befriends:latest
```

### Pull from Docker Hub (if configured)
```sh
docker pull <your-dockerhub-username>/aisa25_befriends:latest
docker run -p 8000:8000 --env-file .env <your-dockerhub-username>/aisa25_befriends:latest
```

Replace `<your-username>` and `<your-dockerhub-username>` with your actual usernames.

---

**Author:** Matthias Leopold  
[GitHub](https://github.com/Matleo)  
[LinkedIn](https://www.linkedin.com/in/matthias-leopold-0ba93413b/)

## License
MIT
