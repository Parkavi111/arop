def get_task(conn, task_id):
    return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def test_delete_pending_task(logged_in_client, conn, make_task):
    task_id = make_task(status="pending")
    logged_in_client.post(f"/tasks/{task_id}/delete")
    assert get_task(conn, task_id) is None


def test_cannot_delete_assigned_task(
    logged_in_client, conn, make_robot, make_task
):
    robot_id = make_robot(status="busy")
    task_id = make_task(status="assigned", robot_id=robot_id)
    logged_in_client.post(f"/tasks/{task_id}/delete")
    assert get_task(conn, task_id) is not None


def test_cannot_delete_completed_task(
    logged_in_client, conn, make_robot, make_task
):
    robot_id = make_robot(status="idle")
    task_id = make_task(status="completed", robot_id=robot_id)
    logged_in_client.post(f"/tasks/{task_id}/delete")
    assert get_task(conn, task_id) is not None


def test_delete_requires_login(client, conn, make_task):
    task_id = make_task(status="pending")
    response = client.post(f"/tasks/{task_id}/delete")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    assert get_task(conn, task_id) is not None


# end of test_tasks.py