from app import assign_task, auto_allocate


def get_task(conn, task_id):
    return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def get_robot(conn, robot_id):
    return conn.execute("SELECT * FROM robots WHERE id = ?", (robot_id,)).fetchone()


def test_assign_works(conn, make_robot, make_task):
    robot_id = make_robot(status="idle", battery=100)
    task_id = make_task()
    assert assign_task(conn, task_id, robot_id) is True
    task = get_task(conn, task_id)
    assert task["status"] == "assigned"
    assert task["assigned_robot_id"] == robot_id
    assert get_robot(conn, robot_id)["status"] == "busy"


def test_assign_allows_exactly_20_percent(conn, make_robot, make_task):
    robot_id = make_robot(battery=20)
    task_id = make_task()
    assert assign_task(conn, task_id, robot_id) is True


def test_assign_rejects_19_percent(conn, make_robot, make_task):
    robot_id = make_robot(battery=19)
    task_id = make_task()
    assert assign_task(conn, task_id, robot_id) is False
    assert get_task(conn, task_id)["status"] == "pending"
    assert get_robot(conn, robot_id)["status"] == "idle"


def test_assign_rejects_busy_robot(conn, make_robot, make_task):
    robot_id = make_robot(status="busy", battery=100)
    task_id = make_task()
    assert assign_task(conn, task_id, robot_id) is False
    assert get_task(conn, task_id)["status"] == "pending"


def test_assign_rejects_task_that_is_not_pending(conn, make_robot, make_task):
    robot_id = make_robot()
    task_id = make_task(status="in_progress")
    assert assign_task(conn, task_id, robot_id) is False
    assert get_task(conn, task_id)["status"] == "in_progress"


def test_assign_writes_activity_log(conn, make_robot, make_task):
    robot_id = make_robot()
    task_id = make_task()
    assign_task(conn, task_id, robot_id)
    log = conn.execute(
        "SELECT * FROM activity_logs WHERE task_id = ?", (task_id,)
    ).fetchone()
    assert log is not None
    assert log["robot_id"] == robot_id
    assert log["event"] == "Task assigned"


def test_auto_allocate_high_priority_first(conn, make_robot, make_task):
    make_robot(name="A")
    make_robot(name="B")
    low_id = make_task(title="low", priority="low")
    high_id = make_task(title="high", priority="high")
    medium_id = make_task(title="medium", priority="medium")
    assert auto_allocate(conn) == 2
    assert get_task(conn, high_id)["status"] == "assigned"
    assert get_task(conn, medium_id)["status"] == "assigned"
    assert get_task(conn, low_id)["status"] == "pending"


def test_auto_allocate_prefers_highest_battery(conn, make_robot, make_task):
    make_robot(name="weak", battery=60)
    strong_id = make_robot(name="strong", battery=90)
    task_id = make_task()
    auto_allocate(conn)
    assert get_task(conn, task_id)["assigned_robot_id"] == strong_id


def test_auto_allocate_with_no_robots(conn, make_task):
    task_id = make_task()
    assert auto_allocate(conn) == 0
    assert get_task(conn, task_id)["status"] == "pending"


def test_cannot_delete_robot_that_has_tasks(
    logged_in_client, conn, make_robot, make_task
):
    robot_id = make_robot()
    make_task(status="assigned", robot_id=robot_id)
    logged_in_client.post(f"/robots/{robot_id}/delete")
    assert get_robot(conn, robot_id) is not None


def test_can_delete_unused_robot(logged_in_client, conn, make_robot):
    robot_id = make_robot()
    logged_in_client.post(f"/robots/{robot_id}/delete")
    assert get_robot(conn, robot_id) is None


# end of test_allocation.py