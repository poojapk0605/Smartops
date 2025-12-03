import requests
import os
import json

BACKEND_URL = os.getenv("TEST_URL", "http://localhost:8080")

def test_analyze_c():
    payload = {"code": "int main() { return 0; }"}
    r = requests.post(f"{BACKEND_URL}/analyze-code", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "best_flag" in data
    assert "flags" in data
