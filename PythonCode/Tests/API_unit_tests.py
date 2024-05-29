import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"


def test_get_sessions():
    response = requests.get(f"{BASE_URL}/sessions")
    assert response.status_code == 200

def test_get_devices():
    response = requests.get(f"{BASE_URL}/devices")
    assert response.status_code == 200

def test_get_devices_for_session_should_return_200():
    session_id = 2268
    response = requests.get(f"{BASE_URL}/{session_id}/devices")
    assert response.status_code == 200

def test_get_devices_for_session_wrong_sessionid_should_return_404():
    session_id = 123
    response = requests.get(f"{BASE_URL}/{session_id}/devices")
    assert response.status_code == 404

def test_get_measurements_wrong_device_should_return_404():
    device = "gps"
    field = "latitude"
    session_id = 2268
    response = requests.get(f"{BASE_URL}/{device}/{field}/{session_id}")
    assert response.status_code == 404

def test_get_measurements_wrong_sessionid_should_return_404():  
    device = "all"
    session_id = 123
    field = "latitude"
    response = requests.get(f"{BASE_URL}/{device}/{field}/{session_id}")
    assert response.status_code == 404

def test_get_measurements_wrong_field_should_return_400():
    device = "all"
    session_id = 2268
    field = "elevation"
    response = requests.get(f"{BASE_URL}/{device}/{field}/{session_id}")
    assert response.status_code == 400

def test_get_measurements_should_return_200():
    device = "all"
    session_id = 360
    field = "position"
    response = requests.get(f"{BASE_URL}/{device}/{field}/{session_id}")
    assert response.status_code == 200

def test_get_avg_wrong_sessionid_should_return_404():
    session_id = 123
    response = requests.get(f"{BASE_URL}/avg/{session_id}")
    assert response.status_code == 404

def test_get_mode_should_return_200():
    session_id = 2268
    response = requests.get(f"{BASE_URL}/mode/{session_id}")
    assert response.status_code == 200

def test_get_mode_wrong_sessionid_should_return_404():
    session_id = 123
    response = requests.get(f"{BASE_URL}/mode/{session_id}")
    assert response.status_code == 404

def test_get_count_should_return_200():
    field = "latitude"
    session_id = 360
    response = requests.get(f"{BASE_URL}/count/{session_id}/{field}")
    assert response.status_code == 200

def test_get_count_wrong_field_should_return_400():
    field = "elevation"
    session_id = 2268
    response = requests.get(f"{BASE_URL}/count/{session_id}/{field}")
    assert response.status_code == 400

def test_get_count_wrong_sessionid_should_return_404():
    field = "latitude"
    session_id = 123
    response = requests.get(f"{BASE_URL}/count/{session_id}/{field}")
    assert response.status_code == 404

def test_get_count_wrong_parameters_should_return_400():
    field = "elevation"
    session_id = 123
    response = requests.get(f"{BASE_URL}/count/{session_id}/{field}")
    assert response.status_code == 400

def test_get_sigma_should_return_200():
    session_id = 2268
    reference_type = "avg"
    response = requests.get(f"{BASE_URL}/sigma/{session_id}/{reference_type}")
    assert response.status_code == 200

def test_get_sigma_wrong_sessionid_should_return_404():
    session_id = 123
    reference_type = "avg"
    response = requests.get(f"{BASE_URL}/sigma/{session_id}/{reference_type}")
    assert response.status_code == 404

def test_get_sigma_wrong_reference_type_should_return_400():
    session_id = 2268
    reference_type = "mean"
    response = requests.get(f"{BASE_URL}/sigma/{session_id}/{reference_type}")
    assert response.status_code == 400

def test_get_drms_should_return_200():
    session_id = 2268
    reference_type = "avg"
    response = requests.get(f"{BASE_URL}/drms/{session_id}/{reference_type}")
    assert response.status_code == 200

def test_get_drms_wrong_sessionid_should_return_404():
    session_id = 123
    reference_type = "avg"
    response = requests.get(f"{BASE_URL}/drms/{session_id}/{reference_type}")
    assert response.status_code == 404

def test_get_drms_wrong_reference_type_should_return_400():
    session_id = 2268
    reference_type = "mean"
    response = requests.get(f"{BASE_URL}/drms/{session_id}/{reference_type}")
    assert response.status_code == 400

def test_get_2drms_should_return_200():
    session_id = 2268
    reference_type = "avg"
    response = requests.get(f"{BASE_URL}/2drms/{session_id}/{reference_type}")
    assert response.status_code == 200

def test_get_2drms_wrong_sessionid_should_return_404():
    session_id = 123
    reference_type = "avg"
    response = requests.get(f"{BASE_URL}/2drms/{session_id}/{reference_type}")
    assert response.status_code == 404

def test_get_2drms_wrong_reference_type_should_return_400():
    session_id = 2268
    reference_type = "mean"
    response = requests.get(f"{BASE_URL}/2drms/{session_id}/{reference_type}")
    assert response.status_code == 400

def test_get_cep_should_return_200():
    session_id = 2268
    reference_type = "avg"
    response = requests.get(f"{BASE_URL}/cep/{session_id}/{reference_type}")
    assert response.status_code == 200

def test_get_cep_wrong_sessionid_should_return_404():
    session_id = 123
    reference_type = "avg"
    response = requests.get(f"{BASE_URL}/cep/{session_id}/{reference_type}")
    assert response.status_code == 404

def test_get_cep_wrong_reference_type_should_return_400():
    session_id = 2268
    reference_type = "mean"
    response = requests.get(f"{BASE_URL}/cep/{session_id}/{reference_type}")
    assert response.status_code == 400

def test_response_content_type_json():
    endpoints = [
        "/sessions",
        "/devices",
        "/2268/devices",  
        "/all/latitude/360",  
        "/avg/360", 
        "/mode/360",
        "/count/360/latitude",
        "/sigma/360/avg",
        "/drms/360/mode", 
        "/2drms/360/avg", 
        "/cep/360/avg"  
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        # Sprawdzenie czy odpowiedź jest poprawnym JSON-em
        try:
            json.loads(response.text)
        except ValueError as e:
            assert False, f"Response is not valid JSON: {e}"