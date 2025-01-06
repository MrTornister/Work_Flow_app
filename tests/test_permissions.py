import pytest
from fastapi.testclient import TestClient
from src.main import app
from models.user import UserRole
from src.auth.security import create_test_token

@pytest.mark.parametrize("role,expected_status", [
    (UserRole.ADMIN, 200),
    (UserRole.MANAGER, 403),
    (UserRole.USER, 403),
])
def test_user_management_access(client, role, expected_status):
    token = create_test_token(role)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == expected_status

def test_health_check(client):  # Use the fixture
    response = client.get("/health")
    assert response.status_code == 200