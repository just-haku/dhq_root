import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from app.models.order_center import OrderCenterOrder, OrderCenterSubOrder
from app.services.external_api import ExternalAPIService

logger = logging.getLogger(__name__)

class OrderCenterWorker:
    def __init__(self):
        self.running = False
        self._condition = asyncio.Condition()
        self._task = None

    async def start(self):
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._worker_loop())
        logger.info("Order Center Worker started")

    async def stop(self):
        self.running = False
        async with self._condition:
            self._condition.notify_all()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Order Center Worker stopped")

    async def notify_new_order(self):
        """Interrupt the worker's sleep to check for new, earlier sub-orders"""
        async with self._condition:
            self._condition.notify_all()
            logger.info("Order Center Worker notified of new order/change")

    async def _worker_loop(self):
        while self.running:
            try:
                # Find the earliest pending sub-order across all active orders
                next_sub, parent_order = await self._get_next_sub_order()

                if not next_sub:
                    # No pending sub-orders, wait for notification or just poll occasionally
                    async with self._condition:
                        try:
                            await asyncio.wait_for(self._condition.wait(), timeout=60)
                        except asyncio.TimeoutError:
                            pass
                    continue

                now = datetime.utcnow()
                delta = (next_sub.scheduled_time - now).total_seconds()

                if delta > 0:
                    # Sleep until scheduled time, but interruptible
                    async with self._condition:
                        try:
                            await asyncio.wait_for(self._condition.wait(), timeout=delta)
                            # If we got here via notify(), we loop back and peek again
                            continue
                        except asyncio.TimeoutError:
                            # Sleep finished naturally
                            pass

                # Execute the sub-order
                await self._execute_sub_order(next_sub, parent_order)

            except Exception as e:
                logger.error(f"Error in Order Center Worker loop: {e}", exc_info=True)
                await asyncio.sleep(5)

    async def _get_next_sub_order(self):
        """Find the earliest pending sub-order in an active order"""
        # We need to query for orders with status 'Active' and sub_orders with internal_status 'Pending'
        # Then find the one with the minimum scheduled_time
        
        # Optimization: We can't easily do a cross-document min(sub_order.scheduled_time) in MongoDB with reference fields easily
        # but we can query for active orders and then peek at their sub_orders.
        
        active_orders = OrderCenterOrder.objects(status='Active')
        
        earliest_sub = None
        target_order = None
        
        for order in active_orders:
            pending = [s for s in order.sub_orders if s.internal_status == 'Pending' and s.is_enabled]
            if not pending:
                continue
            
            # Find the earliest in this order
            order_earliest = min(pending, key=lambda x: x.scheduled_time)
            
            if earliest_sub is None or order_earliest.scheduled_time < earliest_sub.scheduled_time:
                earliest_sub = order_earliest
                target_order = order
                
        return earliest_sub, target_order

    async def _execute_sub_order(self, sub_order, order):
        """Execute the sub-order with exponential backoff for failures"""
        logger.info(f"Executing sub-order {sub_order.id} for order {order.name}")
        
        # Mark as Queued/Sent
        sub_order.internal_status = 'Sent'
        sub_order.executed_at = datetime.utcnow()
        order.save()
        
        max_retries = 3
        backoff_times = [60, 300, 900] # 1m, 5m, 15m
        
        # In a real system, we might want a separate task for retries to not block the main loop
        # But for this simple worker, we'll just handle it. 
        # Actually, let's make it non-blocking for the worker loop.
        asyncio.create_task(self._api_call_with_retry(sub_order, order, max_retries, backoff_times))

    async def _api_call_with_retry(self, sub_order, order, max_retries, backoff_times):
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                # Check if order is still active or paused
                # Re-fetch order to avoid stale data
                current_order = OrderCenterOrder.objects(id=order.id).first()
                if not current_order or current_order.status != 'Active':
                    logger.info(f"Order {order.id} is no longer active, stopping execution of sub-order {sub_order.id}")
                    return

                # Get user for API key
                user = current_order.user
                api_key = user.personal_api_key
                
                # If no personal api key, maybe use server default?
                # The spec says "Only OP can manage global Server Settings and External APIs"
                # But sub-orders send POS requests to assigned API.
                
                # For now, use the ExternalAPIService logic which handles user-configured servers
                from app.services.external_api import ExternalAPIService
                
                success, response = await ExternalAPIService.add_order(
                    api_key=api_key or "", # Fallback to empty if not set
                    service_id=current_order.api_service_id,
                    link=current_order.target_link,
                    quantity=sub_order.qty,
                    user_id=str(user.id),
                    api_server_id=str(current_order.api_server.id) if current_order.api_server else None
                )
                
                # Re-fetch order for sub_order update
                current_order = OrderCenterOrder.objects(id=order.id).first()
                actual_sub = next((s for s in current_order.sub_orders if s.id == sub_order.id), None)
                
                if success:
                    actual_sub.internal_status = 'Success'
                    actual_sub.api_order_ids = str(response.get("order", ""))
                    actual_sub.api_status = response.get("status", "Pending")
                    actual_sub.cost = float(response.get("charge", 0.0))
                    current_order.save()
                    logger.info(f"Sub-order {sub_order.id} succeeded")
                    return
                else:
                    logger.error(f"Sub-order {sub_order.id} failed: {response}")
                    actual_sub.api_status = str(response.get("error", "API Error"))
                    
                    if retry_count < max_retries:
                        retry_count += 1
                        actual_sub.retry_count = retry_count
                        current_order.save()
                        
                        wait_time = backoff_times[retry_count-1]
                        logger.info(f"Retrying sub-order {sub_order.id} in {wait_time}s (Attempt {retry_count})")
                        await asyncio.sleep(wait_time)
                    else:
                        actual_sub.internal_status = 'Tried but failed'
                        current_order.save()
                        return

            except Exception as e:
                logger.error(f"Exception during sub-order {sub_order.id} execution: {e}")
                if retry_count < max_retries:
                    retry_count += 1
                    await asyncio.sleep(backoff_times[retry_count-1])
                else:
                    break

# Global singleton
order_center_worker = OrderCenterWorker()
