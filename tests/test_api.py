import pytest
from fastapi.testclient import TestClient
from src.main import app

# Remove this line
# client = TestClient(app)

def test_health_check(client):  # Use the fixture
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_protected_endpoint_unauthorized(client):
    response = client.get("/protected")
    assert response.status_code == 401

def test_protected_endpoint_authorized(client, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200