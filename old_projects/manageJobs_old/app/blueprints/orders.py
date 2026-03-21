from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Collaboration, Order, User
from app.utils import calculate_crooked_growth
import requests
import datetime
from mongoengine.queryset.visitor import Q

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')
API_URL = "https://tangtuongtacre.com/api/v2"

@orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('orders/create.html')
    
    data = request.json
    if not data: return jsonify({'status': 'error', 'msg': 'No data'}), 400

    try:
        timeline = data.get('timeline', [])
        collab_name = data.get('name', 'Untitled Collaboration')
        
        # MONGO FIX: Instantiate directly and save
        # Note: 'user' is a ReferenceField in models.py, so we pass current_user object
        collab = Collaboration(
            name=collab_name,
            user=current_user,
            service_id=str(data['service_id']),
            service_name=data['service_name'],
            link=data['link'],
            total_days=float(data.get('days', 1)),
            step_hours=float(data.get('step', 1)),
            tolerance_pct=float(data.get('tolerance', 0)),
            total_quantity=int(data.get('final_a', 0))
        )
        collab.save()

        start_time = datetime.datetime.now()
        for step in timeline:
            offset = float(step['time_offset_hours'])
            scheduled_at = start_time + datetime.timedelta(hours=offset)
            
            new_order = Order(
                collaboration=collab,
                quantity=int(step['amount']),
                scheduled_time=scheduled_at,
                status='Pending' 
            )
            new_order.save()

        return jsonify({'status': 'ok', 'collab_id': str(collab.id)})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@orders_bp.route('/manage')
@login_required
def manage():
    # MONGO FIX: Use .objects() for querying
    if current_user.role == 'operator':
        active = Collaboration.objects(is_deleted=False).order_by('-created_at')
    else:
        active = Collaboration.objects(user=current_user, is_deleted=False).order_by('-created_at')
    return render_template('orders/manage.html', orders=active)

@orders_bp.route('/preview', methods=['POST'])
@login_required
def preview():
    data = request.json
    try:
        total_a = int(data.get('total_a', 0))
        days = float(data.get('days', 1))
        step = float(data.get('step', 1))
        tolerance = float(data.get('tolerance', 0))
        
        timeline, final_a = calculate_crooked_growth(total_a, days, step, tolerance)
        return jsonify({'status': 'ok', 'timeline': timeline, 'final_a': final_a})
    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 400

@orders_bp.route('/details/<collab_id>')
@login_required
def details(collab_id):
    # MONGO FIX: get_or_404 using string ID
    collab = Collaboration.objects(id=collab_id).first_or_404()
    
    if collab.user.id != current_user.id and current_user.role != 'operator':
        return jsonify({'status': 'error'}), 403
        
    # MONGO FIX: Query orders manually since we don't have a backref list
    orders_list = Order.objects(collaboration=collab)
    
    orders_data = []
    for o in orders_list:
        orders_data.append({
            'id': str(o.id),
            'quantity': o.quantity,
            'scheduled_time': o.scheduled_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': o.status,
            'api_id': o.api_order_id or '-',
            'api_response': o.api_response or ''
        })
    orders_data.sort(key=lambda x: x['scheduled_time'])

    return jsonify({
        'status': 'ok',
        'collab_name': collab.name,
        'orders': orders_data
    })

# --- NEW ACTIONS ---

@orders_bp.route('/toggle_pending/<order_id>', methods=['POST'])
@login_required
def toggle_pending(order_id):
    order = Order.objects(id=order_id).first_or_404()
    
    if order.collaboration.user.id != current_user.id and current_user.role != 'operator':
        return jsonify({'status': 'error'}), 403
    
    if order.status in ['Pending', 'Not Pending']:
        order.status = 'Not Pending' if order.status == 'Pending' else 'Pending'
        order.save()
        return jsonify({'status': 'ok', 'new_status': order.status})
    
    return jsonify({'status': 'error', 'msg': 'Cannot change status of executed order'}), 400

@orders_bp.route('/retry_order/<order_id>', methods=['POST'])
@login_required
def retry_order(order_id):
    """Resets a Failed order to Pending so Cron can pick it up again"""
    order = Order.objects(id=order_id).first_or_404()
    
    if order.collaboration.user.id != current_user.id and current_user.role != 'operator':
        return jsonify({'status': 'error', 'msg': 'Unauthorized'}), 403

    if order.status == 'Failed':
        order.status = 'Pending'
        order.api_response = None
        # Also re-enable auto_check if it was paused
        order.collaboration.auto_check = True
        order.collaboration.save() # Don't forget to save parent if modified
        order.save()
        return jsonify({'status': 'ok', 'msg': 'Order reactivated (Pending)'})
    
    return jsonify({'status': 'error', 'msg': 'Order is not in Failed state'}), 400

@orders_bp.route('/ignore_order/<order_id>', methods=['POST'])
@login_required
def ignore_order(order_id):
    """Sets a Failed order to 'Not Ordered' (Let it slide)"""
    order = Order.objects(id=order_id).first_or_404()
    
    if order.collaboration.user.id != current_user.id and current_user.role != 'operator':
        return jsonify({'status': 'error', 'msg': 'Unauthorized'}), 403

    if order.status == 'Failed':
        order.status = 'Not Ordered'
        order.api_response = f"Manually Ignored: {order.api_response}"
        order.save()
        return jsonify({'status': 'ok', 'msg': 'Order marked as ignored'})
    
    return jsonify({'status': 'error', 'msg': 'Order is not in Failed state'}), 400

@orders_bp.route('/execute_single', methods=['POST'])
@login_required
def execute_single():
    data = request.json
    order_id = data.get('order_id')
    if not order_id: return jsonify({'status': 'error'}), 400

    api_key = current_user.api_key
    if not api_key: return jsonify({'status': 'error', 'msg': 'Missing API Key'}), 400

    order = Order.objects(id=order_id).first()
    if not order or (order.collaboration.user.id != current_user.id and current_user.role != 'operator'):
        return jsonify({'status': 'error', 'msg': 'Unauthorized'}), 403
    
    payload = {
        'key': api_key,
        'action': 'add',
        'service': order.collaboration.service_id,
        'link': order.collaboration.link,
        'quantity': order.quantity
    }
    
    try:
        res = requests.post(API_URL, data=payload, timeout=15)
        json_res = res.json()
        
        if json_res.get('order'):
            order.status = 'Ordered'
            order.api_order_id = str(json_res.get('order'))
            order.executed_at = datetime.datetime.now()
            order.save()
            return jsonify({'status': 'ok', 'msg': 'Order Placed'})
        else:
            order.api_response = str(json_res)
            order.save()
            return jsonify({'status': 'error', 'msg': 'API Error: ' + str(json_res)}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'msg': str(e)}), 500

@orders_bp.route('/delete_collab/<collab_id>', methods=['POST'])
@login_required
def delete_collab(collab_id):
    collab = Collaboration.objects(id=collab_id).first_or_404()
    
    if collab.user.id != current_user.id and current_user.role != 'operator':
        return jsonify({'status': 'error'}), 403
    
    collab.is_deleted = True
    collab.save()
    return jsonify({'status': 'ok'})

@orders_bp.route('/graph_data/<collab_id>')
@login_required
def graph_data(collab_id):
    collab = Collaboration.objects(id=collab_id).first_or_404()
    
    if collab.user.id != current_user.id and current_user.role != 'operator':
        return jsonify({'status': 'error'}), 403

    orders = Order.objects(collaboration=collab)
    sorted_orders = sorted(orders, key=lambda x: x.scheduled_time)
    
    labels = [o.scheduled_time.strftime('%m-%d %H:%M') for o in sorted_orders]
    quantities = [o.quantity for o in sorted_orders]
    accumulated = []
    curr = 0
    for q in quantities:
        curr += q
        accumulated.append(curr)
        
    return jsonify({
        'status': 'ok',
        'labels': labels,
        'quantities': quantities,
        'accumulated': accumulated
    })