from database import get_connection, init_db


def seed_robots():
    init_db()
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM robots").fetchone()[0]
    if count > 0:
        print("Robots already exist. Nothing added.")
    else:
        conn.executemany(
            "INSERT INTO robots (name, status, battery, location) VALUES (?, ?, ?, ?)",
            [
                ("Robo-1", "idle", 100, "Base"),
                ("Robo-2", "idle", 100, "Base"),
                ("Robo-3", "idle", 100, "Base"),
            ],
        )
        conn.commit()
        print("3 sample robots added.")
    conn.close()


if __name__ == "__main__":
    seed_robots()