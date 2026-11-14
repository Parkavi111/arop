import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "arop.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_column(conn, table, column, definition):
    existing = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})")]
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS robots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'idle',
        battery INTEGER NOT NULL DEFAULT 100,
        location TEXT NOT NULL DEFAULT 'Base',
        capability TEXT NOT NULL DEFAULT 'light'
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'medium',
        status TEXT NOT NULL DEFAULT 'pending',
        assigned_robot_id INTEGER,
        required_capability TEXT NOT NULL DEFAULT 'light',
        FOREIGN KEY (assigned_robot_id) REFERENCES robots (id)
    );

    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        robot_id INTEGER,
        task_id INTEGER,
        event TEXT NOT NULL,
        timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (robot_id) REFERENCES robots (id),
        FOREIGN KEY (task_id) REFERENCES tasks (id)
    );
    """)
    ensure_column(conn, "robots", "capability", "TEXT NOT NULL DEFAULT 'light'")
    ensure_column(conn, "tasks", "required_capability", "TEXT NOT NULL DEFAULT 'light'")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database created: arop.db")


# end of database.py