import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_get_devices_for_session_should_return_200():
    session_id = 2268
    response = requests.get(f"{BASE_URL}/devices?session_id={session_id}")
    assert response.status_code == 200

def test_get_devices_for_session_wrong_session_id_should_return_404():
    session_id = 123
    response = requests.get(f"{BASE_URL}/devices?session_id={session_id}")
    assert response.status_code == 404
