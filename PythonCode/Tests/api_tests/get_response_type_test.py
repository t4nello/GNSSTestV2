import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_response_content_type_json():
    endpoints = [
        "/sessions",
        "/devices",
        "/devices/2268",  
        "/data/360/all/position",  
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
        
        try:
            json.loads(response.text)
        except ValueError as e:
            assert False, f"Response is not valid JSON: {e}"