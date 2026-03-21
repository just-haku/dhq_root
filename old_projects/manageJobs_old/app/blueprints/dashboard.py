from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Task, Media, ChatMessage, User, MediaGroup, MediaComment, Notification
import json
import datetime

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.before_request
def update_last_seen():
    if current_user.is_authenticated:
        now = datetime.datetime.now()
        last = current_user.last_seen or datetime.datetime.min
        if (now - last).total_seconds() > 300:
            current_user.last_seen = now
            current_user.save() # MongoDB uses save() instead of commit()

# --- NOTIFICATION CENTER LOGIC ---

def flush_old_notifications(user_id):
    """Deletes notifications older than 20 days for the user"""
    cutoff = datetime.datetime.now() - datetime.timedelta(days=20)
    try:
        # MongoEngine syntax
        Notification.objects(user=current_user, timestamp__lt=cutoff).delete()
    except Exception as e:
        print(f"Error flushing notifs: {e}")

@dashboard_bp.route('/notifications')
@login_required
def get_notifications():
    # 1. Auto-flush old data
    flush_old_notifications(current_user.id)
    
    # 2. Fetch all notifs (Unread first, then newest)
    notifs = Notification.objects(user=current_user).order_by('is_read', '-timestamp').limit(50)
    
    return jsonify({
        'status': 'ok', 
        'unread_count': Notification.objects(user=current_user, is_read=False).count(),
        'data': [n.to_dict() for n in notifs]
    })

@dashboard_bp.route('/notifications/read/<notif_id>', methods=['POST'])
@login_required
def read_notification(notif_id):
    try:
        n = Notification.objects.get(id=notif_id)
        if n.user.id == current_user.id:
            n.is_read = True
            n.save()
        return jsonify({'status': 'ok'})
    except:
        return jsonify({'status': 'error', 'msg': 'Not found'}), 404

@dashboard_bp.route('/notifications/read_all', methods=['POST'])
@login_required
def read_all_notifications():
    Notification.objects(user=current_user, is_read=False).update(is_read=True)
    return jsonify({'status': 'ok'})

@dashboard_bp.route('/add_notification', methods=['POST'])
@login_required
def add_notification():
    # Helper for frontend to push notifs (e.g. stalled upload)
    data = request.json
    n = Notification(
        user=current_user,
        type=data.get('type', 'info'),
        category=data.get('category', 'system'),
        title=data.get('title'),
        content=data.get('content')
    )
    n.save()
    return jsonify({'status': 'ok'})

# --- DASHBOARD ROUTES ---

@dashboard_bp.route('/')
@login_required
def index():
    # MongoEngine query
    tasks = Task.objects(assigned_to=current_user).order_by('-created_at')
    
    can_view_all = (current_user.role.name == 'operator' or current_user.has_perm('media_view_all'))
    
    # Root Media
    if can_view_all:
        recent_root_media = Media.objects(group=None).order_by('-uploaded_at').limit(6)
    else:
        # Complex OR query in MongoEngine using Q objects
        from mongoengine.queryset.visitor import Q
        recent_root_media = Media.objects(
            Q(group=None) & (Q(is_public=True) | Q(uploaded_by=current_user)) & Q(is_hidden=False)
        ).order_by('-uploaded_at').limit(6)

    # Group Media Activity
    if can_view_all:
        recent_activity = Media.objects(group__ne=None).order_by('-uploaded_at').limit(50)
    else:
        recent_activity = Media.objects(
            Q(group__ne=None) & (Q(is_public=True) | Q(uploaded_by=current_user)) & Q(is_hidden=False)
        ).order_by('-uploaded_at').limit(50)
    
    seen_groups = set()
    recent_galleries = []
    
    for m in recent_activity:
        if not m.group: continue
        g = m.group
        if g.id not in seen_groups:
            # Check group access if not admin/operator
            # Note: allowed_users is now a ListField of References in Mongo model
            is_allowed = False
            if can_view_all or g.creator.id == current_user.id:
                is_allowed = True
            elif current_user in g.allowed_users:
                is_allowed = True
                
            if is_allowed:
                recent_galleries.append(g)
                seen_groups.add(g.id)
        if len(recent_galleries) >= 6: break

    recent_chat = ChatMessage.objects.order_by('-timestamp').limit(5)
    
    return render_template('dashboard/index.html', tasks=tasks, root_media=recent_root_media, gallery_updates=recent_galleries, chat=recent_chat, user=current_user)

@dashboard_bp.route('/add_task', methods=['POST'])
@login_required
def add_task():
    content = request.form.get('content')
    if content:
        # Create self-assigned task
        t = Task(title=content, assigned_to=current_user, assigned_by=current_user)
        t.save()
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/toggle_task/<id>')
@login_required
def toggle_task(id):
    try:
        t = Task.objects.get(id=id)
        if t.assigned_to.id == current_user.id:
            if t.status == 'completed':
                t.status = 'pending'
            else:
                t.status = 'completed'
            t.save()
    except Exception as e:
        print(f"Error toggling task: {e}")
        
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/chat')
@login_required
def chat():
    return render_template('base.html', content="<div class='container mt-5 text-center'><h1><i class='fas fa-comments text-muted'></i></h1><h3>Team Chat</h3><p class='text-muted'>This module is currently under construction.</p><a href='" + url_for('dashboard.index') + "' class='btn btn-secondary'>Back</a></div>")

@dashboard_bp.route('/folder_preview/<group_id>')
@login_required
def folder_preview(group_id):
    # Retrieve files for preview
    files = Media.objects(group=group_id).order_by('-uploaded_at').limit(12)
    visible_files = []
    
    can_view_all = (current_user.role.name == 'operator' or current_user.has_perm('media_view_all'))

    for f in files:
        if current_user.role.name != 'operator' and f.is_hidden: continue
        
        if not can_view_all and not f.is_public and f.uploaded_by.id != current_user.id:
            continue
            
        visible_files.append({
            'id': str(f.id), 
            'filename': f.filename, 
            'file_type': 'video' if f.mimetype.startswith('video') else 'image', 
            'reactions_count': len(f.reactions)
        })
        
    return jsonify({'status': 'ok', 'files': visible_files})