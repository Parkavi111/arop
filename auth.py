import os
import secrets
from urllib.parse import urlparse

from flask import Blueprint, abort, redirect, render_template, request, session
from werkzeug.security import check_password_hash

from database import get_connection

auth_bp = Blueprint("auth", __name__)

UNSAFE_METHODS = ("POST", "PUT", "PATCH", "DELETE")


def check_origin():
    if request.method not in UNSAFE_METHODS:
        return None
    source = request.headers.get("Origin") or request.headers.get("Referer")
    if source and urlparse(source).netloc != request.host:
        abort(403)
    return None


def require_login():
    if request.endpoint in ("auth.login", "static"):
        return None
    if session.get("admin_id"):
        return None
    return redirect("/login")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_connection()
        admin = conn.execute(
            "SELECT * FROM admin WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id"]
            return redirect("/dashboard")
        error = "Wrong username or password."
    return render_template("login.html", error=error)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")


def init_auth(app):
    app.secret_key = os.environ.get("AROP_SECRET_KEY") or secrets.token_hex(32)
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.register_blueprint(auth_bp)
    app.before_request(check_origin)
    app.before_request(require_login)


# end of auth.py