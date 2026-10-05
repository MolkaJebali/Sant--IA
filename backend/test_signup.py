import requests
import json

url = "http://localhost:8000/api/auth/signup"
data = {
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "phone": "0123456789",
    "age": 25,
    "password": "password123",
    "password_confirm": "password123"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error connecting to server: {e}")
