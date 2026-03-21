import os
import time
import hashlib
import mimetypes
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import Media, MediaGroup, MediaComment, MediaReaction, CustomReaction, User, Notification, SavedCollection
from mongoengine.queryset.visitor import Q

media_bp = Blueprint('media', __name__, url_prefix='/media')

# Setup logger
logger = logging.getLogger(__name__)

# Fallback extensions if not in config
DEFAULT_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'ico', 'svg'}

# --- HELPERS ---

def allowed_file(filename):
    """Checks file extension against config."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', DEFAULT_ALLOWED_EXTENSIONS)
    return ext in allowed

def generate_safe_hash(filename):
    """Generates a secure hash name for the file to prevent overwrites and guessing."""
    ext = os.path.splitext(filename)[1].lower()
    unique_str = f"{filename}_{time.time()}"
    hash_name = hashlib.sha256(unique_str.encode()).hexdigest()
    return f"{hash_name}{ext}"

def serve_favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static', 'img'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def serve_placeholder_file():
    return send_from_directory(os.path.join(current_app.root_path, 'static', 'img'), 'placeholder.png')

@media_bp.record_once
def register_auxiliary_routes(state):
    state.app.add_url_rule('/favicon.ico', 'favicon', serve_favicon)
    state.app.add_url_rule('/static/img/favicon.svg', 'favicon_svg_fix', serve_favicon)
    state.app.add_url_rule('/static/images/favicon.svg', 'favicon_svg_images_fix', serve_favicon)
    state.app.add_url_rule('/dashboard/placeholder.png', 'dashboard_placeholder_fix', serve_placeholder_file)

# --- ROUTES ---

@media_bp.route('/')
@media_bp.route('/gallery')
@media_bp.route('/gallery/<group_id>')
@login_required
def gallery(group_id=None):
    current_group = None
    security_filter = Q(is_public=True) | Q(user=current_user) | Q(allowed_users__in=[current_user])

    if group_id:
        current_group = MediaGroup.objects.get_or_404(id=group_id)
        files = Media.objects(security_filter & Q(group=current_group) & Q(is_hidden=False)).order_by('-uploaded_at')
    else:
        files = Media.objects(security_filter & Q(is_hidden=False)).order_by('-uploaded_at')

    user_groups = MediaGroup.objects(Q(creator=current_user) | Q(allowed_users__in=[current_user]))
    custom_reactions = CustomReaction.objects()
    
    return render_template('media/gallery.html', 
                          media_items=files, 
                          groups=user_groups, 
                          current_group=current_group,
                          custom_reactions=custom_reactions)

@media_bp.route('/file/<path:filename>')
@login_required
def serve_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@media_bp.route('/placeholder.png')
def serve_placeholder():
    return serve_placeholder_file()

@media_bp.route('/thumb/<path:filename>')
@login_required
def serve_thumb(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@media_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    user_groups = MediaGroup.objects(Q(creator=current_user) | Q(allowed_users__in=[current_user]))

    if request.method == 'POST':
        if 'file' not in request.files:
            if request.is_json: return jsonify({'error': 'No file part'}), 400
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            if request.is_json: return jsonify({'error': 'No selected file'}), 400
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                original_filename = secure_filename(file.filename)
                hashed_filename = generate_safe_hash(original_filename)
                
                ext = original_filename.rsplit('.', 1)[1].lower()
                file_type = 'video' if ext in ['mp4', 'mov', 'avi'] else 'image'
                
                subfolder = str(current_user.id)
                save_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
                os.makedirs(save_dir, exist_ok=True)
                
                full_path = os.path.join(save_dir, hashed_filename)
                file.save(full_path)
                
                rel_path = os.path.join(subfolder, hashed_filename)

                caption = request.form.get('caption', '')
                group_id = request.form.get('group_id')
                is_public = True if request.form.get('is_public') == 'on' else False
                
                group = None
                if group_id:
                    group = MediaGroup.objects(id=group_id).first()

                new_media = Media(
                    filename=hashed_filename,
                    original_filename=original_filename, 
                    file_type=file_type, 
                    filepath=rel_path,
                    mimetype=file.mimetype or mimetypes.guess_type(original_filename)[0],
                    user=current_user,
                    group=group,
                    caption=caption,
                    is_public=is_public,
                    uploaded_at=datetime.utcnow() 
                )
                new_media.save()
                
                if request.is_json:
                    return jsonify({'success': True, 'filename': rel_path})
                
                flash('File uploaded successfully!', 'success')
                return redirect(url_for('media.gallery'))
                
            except Exception as e:
                logger.error(f"Upload Error: {e}")
                if request.is_json: return jsonify({'error': str(e)}), 500
                flash(f'Error: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            msg = 'File type not allowed.'
            if request.is_json: return jsonify({'error': msg}), 400
            flash(msg, 'warning')

    return render_template('media/upload.html', groups=user_groups)

@media_bp.route('/create_group', methods=['POST'])
@login_required
def create_group():
    try:
        # --- DEBUG LOGGING START ---
        print(f"DEBUG create_group - Content-Type: {request.content_type}")
        print(f"DEBUG create_group - Form Keys: {list(request.form.keys())}")
        # --- DEBUG LOGGING END ---

        # 1. Try Request Form (Standard POST)
        name = request.form.get('name')
        
        # 2. Try JSON Body (AJAX)
        if not name:
            try:
                json_data = request.get_json(silent=True, force=True)
                if json_data and isinstance(json_data, dict):
                    name = json_data.get('name')
            except Exception:
                pass

        # 3. Try Query Params (Just in case)
        if not name:
            name = request.args.get('name')

        if not name:
            print("DEBUG create_group - ERROR: 'name' missing in all request sources.")
            return jsonify({'error': 'Group Name is required.'}), 400

        avatar = request.files.get('avatar')
        
        group = MediaGroup(name=name, creator=current_user)
        group.allowed_users = [current_user]
        
        if avatar and allowed_file(avatar.filename):
            hash_name = generate_safe_hash(secure_filename(avatar.filename))
            avatar_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            avatar.save(os.path.join(avatar_dir, hash_name))
            group.avatar = hash_name 
            
        group.save()
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'ok', 'id': str(group.id), 'name': group.name})
            
        flash('Group created', 'success')
        return redirect(url_for('media.gallery'))

    except Exception as e:
        logger.error(f"Error in create_group: {e}")
        return jsonify({'error': str(e)}), 500

@media_bp.route('/delete_group/<group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    group = MediaGroup.objects.get_or_404(id=group_id)
    
    is_admin = getattr(current_user, 'is_admin', False) or getattr(current_user, 'role', '') == 'admin'
    
    if not is_admin and current_user.id != group.creator.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    files = Media.objects(group=group)
    for f in files:
        try:
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f.filepath)
            if os.path.exists(full_path):
                os.remove(full_path)
        except: pass
        f.delete()
        
    group.delete()
    return jsonify({'status': 'ok'})

@media_bp.route('/details/<media_id>', methods=['GET'])
@login_required
def details(media_id):
    media = Media.objects.get_or_404(id=media_id)
    
    comments_list = []
    for c in media.comments:
        user_name = c.username_snapshot
        user_avatar = ''
        if c.user:
            user_name = c.user.name
            user_avatar = getattr(c.user, 'avatar', '')
            
        comments_list.append({
            'user': user_name,
            'avatar': user_avatar,
            'text': c.content,
            'time': c.timestamp.strftime('%Y-%m-%d %H:%M')
        })

    reaction_counts = {}
    for r in media.reactions:
        reaction_counts[r.reaction_type] = reaction_counts.get(r.reaction_type, 0) + 1

    is_admin = getattr(current_user, 'is_admin', False) or getattr(current_user, 'role', '') == 'admin'

    uploader_name = media.user.name if media.user else 'Unknown'
    uploader_avatar = getattr(media.user, 'avatar', '') if media.user else ''
    is_owner = (media.user and current_user.id == media.user.id)

    return jsonify({
        'id': str(media.id),
        'filename': media.filename, 
        'url': url_for('media.serve_file', filename=media.filepath),
        'uploader': uploader_name,
        'uploader_avatar': uploader_avatar,
        'upload_date': media.uploaded_at.strftime('%Y-%m-%d'),
        'caption': media.caption,
        'comments': comments_list,
        'reactions': reaction_counts,
        'can_edit': (is_admin or is_owner),
        'can_hide': is_admin
    })

@media_bp.route('/manage_file', methods=['POST'])
@login_required
def manage_file():
    data = request.json
    action = data.get('action')
    media_id = data.get('media_id')
    
    media = Media.objects.get_or_404(id=media_id)
    
    is_admin = getattr(current_user, 'is_admin', False) or getattr(current_user, 'role', '') == 'admin'
    is_owner = media.user and current_user.id == media.user.id
    
    if not is_admin and not is_owner:
        return jsonify({'error': 'Unauthorized'}), 403

    if action == 'delete':
        try:
            full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], media.filepath)
            if os.path.exists(full_path):
                os.remove(full_path)
        except: pass
        media.delete()
        
    elif action == 'rename':
        media.filename = data.get('value') 
        media.save()
        
    elif action == 'caption':
        media.caption = data.get('value')
        media.save()
        
    elif action == 'report':
        media.reports += 1
        media.save()
        if media.user:
            # UPDATED: user instead of user_id
            Notification(
                user=media.user, 
                type='warning', 
                title='Post Reported', 
                content=f"Your post {media.filename} was reported."
            ).save()

    elif action == 'hide' and is_admin:
        media.is_hidden = not media.is_hidden
        media.save()

    return jsonify({'status': 'ok'})

@media_bp.route('/react/<media_id>', methods=['POST'])
@login_required
def react(media_id):
    media = Media.objects.get_or_404(id=media_id)
    r_type = request.form.get('type')
    
    media.update(pull__reactions__user=current_user)
    media.reload()
    
    new_react = MediaReaction(
        user=current_user, 
        username_snapshot=current_user.name, 
        reaction_type=r_type
    )
    media.reactions.append(new_react)
    media.save()
    
    return jsonify({'status': 'ok'})

@media_bp.route('/clear_reactions/<media_id>', methods=['POST'])
@login_required
def clear_reactions(media_id):
    media = Media.objects.get_or_404(id=media_id)
    media.update(pull__reactions__user=current_user)
    return jsonify({'status': 'ok'})

@media_bp.route('/comment/<media_id>', methods=['POST'])
@login_required
def comment(media_id):
    media = Media.objects.get_or_404(id=media_id)
    content = request.form.get('content')
    if content:
        c = MediaComment(
            user=current_user, 
            username_snapshot=current_user.name, 
            content=content
        )
        media.comments.append(c)
        media.save()
    return jsonify({'status': 'ok'})

@media_bp.route('/save_post', methods=['POST'])
@login_required
def save_post():
    data = request.json
    media_id = data.get('media_id')
    media = Media.objects.get(id=media_id)
    
    coll = SavedCollection.objects(user=current_user).first()
    if not coll:
        coll = SavedCollection(user=current_user)
    
    if media not in coll.items:
        coll.items.append(media)
        coll.save()
        
    return jsonify({'status': 'ok'})

@media_bp.route('/add_custom_reaction', methods=['POST'])
@login_required
def add_custom_reaction():
    file = request.files.get('file')
    name = request.form.get('name')
    
    if file and name and allowed_file(file.filename):
        hash_name = generate_safe_hash(secure_filename(file.filename))
        
        shop_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'shop')
        os.makedirs(shop_dir, exist_ok=True)
        file.save(os.path.join(shop_dir, hash_name))
        
        CustomReaction(
            name=name, 
            image_url=url_for('media.serve_file', filename=f"shop/{hash_name}"),
            created_by=current_user
        ).save()
        
        return jsonify({'status': 'ok'})
        
    return jsonify({'error': 'Invalid file or data'}), 400