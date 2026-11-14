from flask import Blueprint, redirect, render_template, request

from database import get_connection

edit_bp = Blueprint("edit", __name__)

VALID_PRIORITIES = ("low", "medium", "high")
CAPABILITIES = ("light", "heavy")
MAX_NAME_LENGTH = 50


@edit_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    conn = get_connection()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND status = 'pending'", (task_id,)
    ).fetchone()
    if task is None:
        conn.close()
        return redirect("/tasks")

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        priority = request.form.get("priority", "medium")
        if priority not in VALID_PRIORITIES:
            priority = "medium"
        required = request.form.get("required_capability", task["required_capability"])
        if required not in CAPABILITIES:
            required = "light"
        if title:
            conn.execute(
                "UPDATE tasks SET title = ?, priority = ?, required_capability = ? "
                "WHERE id = ? AND status = 'pending'",
                (title, priority, required, task_id),
            )
            conn.commit()
            conn.close()
            return redirect("/tasks")

    conn.close()
    return render_template("edit_task.html", task=task)


@edit_bp.route("/robots/<int:robot_id>/edit", methods=["GET", "POST"])
def edit_robot(robot_id):
    conn = get_connection()
    robot = conn.execute(
        "SELECT * FROM robots WHERE id = ?", (robot_id,)
    ).fetchone()
    if robot is None:
        conn.close()
        return redirect("/robots")

    if request.method == "POST":
        name = request.form.get("name", "").strip()[:MAX_NAME_LENGTH]
        if name:
            conn.execute(
                "UPDATE robots SET name = ? WHERE id = ?", (name, robot_id)
            )
            conn.commit()
            conn.close()
            return redirect("/robots")

    conn.close()
    return render_template("edit_robot.html", robot=robot)


# end of edit.py