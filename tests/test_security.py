from werkzeug.security import generate_password_hash

EVIL = "http://evil.example"


def get_task(conn, task_id):
    return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def test_post_from_other_site_is_rejected(logged_in_client, conn, make_task):
    task_id = make_task(status="pending")
    response = logged_in_client.post(
        f"/tasks/{task_id}/delete", headers={"Origin": EVIL}
    )
    assert response.status_code == 403
    assert get_task(conn, task_id) is not None


def test_post_with_other_site_referer_is_rejected(
    logged_in_client, conn, make_task
):
    task_id = make_task(status="pending")
    response = logged_in_client.post(
        f"/tasks/{task_id}/delete", headers={"Referer": EVIL + "/page"}
    )
    assert response.status_code == 403
    assert get_task(conn, task_id) is not None


def test_post_from_own_site_is_allowed(logged_in_client, conn, make_task):
    task_id = make_task(status="pending")
    response = logged_in_client.post(
        f"/tasks/{task_id}/delete", headers={"Origin": "http://localhost"}
    )
    assert response.status_code == 302
    assert get_task(conn, task_id) is None


def test_login_post_from_other_site_is_rejected(client, conn):
    conn.execute(
        "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
        ("tester", generate_password_hash("test-password-123")),
    )
    conn.commit()
    response = client.post(
        "/login",
        data={"username": "tester", "password": "test-password-123"},
        headers={"Origin": EVIL},
    )
    assert response.status_code == 403
    assert client.get("/dashboard").status_code == 302


def test_get_pages_are_not_checked(client):
    response = client.get("/login", headers={"Origin": EVIL})
    assert response.status_code == 200


def test_null_origin_is_rejected(logged_in_client, conn, make_task):
    task_id = make_task(status="pending")
    response = logged_in_client.post(
        f"/tasks/{task_id}/delete", headers={"Origin": "null"}
    )
    assert response.status_code == 403
    assert get_task(conn, task_id) is not None


# end of test_security.py