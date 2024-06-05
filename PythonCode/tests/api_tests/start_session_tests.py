import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_start_session_success_should_return_200():
    response = requests.post(f"{BASE_URL}/session/start")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data

def test_start_session_failure_should_return_400():
    response = requests.post(f"{BASE_URL}/session/start")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data

def test_stop_session_success_should_return_200():
    response = requests.post(f"{BASE_URL}/session/stop")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_stop_session_failure_should_return_400():
    response = requests.post(f"{BASE_URL}/session/stop")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data

