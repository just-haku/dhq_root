import os
import time
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app.models import User, Role
from app.extensions import db

# Note: Ensure url_prefix is handled in app/__init__.py if you want this at root
auth_bp = Blueprint('auth', __name__)

# --- HELPERS ---

def get_avatars_path():
    """Resolves absolute path to configured UPLOAD_FOLDER/avatars"""
    upload_root = current_app.config.get('UPLOAD_FOLDER')
    if not upload_root:
        # Fallback for dev if config missing
        base_path = os.path.abspath(os.path.join(current_app.root_path, '..', 'static', 'avatars'))
        return base_path
    return os.path.join(upload_root, 'avatars')

def delete_old_avatar(user):
    """Deletes local avatar file if it exists."""
    if not user.avatar: return
    
    # Check if it looks like a local file path (not an external URL)
    # Our format is typically /avatars/filename
    if user.avatar.startswith('/avatars/'):
        try:
            filename = user.avatar.split('/')[-1]
            file_path = os.path.join(get_avatars_path(), filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[INFO] Deleted old avatar: {file_path}")
        except Exception as e:
            print(f"[WARN] Failed to delete old avatar: {e}")

# --- ROUTES ---

@auth_bp.route('/secret-kuro-grp', methods=['GET', 'POST']) # <--- ADDED SECRET ROUTE
def login():
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = None
        password = None
        is_json = request.is_json

        # 1. Attempt to grab data based on Content-Type
        if is_json:
            data = request.get_json()
            if data:
                username = data.get('username')
                password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')

        # 2. Validate input presence
        if not username or not password:
            error_msg = 'Please provide both username and password.'
            if is_json:
                return jsonify({'success': False, 'message': error_msg}), 400
            flash(error_msg, 'error')
            return render_template('auth/login.html')

        # 3. Authenticate User
        # FIX: Changed from User.query (SQL) to User.objects (Mongo)
        user = User.objects(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            
            # Handle successful login response
            if is_json:
                return jsonify({'success': True, 'redirect': url_for('dashboard.index')})
            return redirect(url_for('dashboard.index'))
        
        else:
            # Handle failure
            error_msg = 'Invalid username or password.'
            if is_json:
                return jsonify({'success': False, 'message': error_msg}), 401
            flash(error_msg, 'error')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    # Redirect to the new secret login route
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        existing_user = User.objects(username=username).first()
        
        if existing_user:
            if existing_user.status == 'denied':
                reason = existing_user.denial_reason or "No reason provided."
                flash(f"Account name '{username}' was denied previously. Reason: {reason}", 'danger')
            elif existing_user.status == 'pending':
                 flash(f"Account '{username}' is already pending Operator approval.", 'warning')
            else:
                flash('Username already exists.', 'warning')
        else:
            # 1. Determine Default Role
            default_role = Role.objects(name='user').first()
            if not default_role:
                # Fallback: Create basic user role if DB is empty
                default_role = Role(name='user', permissions=['basic'])
                default_role.save()

            # 2. Create User
            new_user = User(username=username, role=default_role)
            new_user.set_password(password)
            
            # 3. Set Status (Pending by default, unless first user/bootstrapped)
            # Note: utils.py logic handles the first 'admin/kuro' creation as active.
            # Any public registration is pending.
            new_user.status = 'pending'
            new_user.save()
            
            flash('Registration request sent to Operator. Please wait for approval.', 'info')
            return redirect(url_for('auth.login'))
            
    return render_template('auth/register.html')

@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # 1. Update Profile Info
        if request.form.get('display_name'): 
            current_user.display_name = request.form.get('display_name')
        if request.form.get('bio'): 
            current_user.bio = request.form.get('bio')
        if request.form.get('api_key'): 
            current_user.api_key = request.form.get('api_key')
        
        # 2. Avatar Handling
        try:
            new_avatar_path = None
            
            # A. File Upload
            if 'avatar_file' in request.files:
                file = request.files['avatar_file']
                if file and file.filename.strip() != '':
                    delete_old_avatar(current_user)
                    
                    ts = int(time.time())
                    safe_name = secure_filename(file.filename)
                    fname = f"user_{current_user.id}_{ts}_{safe_name}"
                    
                    save_dir = get_avatars_path()
                    os.makedirs(save_dir, exist_ok=True)
                    
                    full_save_path = os.path.join(save_dir, fname)
                    file.save(full_save_path)
                    
                    # Store relative path for template usage
                    new_avatar_path = f"/avatars/{fname}"
            
            # B. URL Fallback (only if no file uploaded)
            if not new_avatar_path:
                url_input = request.form.get('avatar_url')
                if url_input and url_input.strip():
                    if current_user.avatar != url_input.strip():
                        delete_old_avatar(current_user)
                        new_avatar_path = url_input.strip()

            # C. Save Avatar
            if new_avatar_path:
                current_user.avatar = new_avatar_path

        except Exception as e:
            flash(f"Avatar update failed: {str(e)}", "danger")

        # 3. Password Update
        new_pw = request.form.get('new_password')
        if new_pw:
            current_user.set_password(new_pw)
            flash('Password Updated', 'success')
            
        current_user.save()
        flash('Settings Saved', 'success')
        
    return render_template('auth/settings.html')

@auth_bp.route('/reset_avatar', methods=['POST'])
@login_required
def reset_avatar():
    delete_old_avatar(current_user)
    current_user.avatar = "placeholder.png"
    current_user.save()
    flash('Avatar reset to default.', 'info')
    return jsonify({'status': 'ok'})

@auth_bp.route('/wordpress/<path:subpath>')
@auth_bp.route('/wp-admin/<path:subpath>')
def wordpress_honeypot(subpath=None):
    # Optional: Slow down the response to waste their time (Tarpit)
    import time
    time.sleep(5) 
    return render_template('clock/index.html'), 200 # Serve your login page instead