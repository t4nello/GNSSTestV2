import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_get_2drms_should_return_200():
    session_id = 2268
    reference_type = "avg"
    response = requests.get(f"{BASE_URL}/2drms?session_id={session_id}&reference_type={reference_type}")
    assert response.status_code == 200

def test_get_2drms_wrong_session_id_should_return_404():
    session_id = 123
    reference_type = "avg"
    response = requests.get(f"{BASE_URL}/2drms?session_id={session_id}&reference_type={reference_type}")
    assert response.status_code == 404

def test_get_2drms_wrong_reference_type_should_return_400():
    session_id = 2268
    reference_type = "mean"
    response = requests.get(f"{BASE_URL}/2drms?session_id={session_id}&reference_type={reference_type}")
    assert response.status_code == 400

def test_get_2drms_wrong_both_fields_should_return_400():
    session_id = 123
    reference_type = "mean"
    response = requests.get(f"{BASE_URL}/2drms?session_id={session_id}&reference_type={reference_type}")
    assert response.status_code == 404
