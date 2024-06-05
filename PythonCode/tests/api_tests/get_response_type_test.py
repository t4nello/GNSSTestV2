import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_response_content_type_json():
    endpoints = [
        "/sessions",
        "/devices",
        "/devices?session_id=2268",  
        "/session/data?session_id=360&device=all&field=position",  
        "/average?session_id=360", 
        "/mode?session_id=360",
        "/session/field-count?session_id=360&field=latitude",
        "/sigma?session_id=360&reference_type=avg",
        "/drms?session_id=360&reference_type=mode", 
        "/2drms?session_id=360&reference_type=avg", 
        "/cep?session_id=360&reference_type=avg"  
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        try:
            json.loads(response.text)
        except ValueError as e:
            assert False, f"Response is not valid JSON: {e}"
