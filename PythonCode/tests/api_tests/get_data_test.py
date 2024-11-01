import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_get_measurements_wrong_device_should_return_404():
    device = "gps"
    field = "latitude"
    session_id = 2268
    response = requests.get(f"{BASE_URL}/session/data?session_id={session_id}&device={device}&field={field}")
    assert response.status_code == 404

def test_get_measurements_wrong_session_id_should_return_404():  
    device = "all"
    session_id = 123
    field = "latitude"
    response = requests.get(f"{BASE_URL}/session/data?session_id={session_id}&device={device}&field={field}")
    assert response.status_code == 404

def test_get_measurements_wrong_field_should_return_400():
    device = "all"
    session_id = 2268
    field = "elevation"
    response = requests.get(f"{BASE_URL}/session/data?session_id={session_id}&device={device}&field={field}")
    assert response.status_code == 400

def test_get_measurements_should_return_200():
    device = "all"
    session_id = 360
    field = "position"
    response = requests.get(f"{BASE_URL}/session/data?session_id={session_id}&device={device}&field={field}")
    assert response.status_code == 200
