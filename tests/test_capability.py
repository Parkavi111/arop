from app import assign_task, auto_allocate


def new_robot(conn, capability, battery=100, name="R"):
    cursor = conn.execute(
        "INSERT INTO robots (name, capability, battery) VALUES (?, ?, ?)",
        (name, capability, battery),
    )
    conn.commit()
    return cursor.lastrowid


def new_task(conn, required, priority="medium", title="T"):
    cursor = conn.execute(
        "INSERT INTO tasks (title, priority, required_capability) VALUES (?, ?, ?)",
        (title, priority, required),
    )
    conn.commit()
    return cursor.lastrowid


def get_task(conn, task_id):
    return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def get_robot(conn, robot_id):
    return conn.execute("SELECT * FROM robots WHERE id = ?", (robot_id,)).fetchone()


def test_light_robot_cannot_take_heavy_task(conn):
    robot_id = new_robot(conn, "light")
    task_id = new_task(conn, "heavy")
    assert assign_task(conn, task_id, robot_id) is False
    assert get_task(conn, task_id)["status"] == "pending"


def test_heavy_robot_can_take_heavy_task(conn):
    robot_id = new_robot(conn, "heavy")
    task_id = new_task(conn, "heavy")
    assert assign_task(conn, task_id, robot_id) is True


def test_heavy_robot_can_take_light_task(conn):
    robot_id = new_robot(conn, "heavy")
    task_id = new_task(conn, "light")
    assert assign_task(conn, task_id, robot_id) is True


def test_auto_gives_light_task_to_light_robot_first(conn):
    new_robot(conn, "heavy", battery=100, name="H")
    light_id = new_robot(conn, "light", battery=80, name="L")
    task_id = new_task(conn, "light")
    auto_allocate(conn)
    assert get_task(conn, task_id)["assigned_robot_id"] == light_id


def test_auto_heavy_task_needs_heavy_robot(conn):
    new_robot(conn, "light")
    task_id = new_task(conn, "heavy")
    assert auto_allocate(conn) == 0
    assert get_task(conn, task_id)["status"] == "pending"


def test_auto_skips_unfit_task_and_continues(conn):
    new_robot(conn, "light")
    heavy_id = new_task(conn, "heavy", priority="high", title="heavy job")
    light_id = new_task(conn, "light", priority="medium", title="light job")
    assert auto_allocate(conn) == 1
    assert get_task(conn, heavy_id)["status"] == "pending"
    assert get_task(conn, light_id)["status"] == "assigned"


def test_add_robot_saves_capability(logged_in_client, conn):
    logged_in_client.post("/robots/add", data={"name": "Big", "capability": "heavy"})
    robot = conn.execute("SELECT * FROM robots WHERE name = 'Big'").fetchone()
    assert robot["capability"] == "heavy"


def test_strange_robot_capability_becomes_light(logged_in_client, conn):
    logged_in_client.post("/robots/add", data={"name": "Odd", "capability": "giant"})
    robot = conn.execute("SELECT * FROM robots WHERE name = 'Odd'").fetchone()
    assert robot["capability"] == "light"


def test_add_task_saves_required_capability(logged_in_client, conn):
    logged_in_client.post(
        "/tasks/add",
        data={"title": "Lift", "priority": "high", "required_capability": "heavy"},
    )
    task = conn.execute("SELECT * FROM tasks WHERE title = 'Lift'").fetchone()
    assert task["required_capability"] == "heavy"


def test_edit_task_changes_required_capability(logged_in_client, conn):
    task_id = new_task(conn, "light", title="Old")
    logged_in_client.post(
        f"/tasks/{task_id}/edit",
        data={"title": "Old", "priority": "medium", "required_capability": "heavy"},
    )
    assert get_task(conn, task_id)["required_capability"] == "heavy"


# end of test_capability.py