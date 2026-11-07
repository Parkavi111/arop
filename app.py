from flask import Flask, jsonify, redirect, render_template, request

from database import get_connection, init_db

app = Flask(__name__)
init_db()


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


@app.route("/api/robots")
def api_robots():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM robots ORDER BY id").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(debug=True)