import pytest
from fastapi.testclient import TestClient
from befriends.app import create_app

@pytest.fixture(scope="module")
def client():
    app = create_app()
    with TestClient(app) as c:
        yield c

def test_search_endpoint(client):
    response = client.get("/search", params={"query_text": "music", "city": "Berlin"})
    assert response.status_code == 200
    data = response.json()
    assert "narrative" in data
    assert "cards" in data

def test_admin_reingest_endpoint(client):
    response = client.post("/admin/reingest")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ingested" in data
