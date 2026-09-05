import pytest
from fastapi.testclient import TestClient

def test_api_health_check(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_api_auth_login(client: TestClient):
    res = client.post("/api/auth/login", json={
        "email": "student@campusflow.edu",
        "password": "Password123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "STUDENT"

def test_api_get_resources(client: TestClient):
    res = client.get("/api/resources")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 8

def test_api_ai_understand(client: TestClient):
    login_res = client.post("/api/auth/login", json={
        "email": "student@campusflow.edu",
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    prompt = "I need Seminar Hall A on September 15 from 10 AM to 1 PM for 250 students for a CSE technical symposium. We need a projector and microphone. We can shift the event by one hour."
    res = client.post("/api/ai/understand-request", json={"prompt": prompt}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["preferred_resource"] == "Seminar Hall A"
    assert data["data"]["participant_count"] == 250

def test_api_analytics_overview(client: TestClient):
    res = client.get("/api/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert "performance_metrics" in data
    assert "resource_utilization_rate" in data["performance_metrics"]
    assert "fairness_index" in data["performance_metrics"]
