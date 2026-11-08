from flask import Blueprint, render_template

from database import get_connection

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports")
def reports_page():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    completed = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'completed'"
    ).fetchone()[0]
    per_robot = conn.execute(
        """
        SELECT robots.name AS name, COUNT(tasks.id) AS done
        FROM robots
        LEFT JOIN tasks
               ON tasks.assigned_robot_id = robots.id
              AND tasks.status = 'completed'
        GROUP BY robots.id
        ORDER BY robots.id
        """
    ).fetchall()
    per_priority = conn.execute(
        """
        SELECT priority,
               COUNT(*) AS total,
               SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS done
        FROM tasks
        GROUP BY priority
        ORDER BY CASE priority
                     WHEN 'high' THEN 1
                     WHEN 'medium' THEN 2
                     ELSE 3
                 END
        """
    ).fetchall()
    conn.close()

    rate = round(completed * 100 / total) if total else 0
    return render_template(
        "reports.html",
        total=total,
        completed=completed,
        rate=rate,
        per_robot=per_robot,
        per_priority=per_priority,
    )


# end of reports.py