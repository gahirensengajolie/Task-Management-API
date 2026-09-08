from tests.conftest import register_and_login


def test_password_never_stored_in_plaintext(client, db_session):
    from app.models.user import User

    client.post(
        "/auth/register",
        json={"email": "secure@example.com", "password": "MySecretPass123", "full_name": "S"},
    )
    user = db_session.query(User).filter(User.email == "secure@example.com").first()
    assert user.hashed_password != "MySecretPass123"
    assert user.hashed_password.startswith("$2b$")  # bcrypt prefix


def test_password_not_returned_in_any_response(client):
    headers = register_and_login(client, "noleak@example.com", "NoLeakPass123")
    resp = client.get("/expenses", headers=headers)
    assert "password" not in resp.text
    assert "hashed_password" not in resp.text
    assert "NoLeakPass123" not in resp.text


def test_expired_or_malformed_token_rejected(client):
    bad_tokens = [
        "totally.invalid.token",
        "",
        "Bearer",
    ]
    for token in bad_tokens:
        resp = client.get("/expenses", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401


def test_sql_injection_style_input_handled_safely(client):
    # SQLAlchemy's parameterized queries should neutralize this; we assert
    # the app doesn't error out or leak data, just treats it as a literal
    # (nonexistent) email.
    resp = client.post(
        "/auth/login",
        json={"email": "' OR '1'='1", "password": "whatever"},
    )
    assert resp.status_code in (401, 422)


def test_health_check_does_not_require_auth(client):
    resp = client.get("/health")
    assert resp.status_code == 200
