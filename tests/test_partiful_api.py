import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from partiful_api import PartifulAPI
import requests_mock
from unittest.mock import patch, MagicMock
import json
import requests

# Test constants
TEST_USER_ID = "test_user"
TEST_EVENT_NAME = "Test Event"
TEST_DESCRIPTION = "Test Description"
TEST_MAX_CAPACITY = 50

endpoints = {
    "create_event": "https://api.partiful.com/createEvent",
    "get_mutuals": "https://api.partiful.com/getMutuals",
}

class DummyProfile:
    def __init__(self, user_id):
        self.user_id = user_id

@pytest.fixture
def dummy_profile():
    return DummyProfile(user_id="dummy_user_id")

@pytest.fixture
def mock_partiful_api(dummy_profile):
    fake_profile = MagicMock()
    fake_profile.user_id = 'test_user'

    api = PartifulAPI(default_profile=fake_profile, auth_token='test_token')
    return api

@pytest.fixture
def sample_datetime():
    return datetime(2024, 4, 28, 18, 30, tzinfo=ZoneInfo("America/Los_Angeles"))

def test_create_event(mock_partiful_api, sample_datetime, requests_mock):
    """Test event creation with mocked API call."""
    # Arrange
    mock_response = {
        "result": {
            "data": "test_event_id"
        }
    }
    requests_mock.post(endpoints['create_event'], json=mock_response)

    # Act
    event_id = mock_partiful_api.create_event(
        event_name=TEST_EVENT_NAME,
        event_date=sample_datetime,
        max_capacity=TEST_MAX_CAPACITY,
        description=TEST_DESCRIPTION,
    )

    # Assert
    assert event_id == "https://partiful.com/e/" + "test_event_id"


def test_create_event_with_cohosts(mock_partiful_api, sample_datetime, requests_mock):
    """Test event creation with cohosts."""
    mock_response = {
        "result": {
            "data": "test_event_id"
        }
    }
    requests_mock.post(endpoints['create_event'], json=mock_response)

    cohosts = ["cohost1", "cohost2"]
    response = mock_partiful_api.create_event(
        event_name=TEST_EVENT_NAME,
        event_date=sample_datetime,
        max_capacity=TEST_MAX_CAPACITY,
        description=TEST_DESCRIPTION,
        cohosts=cohosts
    )

    # Verify the request included cohosts
    last_request = requests_mock.last_request
    request_json = json.loads(last_request.json())

    assert request_json['data']['params']['cohostIds'] == cohosts

def test_create_event_error(mock_partiful_api, sample_datetime, requests_mock):
    """Test error handling for event creation."""
    
    mock_response = {"unexpected_key": "unexpected_value"}
    requests_mock.post(endpoints['create_event'], json=mock_response, status_code=400)
    with pytest.raises(Exception):
        mock_partiful_api.create_event(
            event_name=TEST_EVENT_NAME,
            event_date=sample_datetime,
            max_capacity=TEST_MAX_CAPACITY,
            description=TEST_DESCRIPTION
        )

    mock_response = {"unexpected_key": "unexpected_value"}
    requests_mock.post(endpoints['create_event'], json=mock_response, status_code=200)
    with pytest.raises(KeyError):
        mock_partiful_api.create_event(
            event_name=TEST_EVENT_NAME,
            event_date=sample_datetime,
            max_capacity=TEST_MAX_CAPACITY,
            description=TEST_DESCRIPTION
        )

    # Test KeyError when 'data' subkey is missing under 'result'
    mock_response = {"result": {"not_data": "value"}}
    requests_mock.post(endpoints['create_event'], json=mock_response, status_code=200)
    with pytest.raises(KeyError):
        mock_partiful_api.create_event(
            event_name=TEST_EVENT_NAME,
            event_date=sample_datetime,
            max_capacity=TEST_MAX_CAPACITY,
            description=TEST_DESCRIPTION
        )

def test_call_api_get_success(mock_partiful_api, requests_mock):
    """Test call_api with GET method and successful response."""
    url = "https://api.partiful.com/testGet"
    mock_response = {"result": "ok"}
    requests_mock.get(url, json=mock_response, headers={"Content-Type": "application/json"})
    result = mock_partiful_api.call_api(url, method="GET")
    assert result == mock_response

def test_call_api_post_success(mock_partiful_api, requests_mock):
    """Test call_api with POST method and successful response."""
    url = "https://api.partiful.com/testPost"
    mock_response = {"result": "ok"}
    requests_mock.post(url, json=mock_response, headers={"Content-Type": "application/json"})
    result = mock_partiful_api.call_api(url, method="POST", data={"foo": "bar"})
    assert result == mock_response

def test_call_api_unsupported_method(mock_partiful_api):
    """Test call_api with unsupported HTTP method."""
    with pytest.raises(ValueError):
        mock_partiful_api.call_api("https://api.partiful.com/test", method="PUT")

def test_call_api_non_200_status(mock_partiful_api, requests_mock):
    """Test call_api raises exception on non-200 status code."""
    url = "https://api.partiful.com/testError"
    requests_mock.get(url, status_code=404, text="Not Found", headers={"Content-Type": "application/json"})
    with pytest.raises(Exception) as excinfo:
        mock_partiful_api.call_api(url, method="GET")
    assert "Error calling API" in str(excinfo.value)

def test_call_api_json_decode_error(monkeypatch, mock_partiful_api, requests_mock):
    """Test call_api handles JSONDecodeError on error response."""
    url = "https://api.partiful.com/testJsonDecode"
    class DummyResponse:
        status_code = 500
        text = "Internal Server Error"
        headers = {"Content-Type": "application/json"}
        def json(self):
            raise requests.exceptions.JSONDecodeError("Expecting value", "", 0)
    monkeypatch.setattr("requests.get", lambda *a, **kw: DummyResponse())
    with pytest.raises(Exception) as excinfo:
        mock_partiful_api.call_api(url, method="GET")
    assert "Error calling API" in str(excinfo.value)

def test_call_api_api_error_field(mock_partiful_api, requests_mock):
    """Test call_api raises exception if 'error' in JSON response."""
    url = "https://api.partiful.com/testApiError"
    mock_response = {"error": {"message": "Something went wrong"}}
    requests_mock.get(url, json=mock_response, headers={"Content-Type": "application/json"})
    with pytest.raises(Exception) as excinfo:
        mock_partiful_api.call_api(url, method="GET")
    assert "API Error" in str(excinfo.value)

# def test_get_mutuals(mock_partiful_api, requests_mock):
#     """Test getting mutual connections."""
#     mock_response = {
#         "result": {
#             "data": ["user1", "user2"]
#         }
#     }
#     requests_mock.post('https://api.partiful.com/getMutuals', json=mock_response)

#     response = mock_partiful_api.get_mutuals()
#     assert response['result']['data'] == ["user1", "user2"]
