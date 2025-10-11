import pytest
from emailoctopus_sdk import Client, ApiError

API_KEY = "test-api-key"


def test_client_initialization():
    """Tests that the client initializes correctly."""
    client = Client(api_key=API_KEY)
    assert client.api_key == API_KEY
    assert client.BASE_URL == "https://api.emailoctopus.com"

def test_client_init_requires_api_key():
    """Tests that an error is raised if no API key is provided."""
    with pytest.raises(ValueError, match="API key cannot be empty."):
        Client(api_key="")

def test_get_all_lists_success(requests_mock):
    """Tests a successful call to get all lists."""
    mock_response = {
        "data": [
            {"id": "list-1", "name": "Test List 1"},
            {"id": "list-2", "name": "Test List 2"}
        ],
        "paging": {}
    }
    requests_mock.get(f"https://api.emailoctopus.com/lists?api_key={API_KEY}", json=mock_response)

    client = Client(api_key=API_KEY)
    lists = client.get_all_lists()
    assert lists == mock_response

def test_api_error_handling(requests_mock):
    """Tests that a 401 Unauthorized error is handled correctly."""
    error_response = {
        "error": {
            "code": "API_KEY_INVALID",
            "message": "Your API key is invalid."
        }
    }
    requests_mock.get(f"https://api.emailoctopus.com/lists?api_key={API_KEY}", json=error_response, status_code=401)
    
    client = Client(api_key=API_KEY)
    with pytest.raises(ApiError, match="API Error: Your API key is invalid."):
        client.get_all_lists()
