from werkzeug.security import generate_password_hash

PROTECTED_PAGES = ("/dashboard", "/robots", "/tasks", "/logs", "/reports")


def test_pages_require_login(client):
    for path in PROTECTED_PAGES:
        response = client.get(path)
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/login")


def test_login_page_is_open(client):
    assert client.get("/login").status_code == 200


def test_wrong_password_is_rejected(client, conn):
    conn.execute(
        "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
        ("tester", generate_password_hash("test-password-123")),
    )
    conn.commit()
    response = client.post(
        "/login", data={"username": "tester", "password": "wrong-password"}
    )
    assert response.status_code == 200
    assert b"Wrong username or password" in response.data
    assert client.get("/dashboard").status_code == 302


def test_correct_password_logs_in(logged_in_client):
    assert logged_in_client.get("/dashboard").status_code == 200


def test_logout_locks_pages_again(logged_in_client):
    logged_in_client.post("/logout")
    assert logged_in_client.get("/dashboard").status_code == 302


# end of test_auth.py