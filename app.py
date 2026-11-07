from flask import Flask, jsonify

from database import get_connection, init_db

app = Flask(__name__)
init_db()


@app.route("/")
def home():
    return "AROP is running"


@app.route("/api/robots")
def api_robots():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM robots ORDER BY id").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    app.run(debug=True)