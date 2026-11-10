from simulation import simulate_step


def get_task(conn, task_id):
    return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def get_robot(conn, robot_id):
    return conn.execute("SELECT * FROM robots WHERE id = ?", (robot_id,)).fetchone()


def test_assigned_task_starts(conn, make_robot, make_task):
    robot_id = make_robot(status="busy", battery=100)
    task_id = make_task(status="assigned", robot_id=robot_id)
    simulate_step(conn)
    assert get_task(conn, task_id)["status"] == "in_progress"
    robot = get_robot(conn, robot_id)
    assert robot["battery"] == 95
    assert robot["location"] == "Task site"


def test_in_progress_task_finishes(conn, make_robot, make_task):
    robot_id = make_robot(status="busy", battery=95)
    task_id = make_task(status="in_progress", robot_id=robot_id)
    simulate_step(conn)
    assert get_task(conn, task_id)["status"] == "completed"
    robot = get_robot(conn, robot_id)
    assert robot["battery"] == 85
    assert robot["status"] == "idle"
    assert robot["location"] == "Base"


def test_full_cycle_takes_two_steps(conn, make_robot, make_task):
    robot_id = make_robot(status="busy", battery=100)
    task_id = make_task(status="assigned", robot_id=robot_id)
    simulate_step(conn)
    simulate_step(conn)
    assert get_task(conn, task_id)["status"] == "completed"
    robot = get_robot(conn, robot_id)
    assert robot["battery"] == 85
    assert robot["status"] == "idle"


def test_low_battery_robot_goes_to_charging(conn, make_robot, make_task):
    robot_id = make_robot(status="busy", battery=25)
    task_id = make_task(status="in_progress", robot_id=robot_id)
    simulate_step(conn)
    assert get_task(conn, task_id)["status"] == "completed"
    robot = get_robot(conn, robot_id)
    assert robot["battery"] == 15
    assert robot["status"] == "charging"
    assert robot["location"] == "Base"


def test_charging_robot_recovers_to_idle(conn, make_robot):
    robot_id = make_robot(status="charging", battery=15)
    simulate_step(conn)
    robot = get_robot(conn, robot_id)
    assert robot["battery"] == 35
    assert robot["status"] == "charging"
    simulate_step(conn)
    robot = get_robot(conn, robot_id)
    assert robot["battery"] == 55
    assert robot["status"] == "idle"


def test_battery_never_goes_below_zero(conn, make_robot, make_task):
    robot_id = make_robot(status="busy", battery=3)
    make_task(status="assigned", robot_id=robot_id)
    simulate_step(conn)
    assert get_robot(conn, robot_id)["battery"] == 0
    simulate_step(conn)
    assert get_robot(conn, robot_id)["battery"] == 0


def test_battery_never_goes_above_100(conn, make_robot):
    robot_id = make_robot(status="charging", battery=95)
    simulate_step(conn)
    robot = get_robot(conn, robot_id)
    assert robot["battery"] == 100
    assert robot["status"] == "idle"


def test_pending_task_is_left_alone(conn, make_robot, make_task):
    robot_id = make_robot(status="idle", battery=100)
    task_id = make_task(status="pending")
    simulate_step(conn)
    assert get_task(conn, task_id)["status"] == "pending"
    assert get_robot(conn, robot_id)["battery"] == 100


def test_simulation_writes_activity_logs(conn, make_robot, make_task):
    robot_id = make_robot(status="busy", battery=100)
    task_id = make_task(status="assigned", robot_id=robot_id)
    simulate_step(conn)
    log = conn.execute(
        "SELECT * FROM activity_logs WHERE task_id = ?", (task_id,)
    ).fetchone()
    assert log is not None
    assert log["event"] == "Moving to task site"


def test_simulate_button_requires_login(client):
    response = client.post("/simulate/step")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


# end of test_simulation.py