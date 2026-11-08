from flask import Blueprint, render_template

from database import get_connection

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard_page():
    conn = get_connection()
    robots = conn.execute("SELECT * FROM robots ORDER BY id").fetchall()
    task_rows = conn.execute(
        "SELECT status, COUNT(*) AS n FROM tasks GROUP BY status"
    ).fetchall()
    recent = conn.execute(
        """
        SELECT activity_logs.*, robots.name AS robot_name,
               tasks.title AS task_title
        FROM activity_logs
        LEFT JOIN robots ON activity_logs.robot_id = robots.id
        LEFT JOIN tasks ON activity_logs.task_id = tasks.id
        ORDER BY activity_logs.id DESC
        LIMIT 5
        """
    ).fetchall()
    conn.close()

    robot_counts = {}
    for robot in robots:
        robot_counts[robot["status"]] = robot_counts.get(robot["status"], 0) + 1
    task_counts = {row["status"]: row["n"] for row in task_rows}
    if robots:
        avg_battery = round(sum(r["battery"] for r in robots) / len(robots))
    else:
        avg_battery = 0

    return render_template(
        "dashboard.html",
        robots=robots,
        robot_counts=robot_counts,
        task_counts=task_counts,
        total_tasks=sum(task_counts.values()),
        avg_battery=avg_battery,
        recent=recent,
    )


# end of dashboard.py