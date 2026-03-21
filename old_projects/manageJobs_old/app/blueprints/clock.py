from flask import Blueprint, render_template, current_app
import os

clock_bp = Blueprint('clock', __name__)

@clock_bp.route('/')
def index():
    return render_template('clock/index.html')

@clock_bp.route('/diag')
def diag():
    static_folder = current_app.static_folder
    js_path = os.path.join(static_folder, 'js', 'clock_robust.js')
    exists = os.path.exists(js_path)
    return f"Looking for JS at: {js_path}<br>Exists: {exists}"