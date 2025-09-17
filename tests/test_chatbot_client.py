import pytest
from befriends.chatbot_client import ChatbotConfig, ChatbotClient


def test_chatbot_client_custom_endpoint_and_key(monkeypatch):
    # Test with custom config values
    def mock_post(url, headers, json, timeout):
        assert url == "https://custom.endpoint"
        assert headers["Authorization"] == "Bearer custom-key"
        return MockResponse({"choices": [{"message": {"content": "Custom endpoint reply"}}]})
    monkeypatch.setattr("requests.post", mock_post)
    config = ChatbotConfig(endpoint="https://custom.endpoint", api_key="custom-key")
    client = ChatbotClient(config)
    messages = [{"role": "user", "content": "Hi!"}]
    response = client.get_response("user42", messages)
    assert response == "Custom endpoint reply"


def test_chatbot_client_error(monkeypatch):
    # Simulate HTTP error
    def mock_post(url, headers, json, timeout):
        return MockResponse({}, status_code=401)
    monkeypatch.setattr("requests.post", mock_post)
    config = ChatbotConfig(endpoint="https://mock.endpoint", api_key="sk-test")
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
    config = ChatbotConfig(endpoint="https://mock.endpoint", api_key="sk-test")
    client = ChatbotClient(config)
    messages = [
        {"role": "user", "content": "Hello!"}
    ]
    response = client.get_response("test_user", messages)
    assert response == "Hello from GPT-5!"
