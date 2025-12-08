from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_analyze_c():
    payload = {"code": "int main() { return 0; }"}
    response = client.post("/analyze-code", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "best_flag" in data
    assert "flags" in data
    assert "language" in data
