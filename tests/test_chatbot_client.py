import pytest

from befriends.chatbot_client import ChatbotConfig, ChatbotClient
from befriends.common.config import AppConfig

from .conftest import MockResponse

def make_app_config(endpoint, api_key):
    """Helper to create AppConfig for tests."""
    return AppConfig(
        db_url="sqlite:///events.db",
        openai_api_key=api_key,
        openai_api_endpoint=endpoint,
        sources=[],
        features={},
    )


def test_chatbot_client_custom_endpoint_and_key(monkeypatch):
    # Test with custom config values
    def mock_post(url, headers, json, timeout):
        assert url == "https://custom.endpoint"
        assert headers["Authorization"] == "Bearer custom-key"
        return MockResponse({"choices": [{"message": {"content": "Custom endpoint reply"}}]})
    monkeypatch.setattr("requests.post", mock_post)
    app_config = make_app_config("https://custom.endpoint", "custom-key")
    config = ChatbotConfig(app_config)
    client = ChatbotClient(config)
    messages = [{"role": "user", "content": "Hi!"}]
    response = client.get_response("user42", messages)
    assert response == "Custom endpoint reply"


def test_chatbot_client_error(monkeypatch):
    # Simulate HTTP error
    def mock_post(url, headers, json, timeout):
        return MockResponse({}, status_code=401)
    monkeypatch.setattr("requests.post", mock_post)
    app_config = make_app_config("https://mock.endpoint", "sk-test")
    config = ChatbotConfig(app_config)
    client = ChatbotClient(config)
    messages = [{"role": "user", "content": "Hi!"}]
    with pytest.raises(Exception):
        client.get_response("user42", messages)


def test_chatbot_config_env(monkeypatch):
    # Test config loads from environment
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setenv("OPENAI_API_ENDPOINT", "https://env.endpoint")
    config = ChatbotConfig()
    assert config.api_key == "env-key"
    assert config.endpoint == "https://env.endpoint"


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception("HTTP error")


def test_chatbot_client(monkeypatch):
    # Mock requests.post
    def mock_post(url, headers, json, timeout):
        assert headers["Authorization"].startswith("Bearer ")
        assert json["user"] == "test_user"
        assert isinstance(json["messages"], list)
        return MockResponse({
            "choices": [{"message": {"content": "Hello from GPT-5!"}}]
        })
    monkeypatch.setattr("requests.post", mock_post)
    app_config = make_app_config("https://mock.endpoint", "sk-test")
    config = ChatbotConfig(app_config)
    client = ChatbotClient(config)
    messages = [
        {"role": "user", "content": "Hello!"}
    ]
    response = client.get_response("test_user", messages)
    assert response == "Hello from GPT-5!"


# --- Additional coverage and robustness tests ---
import requests

import pytest

def test_chatbot_client_timeout(monkeypatch):
    def mock_post(*a, **k):
        raise requests.Timeout()
    monkeypatch.setattr("requests.post", mock_post)
    app_config = make_app_config("https://mock.endpoint", "sk-test")
    config = ChatbotConfig(app_config)
    client = ChatbotClient(config)
    with pytest.raises(RuntimeError) as exc:
        client.get_response("user", [{"role": "user", "content": "hi"}])
    assert "took too long" in str(exc.value)

def test_chatbot_client_bad_endpoint_type():
    app_config = make_app_config(123, "sk-test")  # Not a string
    config = ChatbotConfig(app_config)
    client = ChatbotClient(config)
    with pytest.raises(ValueError):
        client.get_response("user", [{"role": "user", "content": "hi"}])

def test_chatbot_client_malformed_response(monkeypatch):
    class BadResponse:
        def __init__(self):
            self.status_code = 200
        def raise_for_status(self):
            pass
        def json(self):
            raise Exception("bad json")
    def mock_post(*a, **k):
        return BadResponse()
    monkeypatch.setattr("requests.post", mock_post)
    app_config = make_app_config("https://mock.endpoint", "sk-test")
    config = ChatbotConfig(app_config)
    client = ChatbotClient(config)
    with pytest.raises(RuntimeError) as exc:
        client.get_response("user", [{"role": "user", "content": "hi"}])
    assert "Failed to parse backend response" in str(exc.value)
