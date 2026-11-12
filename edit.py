from flask import Blueprint, redirect, render_template, request

from database import get_connection

edit_bp = Blueprint("edit", __name__)

VALID_PRIORITIES = ("low", "medium", "high")


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
        if title:
            conn.execute(
                "UPDATE tasks SET title = ?, priority = ? "
                "WHERE id = ? AND status = 'pending'",
                (title, priority, task_id),
            )
            conn.commit()
            conn.close()
            return redirect("/tasks")

    conn.close()
    return render_template("edit_task.html", task=task)


# end of edit.py