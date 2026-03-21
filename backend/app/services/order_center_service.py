import logging
from datetime import datetime, timedelta
from app.models.order_center import OrderCenterOrder, OrderCenterSubOrder
from app.services.order_center_worker import order_center_worker
from app.services.curve_generator import CurveGenerator

logger = logging.getLogger(__name__)

class OrderCenterService:
    @staticmethod
    async def create_order(user, order_data):
        """Create a new order and generate sub-orders"""
        order = OrderCenterOrder(
            user=user,
            name=order_data['name'],
            unit_label=order_data.get('unit_label', 'Units'),
            target_link=order_data['target_link'],
            total_qty=order_data['total_qty'],
            total_time=order_data['total_time'],
            time_unit=order_data['time_unit'],
            step_mins=order_data['step_mins'],
            tolerance_pct=order_data['tolerance_pct'],
            graph_type=order_data['graph_type'],
            api_service_id=order_data['api_service_id'],
            api_server=order_data.get('api_server_id'),
            est_cost=order_data.get('est_cost', 0.0)
        )
        
        # Calculate total duration in minutes
        time_mult = {"Minutes": 1, "Hours": 60, "Days": 1440}
        total_mins = order.total_time * time_mult.get(order.time_unit, 1)
        
        # Generate distribution
        distribution = CurveGenerator.generate_sub_orders(
            total_qty=order.total_qty,
            total_time_mins=total_mins,
            step_mins=order.step_mins,
            graph_type=order.graph_type,
            tolerance_pct=order.tolerance_pct
        )
        
        # Map to SubOrder models
        start_time = datetime.utcnow()
        for item in distribution:
            sub = OrderCenterSubOrder(
                ordinal_number=item['ordinal'],
                qty=item['qty'],
                scheduled_time=start_time + timedelta(minutes=item['mins_offset']),
                internal_status='Pending'
            )
            order.sub_orders.append(sub)
            
        order.save()
        
        # Notify worker to recalculate its sleep
        await order_center_worker.notify_new_order()
        return order

    @staticmethod
    async def pause_order(order_id):
        order = OrderCenterOrder.objects(id=order_id).first()
        if not order or order.status != 'Active':
            return False
            
        order.status = 'Paused'
        order.paused_at = datetime.utcnow()
        order.save()
        
        # Notify worker (it will ignore this order now)
        await order_center_worker.notify_new_order()
        return True

    @staticmethod
    async def resume_order(order_id):
        order = OrderCenterOrder.objects(id=order_id).first()
        if not order or order.status != 'Paused':
            return False
            
        now = datetime.utcnow()
        if order.paused_at:
            shift_delta = now - order.paused_at
            
            # Time-Shift: Update all pending sub-orders
            for sub in order.sub_orders:
                if sub.internal_status == 'Pending':
                    sub.scheduled_time += shift_delta
                    
        order.status = 'Active'
        order.paused_at = None
        order.save()
        
        # Notify worker to recalculate
        await order_center_worker.notify_new_order()
        return True

    @staticmethod
    async def force_sub_order(order_id, sub_order_id):
        """Force execution of a specific sub-order NOW!!!"""
        order = OrderCenterOrder.objects(id=order_id).first()
        if not order:
            return False
            
        sub = next((s for s in order.sub_orders if s.id == sub_order_id), None)
        if not sub or sub.internal_status != 'Pending':
            return False
            
        # Update scheduled time to now to let worker pick it up or just execute here
        # Spec says: "bypassing the schedule and fire the API request immediately, marking it as Sent."
        
        # We'll execute it via a background task to not block the request
        sub.internal_status = 'Sent'
        sub.executed_at = datetime.utcnow()
        order.save()
        
        from app.services.order_center_worker import order_center_worker
        asyncio.create_task(order_center_worker._api_call_with_retry(sub, order, 3, [60, 300, 900]))
        
        return True
