import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_get_mode_should_return_200():
    session_id = 2268
    response = requests.get(f"{BASE_URL}/mode/{session_id}")
    assert response.status_code == 200

def test_get_mode_wrong_sessionid_should_return_404():
    session_id = 123
    response = requests.get(f"{BASE_URL}/mode/{session_id}")
    assert response.status_code == 404