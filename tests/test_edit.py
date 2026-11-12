def get_task(conn, task_id):
    return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def test_edit_page_opens_for_pending_task(logged_in_client, make_task):
    task_id = make_task(title="Wash floor", status="pending")
    response = logged_in_client.get(f"/tasks/{task_id}/edit")
    assert response.status_code == 200
    assert b"Wash floor" in response.data


def test_edit_saves_title_and_priority(logged_in_client, conn, make_task):
    task_id = make_task(title="Old", priority="low", status="pending")
    logged_in_client.post(
        f"/tasks/{task_id}/edit", data={"title": "New", "priority": "high"}
    )
    task = get_task(conn, task_id)
    assert task["title"] == "New"
    assert task["priority"] == "high"


def test_strange_priority_is_saved_as_medium(logged_in_client, conn, make_task):
    task_id = make_task(title="Old", priority="low", status="pending")
    logged_in_client.post(
        f"/tasks/{task_id}/edit", data={"title": "Old", "priority": "urgent"}
    )
    assert get_task(conn, task_id)["priority"] == "medium"


def test_empty_title_is_not_saved(logged_in_client, conn, make_task):
    task_id = make_task(title="Keep me", priority="low", status="pending")
    logged_in_client.post(
        f"/tasks/{task_id}/edit", data={"title": "   ", "priority": "high"}
    )
    task = get_task(conn, task_id)
    assert task["title"] == "Keep me"
    assert task["priority"] == "low"


def test_cannot_edit_assigned_task(logged_in_client, conn, make_robot, make_task):
    robot_id = make_robot(status="busy")
    task_id = make_task(title="Busy", status="assigned", robot_id=robot_id)
    page = logged_in_client.get(f"/tasks/{task_id}/edit")
    assert page.status_code == 302
    logged_in_client.post(
        f"/tasks/{task_id}/edit", data={"title": "Changed", "priority": "high"}
    )
    assert get_task(conn, task_id)["title"] == "Busy"


def test_cannot_edit_completed_task(logged_in_client, conn, make_robot, make_task):
    robot_id = make_robot(status="idle")
    task_id = make_task(title="Done", status="completed", robot_id=robot_id)
    logged_in_client.post(
        f"/tasks/{task_id}/edit", data={"title": "Changed", "priority": "high"}
    )
    assert get_task(conn, task_id)["title"] == "Done"


def test_edit_requires_login(client, conn, make_task):
    task_id = make_task(title="Locked", status="pending")
    page = client.get(f"/tasks/{task_id}/edit")
    assert page.status_code == 302
    assert page.headers["Location"].endswith("/login")
    client.post(f"/tasks/{task_id}/edit", data={"title": "Hacked", "priority": "high"})
    assert get_task(conn, task_id)["title"] == "Locked"


# end of test_edit.py