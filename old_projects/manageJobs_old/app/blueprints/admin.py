import os
import shutil
import json
from flask import Blueprint, render_template, abort, g, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from app.models import User, Role, Group, Task, Notification
from app.utils import create_default_admin
from app.extensions import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

PERMISSIONS = {
    'User Management': ['user_create', 'user_ban', 'user_delete'],
    'Media & Gallery': [
        'media_view_all', 'media_manage', 'media_delete',
        'gallery_create', 'gallery_access', 'gallery_delete'
    ],
    'Chat': ['chat_delete', 'chat_sticker'],
    'Groups': ['group_create', 'group_manage'],
    'Tasks': ['task_manage']
}

@admin_bp.before_request
@login_required
def restrict_access():
    # Allow task management for everyone (viewing own tasks), but protect admin actions
    if request.endpoint == 'admin.tasks':
        return
    
    if not current_user.is_admin:
        flash('Unauthorized Access', 'danger')
        return redirect(url_for('dashboard.index'))

# --- NUKE DATA (OPERATOR ONLY) ---
@admin_bp.route('/nuke_data', methods=['POST'])
@login_required
def nuke_data():
    if current_user.role.name != 'operator':
        return jsonify({'status': 'error', 'msg': 'OPERATOR ONLY'}), 403
    
    data = request.json
    step1 = data.get('confirm_text')
    step2 = data.get('password')
    
    if step1 != "YES":
        return jsonify({'status': 'error', 'msg': 'Incorrect confirmation text.'}), 400
    
    if not current_user.check_password(step2):
        return jsonify({'status': 'error', 'msg': 'Invalid Password.'}), 400
        
    try:
        # 1. DATABASE WIPE
        # Drops the entire database associated with the connection
        db.connection.drop_database(db.get_db().name)
        
        # Re-initialize defaults (Operator, Roles)
        create_default_admin()
        
        # 2. FILE WIPE
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        if upload_folder and os.path.exists(upload_folder):
            # We want to keep the folder structure but remove files
            for root, dirs, files in os.walk(upload_folder):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
            
            # Re-create critical subfolders
            os.makedirs(os.path.join(upload_folder, 'avatars'), exist_ok=True)
            os.makedirs(os.path.join(upload_folder, 'shop'), exist_ok=True)

        return jsonify({'status': 'ok', 'msg': 'SYSTEM NUKED & RE-INITIALIZED.'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

# --- USER & GROUP MANAGEMENT ---

@admin_bp.route('/users')
def users():
    all_users = User.objects()
    all_groups = Group.objects()
    return render_template('admin/users.html', users=all_users, groups=all_groups)

@admin_bp.route('/groups')
def groups():
    all_groups = Group.objects()
    return render_template('admin/groups.html', groups=all_groups)

@admin_bp.route('/delete_group/<group_id>', methods=['POST'])
def delete_group(group_id):
    try:
        grp = Group.objects.get(id=group_id)
        grp.delete()
        flash('Group deleted.', 'success')
    except Exception:
        flash('Group not found.', 'danger')
    return redirect(url_for('admin.groups'))

@admin_bp.route('/group_perms/<group_id>', methods=['GET', 'POST'])
def group_perms(group_id):
    grp = Group.objects.get_or_404(id=group_id)
    
    if request.method == 'POST':
        new_perms = {}
        for category, keys in PERMISSIONS.items():
            for key in keys:
                if request.form.get(key) == 'on':
                    new_perms[key] = True
        
        grp.permissions = json.dumps(new_perms)
        grp.save()
        flash('Group permissions updated.', 'success')
        return redirect(url_for('admin.groups'))
        
    current_perms = json.loads(grp.permissions or '{}')
    return render_template('admin/permissions.html', target=grp, current_perms=current_perms, all_perms=PERMISSIONS, is_group=True)

@admin_bp.route('/create_group', methods=['POST'])
def create_group():
    if not current_user.has_perm('group_create'):
        return redirect(url_for('admin.users'))
        
    name = request.form.get('name')
    if name and not Group.objects(name=name).first():
        Group(name=name).save()
        flash('Group created.', 'success')
    else:
        flash('Group name invalid or exists.', 'warning')
    return redirect(url_for('admin.users'))

@admin_bp.route('/assign_group', methods=['POST'])
def assign_group():
    user_id = request.form.get('user_id')
    group_id = request.form.get('group_id')
    
    try:
        user = User.objects.get(id=user_id)
        if user.role.name != 'operator':
            if group_id:
                grp = Group.objects.get(id=group_id)
                # Assuming simple single-group assignment logic for now, or append
                if grp not in user.groups:
                    user.groups.append(grp)
            else:
                user.groups = [] # Clear groups if None selected
            user.save()
            flash('Group assigned.', 'success')
    except Exception as e:
        flash(f'Error assigning group: {e}', 'danger')
        
    return redirect(url_for('admin.users'))

# --- TASK MANAGEMENT ---

@admin_bp.route('/tasks')
def tasks():
    if not current_user.is_admin:
        # Regular user sees their own tasks
        my_tasks = Task.objects(assigned_to=current_user).order_by('-created_at')
        return render_template('admin/tasks.html', tasks=my_tasks, is_admin=False)
    
    # Admin sees all
    all_tasks = Task.objects.order_by('-created_at')
    users = User.objects()
    return render_template('admin/tasks.html', tasks=all_tasks, users=users, is_admin=True)

@admin_bp.route('/create_task', methods=['POST'])
def create_task():
    content = request.form.get('content') # Maps to 'title' in model
    description = request.form.get('description', '')
    
    if current_user.is_admin:
        user_id = request.form.get('user_id')
        if not user_id:
            flash("User ID required", "warning")
            return redirect(url_for('admin.tasks'))
            
        target_user = User.objects.get(id=user_id)
        t = Task(title=content, description=description, assigned_to=target_user, assigned_by=current_user)
        
        # Notify User
        Notification(
            user=target_user, 
            type='info', 
            category='task', 
            title='New Task Assigned', 
            content=content
        ).save()
    else:
        # Self assign
        t = Task(title=content, description=description, assigned_to=current_user, assigned_by=current_user)
        
    t.save()
    flash('Task created.', 'success')
    return redirect(url_for('admin.tasks'))

@admin_bp.route('/manage_task/<task_id>', methods=['POST'])
def manage_task(task_id):
    try:
        t = Task.objects.get(id=task_id)
        action = request.form.get('action')
        
        # Auth check: Owner or Admin
        if not current_user.is_admin and t.assigned_to.id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        if action == 'delete':
            t.delete()
            flash('Task deleted.', 'info')
            
        elif action == 'toggle':
            if t.status == 'completed':
                t.status = 'pending'
            else:
                t.status = 'completed'
            
            # --- KPI LOGIC ---
            # If task is now completed AND wasn't awarded AND assigned by Admin
            if t.status == 'completed' and not t.kpi_awarded and t.assigned_by and t.assigned_by.id != t.assigned_to.id:
                if t.assigned_by.role.name in ['operator', 'admin']:
                    # Award KPI
                    worker = t.assigned_to
                    worker.kpi += 50
                    worker.save()
                    
                    t.kpi_awarded = True
                    
                    # Notify Worker
                    Notification(
                        user=worker, 
                        type='success', 
                        category='shop', 
                        title='Task Complete +50 KPI', 
                        content=f"Good job! You earned 50 KPI for completing: {t.title}"
                    ).save()

            # Notify Assigner
            if t.status == 'completed' and t.assigned_by and t.assigned_by.id != t.assigned_to.id:
                 Notification(
                    user=t.assigned_by, 
                    type='success', 
                    category='task', 
                    title='Task Completed', 
                    content=f"{current_user.name} completed: {t.title}"
                 ).save()
            
            t.save()

        elif action == 'update':
            t.title = request.form.get('content')
            t.save()
            
    except Exception as e:
        flash(f'Error managing task: {e}', 'danger')
        
    return redirect(url_for('admin.tasks'))

# --- USER ACTIONS ---

@admin_bp.route('/create_user', methods=['POST'])
def create_user():
    username = request.form.get('username')
    password = request.form.get('password')
    role_name = request.form.get('role')
    
    # Logic to limit admins if needed
    if role_name == 'admin':
        admin_role = Role.objects(name='admin').first()
        if User.objects(role=admin_role).count() >= 5:
            flash('Limit Reached: Max 5 Admins allowed.', 'warning')
            return redirect(url_for('admin.users'))
            
    if User.objects(username=username).first():
        flash('Username exists', 'warning')
        return redirect(url_for('admin.users'))
        
    role = Role.objects(name=role_name).first()
    if not role:
        flash('Role not found', 'danger')
        return redirect(url_for('admin.users'))

    new_user = User(username=username, role=role, status='active')
    new_user.set_password(password)
    new_user.save()
    
    # Notify Operators
    op_role = Role.objects(name='operator').first()
    ops = User.objects(role=op_role)
    for op in ops:
        Notification(
            user=op, 
            type='info', 
            category='system', 
            title='New User', 
            content=f"Created: {username} ({role_name})"
        ).save()
    
    flash(f'User {username} created', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    if not current_user.has_perm('user_delete') and current_user.role.name != 'operator':
        flash('Permission Denied', 'danger')
        return redirect(url_for('admin.users'))
        
    try:
        user = User.objects.get(id=user_id)
        if user.role.name == 'operator':
            flash('Cannot delete operator.', 'danger')
            return redirect(url_for('admin.users'))
            
        user.delete()
        flash('User deleted.', 'success')
    except Exception:
        flash('User not found.', 'danger')
        
    return redirect(url_for('admin.users'))

@admin_bp.route('/permissions/<user_id>', methods=['GET', 'POST'])
def permissions(user_id):
    target = User.objects.get_or_404(id=user_id)
    
    if request.method == 'POST':
        new_perms = {}
        for category, keys in PERMISSIONS.items():
            for key in keys:
                if request.form.get(key) == 'on':
                    new_perms[key] = True
                    
        target.permissions = json.dumps(new_perms)
        target.save()
        flash('User permissions updated.', 'success')
        return redirect(url_for('admin.users'))
        
    current = json.loads(target.permissions or '{}')
    return render_template('admin/permissions.html', target=target, current_perms=current, all_perms=PERMISSIONS, is_group=False)

# --- PENDING REQUESTS ---

@admin_bp.route('/pending_requests')
def pending_requests():
    pending = User.objects(status='pending')
    return render_template('admin/pending.html', requests=pending)

@admin_bp.route('/approve_user/<user_id>', methods=['POST'])
def approve_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        user.status = 'active'
        user.save()
        flash(f'User {user.username} approved.', 'success')
    except:
        flash('User not found', 'danger')
    return redirect(url_for('admin.pending_requests'))

@admin_bp.route('/deny_user/<user_id>', methods=['POST'])
def deny_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        reason = request.form.get('reason', 'Denied by Operator')
        user.status = 'denied'
        user.denial_reason = reason
        user.save()
        flash(f'User {user.username} denied.', 'warning')
    except:
        flash('User not found', 'danger')
    return redirect(url_for('admin.pending_requests'))