import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_get_avg_wrong_sessionid_should_return_404():
    session_id = 123
    response = requests.get(f"{BASE_URL}/average?sessionid={session_id}")
    assert response.status_code == 404

def test_get_avg_should_return_200():
    session_id = 360
    response = requests.get(f"{BASE_URL}/average?sessionid={session_id}")
    assert response.status_code == 200
