from flask import Flask, jsonify, redirect, render_template, request

from database import get_connection, init_db

app = Flask(__name__)
init_db()

VALID_PRIORITIES = ("low", "medium", "high")


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
    conn.close()
    return render_template("tasks.html", tasks=tasks)


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


@app.route("/api/robots")
def api_robots():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM robots ORDER BY id").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(debug=True)