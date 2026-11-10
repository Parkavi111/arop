import os
import tempfile

import pytest
from werkzeug.security import generate_password_hash

import database

# Use a throwaway database for every test. The real arop.db is never touched.
database.DB_PATH = os.path.join(tempfile.mkdtemp(), "test_arop.db")

from app import app as flask_app  # noqa: E402
from database import get_connection, init_db  # noqa: E402

TEST_USERNAME = "tester"
TEST_PASSWORD = "test-password-123"


@pytest.fixture(autouse=True)
def clean_db():
    init_db()
    connection = get_connection()
    for table in ("activity_logs", "tasks", "robots", "admin"):
        connection.execute(f"DELETE FROM {table}")
    connection.commit()
    connection.close()
    yield


@pytest.fixture
def conn():
    connection = get_connection()
    yield connection
    connection.close()


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as test_client:
        yield test_client


@pytest.fixture
def logged_in_client(client, conn):
    conn.execute(
        "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
        (TEST_USERNAME, generate_password_hash(TEST_PASSWORD)),
    )
    conn.commit()
    client.post(
        "/login", data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    return client


@pytest.fixture
def make_robot(conn):
    def _make(name="Robo", status="idle", battery=100):
        cursor = conn.execute(
            "INSERT INTO robots (name, status, battery) VALUES (?, ?, ?)",
            (name, status, battery),
        )
        conn.commit()
        return cursor.lastrowid

    return _make


@pytest.fixture
def make_task(conn):
    def _make(title="Task", priority="medium", status="pending", robot_id=None):
        cursor = conn.execute(
            "INSERT INTO tasks (title, priority, status, assigned_robot_id) "
            "VALUES (?, ?, ?, ?)",
            (title, priority, status, robot_id),
        )
        conn.commit()
        return cursor.lastrowid

    return _make


# end of conftest.py