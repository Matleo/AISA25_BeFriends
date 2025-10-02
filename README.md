# AISA25_BeFriends

**A modular event search and chatbot platform with FastAPI backend and Streamlit frontend.**

---

## Features
- **Search API**: Fuzzy, filtered, and ranked event search.
- **Streamlit UI**: Modern frontend for event discovery and chatbot interaction.
- **Automated Data Import**: Supports CSV, HTML, and API ingestion.
- **Persistent Database**: SQLite by default, configurable for other databases.
- **Extensible Architecture**: Modular, testable, and production-ready.
- **Full Test Suite**: Unit, integration, and end-to-end tests.
- **Docker Support**: Easy deployment with Docker.

---

## Quickstart

### 1. Clone the Repository
```sh
git clone git@github.com:Matleo/AISA25_BeFriends.git
cd AISA25_BeFriends
```

### 2. Set Up the Environment
1. Create a virtual environment:
   ```sh
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```sh
   cp .env.example .env
   ```
   Edit `.env` as needed.

---

### 3. Start the Backend (FastAPI)
1. Run the backend using Uvicorn:
   ```sh
   uvicorn befriends.app:create_app --host 0.0.0.0 --port 8000 --reload --factory
   ```

2. Access the API documentation:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 4. Start the Frontend (Streamlit)
1. Install Streamlit (if not already installed):
   ```sh
   pip install streamlit
   ```

2. Start the event search UI:
   ```sh
   streamlit run streamlit_app.py
   ```

3. Alternatively, start the chatbot UI:
   ```sh
   streamlit run streamlit_chatbot.py
   ```

4. Access the frontend:
   - The app will open in your browser, typically at [http://localhost:8501](http://localhost:8501).

---

### 5. Data Import
1. Place new CSV files in the `befriends/data/` directory.
2. Trigger ingestion via the FastAPI admin endpoint:
   ```sh
   curl -X POST "http://localhost:8000/admin/reingest"
   ```

---

## Development

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the backend API server:
   ```bash
   uvicorn main:app --reload
   ```
   (Replace `main:app` with your actual entrypoint if different)

4. Start the Streamlit frontend:
   ```bash
   streamlit run streamlit_chatbot.py
   ```

---

## Testing & Linting
Run the test suite to ensure everything works as expected:
```sh
pytest
ruff check .
coverage run -m pytest && coverage report -m
```

---

## Docker
1. Build the Docker image:
   ```sh
   docker build -t aisa25_befriends .
   ```

2. Run the container:
   ```sh
   docker run -p 8000:8000 --env-file .env aisa25_befriends
   ```

---

## Project Structure
```
befriends/   # Backend code (API, logic, models)
components/  # UI components for Streamlit
static/      # CSS, HTML assets
scripts/     # Data import/utilities
tests/       # Test suite
requirements.txt
.env.example
```

---

## API Endpoints
- `GET /search` — Search events (query, filters).
- `POST /admin/reingest` — Re-import all sources.
- `POST /admin/import-csv?password=import123` — Import CSV (admin).

---

## Notes
- The Streamlit app expects the FastAPI backend to be running at `http://localhost:8000` by default.
- To change the API URL, edit the `API_URL` variable at the top of `streamlit_app.py`.
- If you change the database schema, delete `events.db` before running tests or the backend.

---

## License
MIT

---

## Author
Matthias Leopold  
[GitHub](https://github.com/Matleo) | [LinkedIn](https://www.linkedin.com/in/matthias-leopold-0ba93413b/)