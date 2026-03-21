import os
import time
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import User, ShopItem, UserInventory, Notification

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

# --- HELPER: USB PATH ---
def get_usb_shop_path():
    """Resolves absolute path to UPLOAD_FOLDER/shop (on USB)"""
    base = current_app.config['UPLOAD_FOLDER']
    path = os.path.join(base, 'shop')
    if not os.path.exists(path): os.makedirs(path)
    return path

@shop_bp.route('/')
@login_required
def index():
    if current_user.role == 'operator':
        items = ShopItem.objects()
    else:
        items = ShopItem.objects(is_active=True)
        
    inventory = UserInventory.objects(user_id=current_user.id)
    owned_ids = [str(i.item_id.id) for i in inventory] if inventory else []
    
    all_users = User.objects() if current_user.role == 'operator' else []
    
    return render_template('shop/index.html', items=items, owned_ids=owned_ids, users=all_users)

@shop_bp.route('/buy/<item_id>', methods=['POST'])
@login_required
def buy(item_id):
    item = ShopItem.objects(id=item_id).first_or_404()
    
    if not item.is_active and current_user.role != 'operator':
        return jsonify({'status': 'error', 'msg': 'Item is no longer available'})
        
    exists = UserInventory.objects(user_id=current_user.id, item_id=item.id).first()
    if exists:
        return jsonify({'status': 'error', 'msg': 'Already owned'})
    
    final_price = item.price
    if item.discount > 0:
        final_price = int(item.price * (1 - item.discount / 100))

    if current_user.kpi < final_price:
        return jsonify({'status': 'error', 'msg': 'Insufficient KPI! Complete more tasks to earn points.'})
    
    current_user.kpi -= final_price
    current_user.save()
    
    inv = UserInventory(user_id=current_user.id, item_id=item.id)
    inv.save()
    
    n = Notification(
        user=current_user.id, # UPDATED: user instead of user_id
        type='success', 
        category='shop',
        title='Item Purchased', 
        content=f"You bought '{item.name}' for {final_price} KPI."
    )
    n.save()
    
    return jsonify({'status': 'ok', 'new_balance': current_user.kpi})

@shop_bp.route('/equip/<item_id>', methods=['POST'])
@login_required
def equip(item_id):
    exists = UserInventory.objects(user_id=current_user.id, item_id=item_id).first()
    if not exists:
        return jsonify({'status': 'error', 'msg': 'Not owned'})
    
    item = ShopItem.objects(id=item_id).first()
    if not item:
        return jsonify({'status': 'error', 'msg': 'Item not found'})
    
    if item.type == 'namecard': 
        current_user.namecard_url = item.resource_url
    elif item.type == 'title': 
        current_user.active_title = item.title_content or item.name
        current_user.active_title_bg = item.resource_url
    elif item.type == 'background': 
        current_user.active_background = item.resource_url
    elif item.type == 'avatar_frame':
        current_user.active_avatar_frame = item.resource_url
    elif item.type == 'banner_frame':
        current_user.active_banner_frame = item.resource_url
    
    current_user.save()
    return jsonify({'status': 'ok'})

@shop_bp.route('/unequip', methods=['POST'])
@login_required
def unequip():
    type_to_clear = request.json.get('type', 'namecard')
    
    if type_to_clear == 'namecard': 
        current_user.namecard_url = None
    elif type_to_clear == 'title': 
        current_user.active_title = None
        current_user.active_title_bg = None
    elif type_to_clear == 'background': 
        current_user.active_background = None
    elif type_to_clear == 'avatar_frame':
        current_user.active_avatar_frame = None
    elif type_to_clear == 'banner_frame':
        current_user.active_banner_frame = None
        
    current_user.save()
    return jsonify({'status': 'ok'})

# --- OPERATOR COMMANDS ---

@shop_bp.route('/create_item', methods=['POST'])
@login_required
def create_item():
    if current_user.role != 'operator': return jsonify({'error': 'Denied'}), 403
    
    try:
        name = request.form.get('name')
        price_val = request.form.get('price', '')
        price = int(price_val) if price_val.isdigit() else 0
        disc_val = request.form.get('discount', '')
        discount = int(disc_val) if disc_val.isdigit() else 0
        desc = request.form.get('description', '')
        item_type = request.form.get('type', 'namecard')
        title_content = request.form.get('title_content', '') 
        
        resource = ""
        file = request.files.get('file')
        
        if file and file.filename:
            ts = int(time.time())
            ext = secure_filename(file.filename).split('.')[-1]
            filename = f"item_{ts}.{ext}"
            
            save_dir = get_usb_shop_path()
            file.save(os.path.join(save_dir, filename))
            
            resource = f"/shop_assets/{filename}"
        else:
            css_value = request.form.get('css_value')
            if css_value:
                resource = css_value
            elif item_type == 'title':
                resource = "#0d6efd"
            else:
                resource = ""
        
        item = ShopItem(
            name=name, 
            price=price, 
            discount=discount,
            description=desc, 
            resource_url=resource, 
            type=item_type,
            title_content=title_content
        )
        item.save()
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        print(f"Create Item Error: {e}")
        return jsonify({'error': str(e)}), 500

@shop_bp.route('/edit_item/<item_id>', methods=['POST'])
@login_required
def edit_item(item_id):
    if current_user.role != 'operator': return jsonify({'error': 'Denied'}), 403
    
    item = ShopItem.objects(id=item_id).first_or_404()
    item.name = request.form.get('name')
    
    price_str = request.form.get('price', '0')
    item.price = int(price_str) if price_str.isdigit() else 0
    
    disc_str = request.form.get('discount', '0')
    item.discount = int(disc_str) if disc_str.isdigit() else 0
    
    item.description = request.form.get('description')
    item.title_content = request.form.get('title_content')
    
    file = request.files.get('file')
    if file and file.filename:
        ts = int(time.time())
        ext = secure_filename(file.filename).split('.')[-1]
        filename = f"item_{ts}.{ext}"
        
        save_dir = get_usb_shop_path()
        file.save(os.path.join(save_dir, filename))
        
        if item.resource_url and '/shop_assets/' in item.resource_url:
            try:
                old_name = item.resource_url.split('/')[-1]
                old_path = os.path.join(save_dir, old_name)
                if os.path.exists(old_path): os.remove(old_path)
            except: pass
            
        item.resource_url = f"/shop_assets/{filename}"
    
    elif request.form.get('css_value'):
        item.resource_url = request.form.get('css_value')

    item.save()
    return jsonify({'status': 'ok'})

@shop_bp.route('/toggle_item/<item_id>', methods=['POST'])
@login_required
def toggle_item(item_id):
    if current_user.role != 'operator': return jsonify({'error': 'Denied'}), 403
    
    item = ShopItem.objects(id=item_id).first_or_404()
    item.is_active = not item.is_active
    item.save()
    
    return jsonify({'status': 'ok', 'new_state': item.is_active})

@shop_bp.route('/delete_item/<item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    if current_user.role != 'operator': return jsonify({'error': 'Denied'}), 403
    
    item = ShopItem.objects(id=item_id).first_or_404()
    
    if item.resource_url and '/shop_assets/' in item.resource_url:
        try:
            save_dir = get_usb_shop_path()
            old_name = item.resource_url.split('/')[-1]
            old_path = os.path.join(save_dir, old_name)
            if os.path.exists(old_path): os.remove(old_path)
        except: pass
        
    item.delete()
    return jsonify({'status': 'ok'})

@shop_bp.route('/give_kpi', methods=['POST'])
@login_required
def give_kpi():
    if current_user.role != 'operator': return jsonify({'error': 'Denied'}), 403
    
    target_id = request.json.get('user_id')
    amount = int(request.json.get('amount', 0))
    
    user = User.objects(id=target_id).first_or_404()
    user.kpi += amount
    user.save()
    
    n = Notification(
        user=user.id, # UPDATED: user instead of user_id
        type='success', 
        category='shop', 
        title='KPI Received', 
        content=f"Operator granted you {amount} KPI."
    )
    n.save()
    
    return jsonify({'status': 'ok', 'new_total': user.kpi})