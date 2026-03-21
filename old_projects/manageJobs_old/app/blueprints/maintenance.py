import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user, logout_user
from flush_data import perform_nuke

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@maintenance_bp.route('/nuke', methods=['GET', 'POST'])
@login_required
def nuke():
    # Security: Only Admin/Operator allowed
    if not current_user.is_admin:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        password = request.form.get('nuke_password')
        required_password = os.environ.get('NUKE_PASSWORD')
        confirm_text = request.form.get('confirm_text')

        # 1. Check if ENV is set
        if not required_password:
            flash("System Error: NUKE_PASSWORD is not set in environment variables.", "danger")
            return redirect(request.url)

        # 2. Verify Credentials
        if password == required_password and confirm_text == 'NUKE':
            try:
                # 3. Perform Nuke
                # We pass current_app._get_current_object() to ensure the real app instance is used
                logs = perform_nuke(current_app._get_current_object())
                
                # 4. Cleanup Session
                logout_user()
                flash("SYSTEM WIPE COMPLETE. Please restart the server if needed.", "success")
                
                return render_template('maintenance/nuke_results.html', logs=logs)
            except Exception as e:
                flash(f"An error occurred during nuke: {e}", "danger")
        else:
            flash("Invalid password or confirmation text.", "danger")

    return render_template('maintenance/nuke.html')