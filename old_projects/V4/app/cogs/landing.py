from flask import Blueprint, render_template

# Create a new blueprint named "landing"
landing_bp = Blueprint('landing', __name__)

@landing_bp.route("/")
def index():
    # Render the landing page (index.html)
    return render_template("index.html")

@landing_bp.route("/login")
def login():
    # Render the login page (login.html)
    return render_template("login.html")
