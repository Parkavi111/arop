from flask import Blueprint, render_template

from database import get_connection

logs_bp = Blueprint("logs", __name__)


@logs_bp.route("/logs")
def logs_page():
    conn = get_connection()
    logs = conn.execute(
        """
        SELECT activity_logs.*, robots.name AS robot_name,
               tasks.title AS task_title
        FROM activity_logs
        LEFT JOIN robots ON activity_logs.robot_id = robots.id
        LEFT JOIN tasks ON activity_logs.task_id = tasks.id
        ORDER BY activity_logs.id DESC
        LIMIT 100
        """
    ).fetchall()
    conn.close()
    return render_template("logs.html", logs=logs)


# end of logs.py