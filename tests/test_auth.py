import pytest
from fastapi.testclient import TestClient
from src.main import app
from models.user import User, UserRole
from src.auth.security import SecurityUtils

def test_user_creation(client):
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "Test123!",
        "role": UserRole.USER
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == user_data["username"]

def test_login_success(client, test_user):
    login_data = {
        "username": "testuser",
        "password": "Test123!"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(client):
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 401

def test_health_check(client):  # Use the fixture
    response = client.get("/health")
    assert response.status_code == 200