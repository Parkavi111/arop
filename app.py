from flask import Flask, jsonify, redirect, render_template, request

from database import get_connection, init_db
from simulation import simulate_step

app = Flask(__name__)
init_db()

VALID_PRIORITIES = ("low", "medium", "high")
MIN_BATTERY = 20


def assign_task(conn, task_id, robot_id):
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    robot = conn.execute("SELECT * FROM robots WHERE id = ?", (robot_id,)).fetchone()
    if task is None or robot is None:
        return False
    if task["status"] != "pending":
        return False
    if robot["status"] != "idle" or robot["battery"] < MIN_BATTERY:
        return False
    conn.execute(
        "UPDATE tasks SET status = 'assigned', assigned_robot_id = ? WHERE id = ?",
        (robot_id, task_id),
    )
    conn.execute("UPDATE robots SET status = 'busy' WHERE id = ?", (robot_id,))
    conn.execute(
        "INSERT INTO activity_logs (robot_id, task_id, event) VALUES (?, ?, ?)",
        (robot_id, task_id, "Task assigned"),
    )
    conn.commit()
    return True


def auto_allocate(conn):
    assigned_count = 0
    pending = conn.execute(
        """
        SELECT id FROM tasks
        WHERE status = 'pending'
        ORDER BY CASE priority
                     WHEN 'high' THEN 1
                     WHEN 'medium' THEN 2
                     ELSE 3
                 END, id
        """
    ).fetchall()
    for task in pending:
        robot = conn.execute(
            """
            SELECT id FROM robots
            WHERE status = 'idle' AND battery >= ?
            ORDER BY battery DESC, id
            LIMIT 1
            """,
            (MIN_BATTERY,),
        ).fetchone()
        if robot is None:
            break
        if assign_task(conn, task["id"], robot["id"]):
            assigned_count += 1
    return assigned_count


@app.route("/")
def home():
    return redirect("/robots")


@app.route("/robots")
def robots_page():
    conn = get_connection()
    robots = conn.execute("SELECT * FROM robots ORDER BY id").fetchall()
    conn.close()
    return render_template("robots.html", robots=robots)


@app.route("/robots/add", methods=["POST"])
def add_robot():
    name = request.form.get("name", "").strip()
    if name:
        conn = get_connection()
        conn.execute("INSERT INTO robots (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
    return redirect("/robots")


@app.route("/robots/<int:robot_id>/delete", methods=["POST"])
def delete_robot(robot_id):
    conn = get_connection()
    has_tasks = conn.execute(
        "SELECT 1 FROM tasks WHERE assigned_robot_id = ? LIMIT 1", (robot_id,)
    ).fetchone()
    has_logs = conn.execute(
        "SELECT 1 FROM activity_logs WHERE robot_id = ? LIMIT 1", (robot_id,)
    ).fetchone()
    if not has_tasks and not has_logs:
        conn.execute("DELETE FROM robots WHERE id = ?", (robot_id,))
        conn.commit()
    conn.close()
    return redirect("/robots")


@app.route("/tasks")
def tasks_page():
    conn = get_connection()
    tasks = conn.execute(
        """
        SELECT tasks.*, robots.name AS robot_name
        FROM tasks
        LEFT JOIN robots ON tasks.assigned_robot_id = robots.id
        ORDER BY tasks.id
        """
    ).fetchall()
    available_robots = conn.execute(
        "SELECT * FROM robots WHERE status = 'idle' AND battery >= ? ORDER BY id",
        (MIN_BATTERY,),
    ).fetchall()
    conn.close()
    return render_template(
        "tasks.html", tasks=tasks, available_robots=available_robots
    )


@app.route("/tasks/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    priority = request.form.get("priority", "medium")
    if priority not in VALID_PRIORITIES:
        priority = "medium"
    if title:
        conn = get_connection()
        conn.execute(
            "INSERT INTO tasks (title, priority) VALUES (?, ?)",
            (title, priority),
        )
        conn.commit()
        conn.close()
    return redirect("/tasks")


@app.route("/tasks/<int:task_id>/assign", methods=["POST"])
def assign_task_route(task_id):
    robot_id = request.form.get("robot_id", type=int)
    if robot_id is not None:
        conn = get_connection()
        assign_task(conn, task_id, robot_id)
        conn.close()
    return redirect("/tasks")


@app.route("/tasks/auto-assign", methods=["POST"])
def auto_assign_route():
    conn = get_connection()
    auto_allocate(conn)
    conn.close()
    return redirect("/tasks")


@app.route("/simulate/step", methods=["POST"])
def simulate_step_route():
    conn = get_connection()
    simulate_step(conn)
    conn.close()
    return redirect("/tasks")


@app.route("/api/robots")
def api_robots():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM robots ORDER BY id").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(debug=True)