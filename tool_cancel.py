import requests

try:
    response = requests.put("http://localhost:8000/reservations/3/cancel", json={"reason": "test"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
