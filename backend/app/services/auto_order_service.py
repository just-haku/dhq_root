import asyncio
import logging
from datetime import datetime, timedelta
from app.core.database import redis_client
from app.models.growth_order import GrowthOrder, SubOrder
from app.models.user import User
from app.api.auth import get_op_user
from fastapi import HTTPException, Depends

logger = logging.getLogger(__name__)

class AutoOrderService:
    def __init__(self):
        self.running = False
        self.task = None
        self.log_file = "logs/history.log"
        self._ensure_log_directory()
        
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        import os
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
    def _write_history_log(self, message: str, level: str = "INFO"):
        """Write to history log file"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        log_entry = f"[{timestamp}] [{level}] AUTO_ORDER: {message}\n"
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            logger.error(f"Failed to write to history log: {e}")
            
    def _log_sub_order_action(self, sub_order, action: str, details: str = ""):
        """Log specific sub-order actions"""
        order_info = f"SubOrder {sub_order.id} (Order: {getattr(sub_order, 'parent_order_id', 'unknown')}) - {action}"
        if details:
            order_info += f" - {details}"
        self._write_history_log(order_info)
        
    async def start(self):
        """Start the auto-order service"""
        if self.running:
            self._write_history_log("Auto-order service already running, ignoring start request", "WARNING")
            return
            
        self.running = True
        self.task = asyncio.create_task(self._auto_order_loop())
        logger.info("Auto-order service started")
        self._write_history_log("Auto-order service started successfully")
        
    async def stop(self):
        """Stop the auto-order service"""
        if not self.running:
            self._write_history_log("Auto-order service not running, ignoring stop request", "WARNING")
            return
            
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Auto-order service stopped")
        self._write_history_log("Auto-order service stopped")
        
    async def _auto_order_loop(self):
        """Main loop for auto-order processing"""
        self._write_history_log("Auto-order processing loop started")
        
        while self.running:
            try:
                await self._process_pending_orders()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                self._write_history_log("Auto-order processing loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in auto-order loop: {e}")
                self._write_history_log(f"Error in auto-order loop: {e}", "ERROR")
                await asyncio.sleep(30)
                
        self._write_history_log("Auto-order processing loop ended")
                
    async def _process_pending_orders(self):
        """Process all pending sub-orders whose time has passed"""
        try:
            self._write_history_log("=== Auto-order processing cycle started ===")
            
            # Check if auto-order is enabled
            auto_order_enabled = await redis_client.hget("admin:timezone_config", "auto_order_enabled")
            logger.info(f"Auto-order enabled check: {auto_order_enabled}")
            
            # Handle both bytes and string responses from Redis
            auto_order_enabled_str = auto_order_enabled.decode('utf-8') if isinstance(auto_order_enabled, bytes) else auto_order_enabled
            if not auto_order_enabled_str or auto_order_enabled_str != "True":
                logger.info("Auto-order is disabled, skipping processing")
                self._write_history_log("Auto-order is disabled, skipping processing")
                return
                
            # Get current time with timezone offset
            current_time = await self._get_current_time_with_timezone()
            logger.info(f"Current time with timezone: {current_time}")
            self._write_history_log(f"Current time with timezone: {current_time}")
            
            # Find all active growth orders
            active_orders = GrowthOrder.objects(status="Active")
            logger.info(f"Found {len(active_orders)} active orders")
            self._write_history_log(f"Found {len(active_orders)} active orders")
            
            if len(active_orders) == 0:
                logger.info("No active growth orders found")
                self._write_history_log("No active growth orders found")
                return
            
            processed_count = 0
            for order in active_orders:
                try:
                    self._write_history_log(f"Processing order {order.id} ({order.name}) with {len(order.sub_orders)} sub-orders")
                    logger.info(f"Processing order {order.id} with {len(order.sub_orders)} sub-orders")
                    
                    # Count pending sub-orders
                    pending_sub_orders = [sub for sub in order.sub_orders if sub.status == "Pending"]
                    logger.info(f"Order {order.id} has {len(pending_sub_orders)} pending sub-orders")
                    self._write_history_log(f"Order {order.id} has {len(pending_sub_orders)} pending sub-orders")
                    
                    # Show upcoming sub-orders for debugging
                    upcoming_sub_orders = [
                        sub for sub in order.sub_orders 
                        if sub.status == "Pending" and sub.scheduled_time <= current_time
                    ]
                    logger.info(f"Order {order.id} has {len(upcoming_sub_orders)} sub-orders whose time has passed")
                    self._write_history_log(f"Order {order.id} has {len(upcoming_sub_orders)} sub-orders whose time has passed")
                    
                    # Show next few scheduled times
                    next_scheduled = sorted([sub for sub in order.sub_orders if sub.status == "Pending"], key=lambda x: x.scheduled_time)[:3]
                    for i, sub in enumerate(next_scheduled):
                        time_diff = sub.scheduled_time - current_time
                        logger.info(f"  Sub-order {i+1}: {sub.id} at {sub.scheduled_time} (diff: {time_diff})")
                        self._write_history_log(f"  Sub-order {i+1}: {sub.id} scheduled at {sub.scheduled_time} (diff: {time_diff})")
                    
                    if len(pending_sub_orders) == 0:
                        logger.info(f"Order {order.id} has no pending sub-orders")
                        self._write_history_log(f"Order {order.id} has no pending sub-orders")
                        continue
                    
                    # Check if this order uses sequential placement
                    if order.sequential_placement:
                        logger.info(f"Order {order.id} uses sequential placement")
                        self._write_history_log(f"Order {order.id} uses sequential placement")
                        # For sequential placement, only process next pending sub-order
                        # if the previous one is completed
                        processed = await self._process_sequential_order(order, current_time)
                    else:
                        logger.info(f"Order {order.id} uses time-based placement")
                        self._write_history_log(f"Order {order.id} uses time-based placement")
                        # For time-based placement, process all pending sub-orders whose time has passed
                        processed = await self._process_time_based_order(order, current_time)
                    
                    processed_count += processed
                    logger.info(f"Order {order.id} processed {processed} sub-orders")
                    self._write_history_log(f"Order {order.id} processed {processed} sub-orders")
                    
                except Exception as e:
                    logger.error(f"Failed to process order {order.id}: {e}")
                    self._write_history_log(f"Failed to process order {order.id}: {e}", "ERROR")
                    
            if processed_count > 0:
                await redis_client.hset("admin:timezone_config", "last_check", datetime.utcnow().isoformat())
                logger.info(f"Auto-order service processed {processed_count} sub-orders")
                self._write_history_log(f"Auto-order service processed {processed_count} sub-orders in this cycle")
            else:
                logger.info("No sub-orders were processed in this cycle")
                self._write_history_log("No sub-orders were processed in this cycle")
                
            self._write_history_log("=== Auto-order processing cycle completed ===")
                
        except Exception as e:
            logger.error(f"Error processing pending orders: {e}")
            self._write_history_log(f"Error processing pending orders: {e}", "ERROR")
            
    async def _process_sequential_order(self, order, current_time):
        """Process sub-orders sequentially (only after previous one is completed)"""
        processed_count = 0
        
        # Sort sub-orders by scheduled time
        sorted_sub_orders = sorted(order.sub_orders, key=lambda x: x.scheduled_time)
        
        # Find first pending sub-order
        next_pending_index = None
        for i, sub_order in enumerate(sorted_sub_orders):
            if sub_order.status == "Pending":
                next_pending_index = i
                break
        
        if next_pending_index is None:
            self._write_history_log(f"Order {order.id}: No pending sub-orders found for sequential processing")
            return 0  # No pending sub-orders
        
        next_sub_order = sorted_sub_orders[next_pending_index]
        
        # Check if this is the first sub-order or if the previous one is completed
        if next_pending_index == 0:
            # First sub-order - check if scheduled time has passed
            if next_sub_order.scheduled_time <= current_time:
                success = await self._place_sub_order(next_sub_order)
                if success:
                    processed_count += 1
                    logger.info(f"First sub-order {next_sub_order.id} placed successfully")
                    self._log_sub_order_action(next_sub_order, "PLACED", "First sub-order in sequence")
                else:
                    self._log_sub_order_action(next_sub_order, "FAILED_TO_PLACE", "First sub-order in sequence")
            else:
                self._log_sub_order_action(next_sub_order, "WAITING", f"Scheduled time {next_sub_order.scheduled_time} not yet reached")
        else:
            # Not the first sub-order - check if the previous one is completed
            previous_sub_order = sorted_sub_orders[next_pending_index - 1]
            if (previous_sub_order.status == "Completed" and 
                next_sub_order.scheduled_time <= current_time):
                success = await self._place_sub_order(next_sub_order)
                if success:
                    processed_count += 1
                    logger.info(f"Sub-order {next_sub_order.id} placed after previous completion")
                    self._log_sub_order_action(next_sub_order, "PLACED", f"Previous sub-order {previous_sub_order.id} completed")
                else:
                    self._log_sub_order_action(next_sub_order, "FAILED_TO_PLACE", f"Previous sub-order {previous_sub_order.id} completed")
            elif previous_sub_order.status != "Completed":
                logger.info(f"Previous sub-order {previous_sub_order.id} status is {previous_sub_order.status}, waiting for completion")
                self._log_sub_order_action(next_sub_order, "WAITING", f"Previous sub-order {previous_sub_order.id} status is {previous_sub_order.status}")
            else:
                self._log_sub_order_action(next_sub_order, "WAITING", f"Scheduled time {next_sub_order.scheduled_time} not yet reached")
        
        return processed_count
    
    async def _process_time_based_order(self, order, current_time):
        """Process sub-orders based on time (regardless of previous sub-order status)"""
        processed_count = 0
        
        # Find all pending sub-orders whose scheduled time has passed
        pending_sub_orders = [
            sub for sub in order.sub_orders 
            if sub.status == "Pending" and sub.scheduled_time <= current_time
        ]
        
        logger.info(f"Time-based: Found {len(pending_sub_orders)} pending sub-orders whose time has passed")
        self._write_history_log(f"Order {order.id}: Found {len(pending_sub_orders)} time-based sub-orders to process")
        
        for sub_order in pending_sub_orders:
            logger.info(f"Time-based: Processing sub-order {sub_order.id} scheduled at {sub_order.scheduled_time}")
            self._log_sub_order_action(sub_order, "PROCESSING", f"Time-based placement, scheduled at {sub_order.scheduled_time}")
            try:
                success = await self._place_sub_order(sub_order)
                if success:
                    processed_count += 1
                    logger.info(f"Time-based: Sub-order {sub_order.id} placed successfully")
                    self._log_sub_order_action(sub_order, "PLACED", "Time-based placement successful")
                else:
                    logger.warning(f"Time-based: Failed to place sub-order {sub_order.id}")
                    self._log_sub_order_action(sub_order, "FAILED_TO_PLACE", "Time-based placement failed")
            except Exception as e:
                logger.error(f"Time-based: Error placing sub-order {sub_order.id}: {e}")
                self._log_sub_order_action(sub_order, "ERROR", f"Time-based placement error: {e}")
        
        return processed_count
            
    async def _get_current_time_with_timezone(self):
        """Get current time with configured timezone offset"""
        try:
            # Get timezone from Redis
            timezone = await redis_client.hget("admin:timezone_config", "timezone")
            # Handle both bytes and string responses from Redis
            timezone_str = timezone.decode('utf-8') if isinstance(timezone, bytes) else timezone
            if not timezone_str:
                timezone_str = "GMT+7"
                
            # Calculate timezone offset
            if timezone_str == "GMT+7":
                offset_hours = 7
            elif timezone_str == "GMT+8":
                offset_hours = 8
            elif timezone_str == "GMT+9":
                offset_hours = 9
            else:
                offset_hours = 7  # Default to GMT+7
                
            # Apply timezone offset to current time
            current_time = datetime.utcnow() + timedelta(hours=offset_hours)
            return current_time
            
        except Exception as e:
            logger.error(f"Error getting timezone time: {e}")
            return datetime.utcnow()
            
    async def _place_sub_order(self, sub_order):
        """Place a sub-order via ExternalAPIService"""
        try:
            from app.models.growth_order import GrowthOrder
            from app.core.security import decrypt_data
            from app.services.external_api import ExternalAPIService
            
            parent_order = GrowthOrder.objects(sub_orders__id=sub_order.id).first()
            if not parent_order:
                logger.error(f"Could not find parent order for sub-order {sub_order.id}")
                self._log_sub_order_action(sub_order, "ERROR", "Could not find parent order")
                return False
                
            old_status = sub_order.status
            sub_order.status = "Running"
            sub_order.executed_at = datetime.utcnow()
            parent_order.save()
            
            # Execute via external API
            try:
                api_key = decrypt_data(parent_order.api_key_encrypted).decode('utf-8')
            except Exception as e:
                logger.error(f"Failed to decrypt API key: {e}")
                sub_order.status = "Failed_Fatal"
                sub_order.error_log = "Failed to decrypt API key"
                parent_order.total_failed += 1
                parent_order.save()
                return False
                
            success, response = await ExternalAPIService.add_order(
                api_key=api_key,
                service_id=parent_order.service_id,
                link=parent_order.target_link,
                quantity=sub_order.quantity,
                user_id=str(parent_order.user_id)
            )
            
            if success:
                sub_order.external_order_id = str(response.get("order", response.get("order_id", "")))
                sub_order.status = "Completed"
                parent_order.total_executed += 1
                logger.info(f"Sub-order {sub_order.id} completed successfully")
                self._log_sub_order_action(sub_order, "COMPLETED", f"Response: {response}")
            else:
                sub_order.status = "Failed_Fatal" if ExternalAPIService.is_fatal_error(response) else "Retry_Pending"
                sub_order.error_log = str(response)
                sub_order.retry_count += 1
                parent_order.total_failed += 1
                
                # If network error, pause the main order
                if ExternalAPIService.is_network_error(response):
                    parent_order.status = "Paused_Error"
                    parent_order.last_error_time = datetime.utcnow()
                
                self._log_sub_order_action(sub_order, "FAILED", f"Response: {response}")
                
            parent_order.save()
            return success
            
        except Exception as e:
            logger.error(f"Error placing sub-order {sub_order.id}: {e}")
            self._log_sub_order_action(sub_order, "ERROR", f"Placement failed: {e}")
            return False
            
    async def get_status(self):
        """Get current status of auto-order service"""
        try:
            auto_order_enabled = await redis_client.hget("admin:timezone_config", "auto_order_enabled")
            last_check = await redis_client.hget("admin:timezone_config", "last_check")
            
            return {
                "running": self.running,
                "auto_order_enabled": auto_order_enabled == "True",
                "last_check": last_check
            }
        except Exception as e:
            logger.error(f"Error getting auto-order status: {e}")
            return {
                "running": False,
                "auto_order_enabled": False,
                "last_check": None
            }

# Global instance
auto_order_service = AutoOrderService()

async def initialize_auto_order_service():
    """Initialize and start the auto-order service"""
    # Set default auto-order enabled to True
    await redis_client.hset("admin:timezone_config", "auto_order_enabled", "True")
    await redis_client.hset("admin:timezone_config", "timezone", "GMT+7")
    
    # Start the service
    await auto_order_service.start()
    logger.info("Auto-order service initialized with default settings")
