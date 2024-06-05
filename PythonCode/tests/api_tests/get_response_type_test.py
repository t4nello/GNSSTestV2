import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_response_content_type_json():
    endpoints = [
        "/sessions",
        "/devices",
        "/devices?sessionid=2268",  
        "/session/data?sessionid=360&device=all&field=position",  
        "/average?sessionid=360", 
        "/mode?sessionid=360",
        "/session/field-count?sessionid=360&field=latitude",
        "/sigma?sessionid=360&reference_type=avg",
        "/drms?sessionid=360&reference_type=mode", 
        "/2drms?sessionid=360&reference_type=avg", 
        "/cep?sessionid=360&reference_type=avg"  
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        try:
            json.loads(response.text)
        except ValueError as e:
            assert False, f"Response is not valid JSON: {e}"
