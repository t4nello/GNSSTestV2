import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_get_count_should_return_200():
    field = "latitude"
    session_id = 360
    response = requests.get(f"{BASE_URL}/session/field-count?sessionid={session_id}&field={field}")
    assert response.status_code == 200

def test_get_count_wrong_field_should_return_400():
    field = "elevation"
    session_id = 2268
    response = requests.get(f"{BASE_URL}/session/field-count?sessionid={session_id}&field={field}")
    assert response.status_code == 400

def test_get_count_wrong_sessionid_should_return_404():
    field = "latitude"
    session_id = 123
    response = requests.get(f"{BASE_URL}/session/field-count?sessionid={session_id}&field={field}")
    assert response.status_code == 404

def test_get_count_wrong_parameters_should_return_400():
    response = requests.get(f"{BASE_URL}/session/field-count")
    assert response.status_code == 400
