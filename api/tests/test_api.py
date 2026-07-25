# tests/test_api.py
import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def token():
    """Login and return a valid access token."""
    response = httpx.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    return data["access_token"]


def test_login_success():
    """1. Login returns a valid token."""
    response = httpx.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 0


def test_protected_list_requires_auth():
    """2a. Protected list route rejects requests with no token."""
    response = httpx.get(f"{BASE_URL}/customers/")
    assert response.status_code == 401


def test_protected_list_with_auth(token):
    """2b. Protected list route succeeds with a valid token."""
    response = httpx.get(
        f"{BASE_URL}/customers/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_customer(token):
    """3. Create a customer, confirm it persists with a real ID."""
    import uuid
    unique_email = f"test.{uuid.uuid4().hex[:8]}@example.com"

    response = httpx.post(
        f"{BASE_URL}/customers/",
        headers={"Authorization": f"Bearer {token}"},
        json={"first_name": "Test", "last_name": "User", "email": unique_email},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == unique_email
    assert "id" in body
    get_response = httpx.get(
        f"{BASE_URL}/customers/{body['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["email"] == unique_email