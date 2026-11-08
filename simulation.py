MIN_BATTERY = 20
DRAIN_START = 5
DRAIN_FINISH = 10
CHARGE_PER_STEP = 20
CHARGED_LEVEL = 50


def log_event(conn, robot_id, task_id, event):
    conn.execute(
        "INSERT INTO activity_logs (robot_id, task_id, event) VALUES (?, ?, ?)",
        (robot_id, task_id, event),
    )


def charge_robots(conn):
    robots = conn.execute(
        "SELECT * FROM robots WHERE status = 'charging' ORDER BY id"
    ).fetchall()
    for robot in robots:
        battery = min(100, robot["battery"] + CHARGE_PER_STEP)
        if battery >= CHARGED_LEVEL:
            conn.execute(
                "UPDATE robots SET battery = ?, status = 'idle' WHERE id = ?",
                (battery, robot["id"]),
            )
            log_event(conn, robot["id"], None, "Charged, back to idle")
        else:
            conn.execute(
                "UPDATE robots SET battery = ? WHERE id = ?", (battery, robot["id"])
            )
            log_event(conn, robot["id"], None, "Charging")


def start_task(conn, task, robot):
    battery = max(0, robot["battery"] - DRAIN_START)
    conn.execute("UPDATE tasks SET status = 'in_progress' WHERE id = ?", (task["id"],))
    conn.execute(
        "UPDATE robots SET battery = ?, location = 'Task site' WHERE id = ?",
        (battery, robot["id"]),
    )
    log_event(conn, robot["id"], task["id"], "Moving to task site")


def finish_task(conn, task, robot):
    battery = max(0, robot["battery"] - DRAIN_FINISH)
    new_status = "charging" if battery < MIN_BATTERY else "idle"
    conn.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task["id"],))
    conn.execute(
        "UPDATE robots SET battery = ?, status = ?, location = 'Base' WHERE id = ?",
        (battery, new_status, robot["id"]),
    )
    log_event(conn, robot["id"], task["id"], "Task completed, back at Base")
    if new_status == "charging":
        log_event(conn, robot["id"], None, "Battery low, charging")


def simulate_step(conn):
    tasks = conn.execute(
        """
        SELECT * FROM tasks
        WHERE status IN ('assigned', 'in_progress')
          AND assigned_robot_id IS NOT NULL
        ORDER BY id
        """
    ).fetchall()
    charge_robots(conn)
    for task in tasks:
        robot = conn.execute(
            "SELECT * FROM robots WHERE id = ?", (task["assigned_robot_id"],)
        ).fetchone()
        if robot is None:
            continue
        if task["status"] == "assigned":
            start_task(conn, task, robot)
        else:
            finish_task(conn, task, robot)
    conn.commit()


# end of simulation.py