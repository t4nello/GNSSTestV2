import requests

BASE_URL = "http://127.0.0.1:5000/api"


def test_get_sessions():
    response = requests.get(f"{BASE_URL}/sessions")
    assert response.status_code == 200

def test_get_devices():
    response = requests.get(f"{BASE_URL}/devices")
    assert response.status_code == 200