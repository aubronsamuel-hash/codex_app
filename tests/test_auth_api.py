"""Integration tests for the authentication API."""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.security import create_access_token, create_refresh_token, decode_token
from app.models import User


def signup_user(client: TestClient, email: str = "user@example.com", password: str = "SuperSecret1!") -> dict[str, Any]:
    response = client.post("/auth/signup", json={"email": email, "password": password})
    assert response.status_code == 201
    return response.json()


def login_user(client: TestClient, email: str, password: str) -> tuple[dict[str, Any], int]:
    response = client.post("/auth/login", json={"email": email, "password": password})
    return response.json(), response.status_code


def test_signup_creates_user(client: TestClient) -> None:
    payload = signup_user(client)

    assert payload["email"] == "user@example.com"
    assert payload["is_active"] is True
    assert "password_hash" not in payload


def test_signup_conflict_on_duplicate_email(client: TestClient) -> None:
    signup_user(client)
    response = client.post("/auth/signup", json={"email": "user@example.com", "password": "AnotherPass2!"})

    assert response.status_code == 409
    assert response.json()["detail"] == "Email is already registered"


def test_login_returns_tokens(client: TestClient) -> None:
    signup_user(client)
    tokens, status_code = login_user(client, "user@example.com", "SuperSecret1!")

    assert status_code == 200
    assert "access_token" in tokens and "refresh_token" in tokens

    access_payload = decode_token(tokens["access_token"])
    refresh_payload = decode_token(tokens["refresh_token"])

    assert access_payload.type == "access"
    assert refresh_payload.type == "refresh"
    assert access_payload.sub == refresh_payload.sub


def test_login_rejects_bad_password(client: TestClient) -> None:
    signup_user(client)
    _, status_code = login_user(client, "user@example.com", "WrongPassword")

    assert status_code == 401


def test_login_rejects_unknown_email(client: TestClient) -> None:
    response = client.post(
        "/auth/login", json={"email": "missing@example.com", "password": "irrelevant"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_rejects_inactive_user(client: TestClient, db_session: Session) -> None:
    signup_user(client)
    user = db_session.scalar(select(User).where(User.email == "user@example.com"))
    assert user is not None
    user.is_active = False
    db_session.commit()

    response = client.post(
        "/auth/login", json={"email": "user@example.com", "password": "SuperSecret1!"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "User is inactive"


def test_me_requires_authentication(client: TestClient) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401

    signup_user(client)
    tokens, _ = login_user(client, "user@example.com", "SuperSecret1!")

    auth_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert auth_response.status_code == 200
    assert auth_response.json()["email"] == "user@example.com"

    refresh_header_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )

    assert refresh_header_response.status_code == 401
    assert refresh_header_response.json()["detail"] == "Invalid token type"


def test_refresh_returns_new_access_token(client: TestClient) -> None:
    signup_user(client)
    tokens, _ = login_user(client, "user@example.com", "SuperSecret1!")

    refresh_response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert refresh_response.status_code == 200
    payload = decode_token(refresh_response.json()["access_token"])

    assert payload.type == "access"
    assert payload.sub == decode_token(tokens["refresh_token"]).sub


def test_refresh_rejects_access_token(client: TestClient) -> None:
    signup_user(client)
    tokens, _ = login_user(client, "user@example.com", "SuperSecret1!")

    response = client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token type"


def test_refresh_rejects_invalid_token(client: TestClient) -> None:
    response = client.post("/auth/refresh", json={"refresh_token": "invalid"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"


def test_refresh_rejects_expired_token(client: TestClient) -> None:
    user = signup_user(client)
    expired_token = create_refresh_token(user["id"], ttl_seconds=-1)

    response = client.post("/auth/refresh", json={"refresh_token": expired_token})

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token expired"


def test_refresh_rejects_invalid_subject(client: TestClient) -> None:
    token = create_refresh_token("not-an-int")

    response = client.post("/auth/refresh", json={"refresh_token": token})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token subject"


def test_me_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"


def test_me_rejects_expired_token(client: TestClient) -> None:
    user = signup_user(client)
    expired_token = create_access_token(user["id"], ttl_seconds=-1)

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token expired"


def test_me_rejects_invalid_subject(client: TestClient) -> None:
    token = create_access_token("not-an-int")

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token subject"


def test_me_rejects_missing_user(client: TestClient, db_session: Session) -> None:
    user_payload = signup_user(client)
    access_token = create_access_token(user_payload["id"])

    user = db_session.get(User, user_payload["id"])
    assert user is not None
    db_session.delete(user)
    db_session.commit()

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not found or inactive"


def test_me_rejects_inactive_user(client: TestClient, db_session: Session) -> None:
    user_payload = signup_user(client)
    access_token = create_access_token(user_payload["id"])

    user = db_session.get(User, user_payload["id"])
    assert user is not None
    user.is_active = False
    db_session.commit()

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User not found or inactive"
