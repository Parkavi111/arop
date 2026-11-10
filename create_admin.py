from werkzeug.security import generate_password_hash

from database import get_connection, init_db


def main():
    init_db()
    username = input("Admin username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return
    password = input("Admin password (visible, min 8 characters): ")
    confirm = input("Repeat password: ")
    if len(password) < 8:
        print("Password must be at least 8 characters.")
        return
    if password != confirm:
        print("Passwords do not match.")
        return

    password_hash = generate_password_hash(password)
    conn = get_connection()
    existing = conn.execute(
        "SELECT id FROM admin WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE admin SET password_hash = ? WHERE id = ?",
            (password_hash, existing["id"]),
        )
        print("Password updated.")
    else:
        conn.execute(
            "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        print("Admin created.")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()


# end of create_admin.py