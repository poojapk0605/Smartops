import requests
import os

BACKEND_URL = os.getenv("TEST_URL", "http://localhost:8080")

def test_health():
    response = requests.get(f"{BACKEND_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
