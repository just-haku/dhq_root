# app/cogs/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import get_user_by_username

auth_bp = Blueprint("auth", __name__)

# Hardcoded operator credentials:
OP_USERNAME = "Haku"
# Pre-compute the hashed password for "00491E4C". In production you might want to store this elsewhere.
OP_PASSWORD_HASH = generate_password_hash("00491E4C")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        # Check if this is the operator account.
        if username == OP_USERNAME:
            if check_password_hash(OP_PASSWORD_HASH, password):
                session["user_role"] = "operator"
                session["username"] = username
                return redirect(url_for("operator.index"))
            else:
                return "Invalid operator credentials", 401
        else:
            # Check user in MongoDB (their password should be stored hashed).
            user = get_user_by_username(username)
            if user and check_password_hash(user.get("password", ""), password):
                session["user_role"] = "user"
                session["user_id"] = str(user["_id"])
                session["username"] = username
                return redirect(url_for("user.index"))
            else:
                return "Invalid credentials", 401
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
