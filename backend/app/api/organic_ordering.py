from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.models.user import User
from app.models.kpi import KPIHistory
from app.models.order import APIEndpoint, Order
from app.api.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime, timedelta
import httpx
import asyncio
import logging
import random

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class OrganicGrowthRequest(BaseModel):
    order_name: str
    service_name: str
    target_url: str
    service_type: str  # "views", "likes", "followers", etc.
    total_quantity: int
    duration_days: float
    growth_pattern: str = "organic"  # organic, viral, steady, burst
    start_delay_hours: float = 0
    peak_hours: list = []  # Hours of day for peak activity (0-23)
    min_per_hour: int = 0
    max_per_hour: int = 0

class OrganicOrderRequest(BaseModel):
    order_name: str
    target_url: str
    service_type: str
    total_quantity: int
    duration_days: float
    growth_pattern: str = "organic"
    api_key: str
    tolerance_pct: float = 0

@router.post("/organic/growth-plan")
async def create_growth_plan(
    request: OrganicGrowthRequest,
    current_user: User = Depends(get_current_user)
):
    """Create an organic growth simulation plan"""
    
    # Calculate KPI cost
    kpi_cost = max(20, request.total_quantity // 100)  # 1 KPI per 100 units, minimum 20
    
    if current_user.kpi_current < kpi_cost:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient KPI points. Need {kpi_cost} KPI to create growth plan."
        )
    
    # Generate hourly distribution based on growth pattern
    hourly_plan = generate_organic_distribution(
        total_quantity=request.total_quantity,
        duration_days=request.duration_days,
        growth_pattern=request.growth_pattern,
        peak_hours=request.peak_hours,
        min_per_hour=request.min_per_hour,
        max_per_hour=request.max_per_hour
    )
    
    # Create growth plan
    growth_plan = {
        "order_name": request.order_name,
        "service_name": request.service_name,
        "target_url": request.target_url,
        "service_type": request.service_type,
        "total_quantity": request.total_quantity,
        "duration_days": request.duration_days,
        "growth_pattern": request.growth_pattern,
        "start_delay_hours": request.start_delay_hours,
        "hourly_plan": hourly_plan,
        "created_at": datetime.utcnow(),
        "status": "planned",
        "user_id": str(current_user.id)
    }
    
    # Store in database (using Order model)
    order = Order(
        order_type="ORGANIC_GROWTH",
        service_name=growth_plan["order_name"],
        user=current_user,
        request_data=growth_plan,
        cost_kpi=0,  # No KPI cost for order creation
        status="PENDING"
    )
    order.save()
    
    return {
        "message": "Organic growth plan created successfully!",
        "plan_id": str(order.id),
        "order_name": growth_plan["order_name"],
        "total_quantity": request.total_quantity,
        "duration_days": request.duration_days,
        "growth_pattern": request.growth_pattern,
        "kpi_cost": 0,  # No KPI cost
        "hourly_distribution": len(hourly_plan),
        "estimated_start": (datetime.utcnow() + timedelta(hours=request.start_delay_hours)).isoformat()
    }

@router.post("/organic/execute")
async def execute_organic_order(
    request: OrganicOrderRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Execute an organic growth order"""
    
    # Generate hourly distribution
    hourly_plan = generate_organic_distribution(
        total_quantity=request.total_quantity,
        duration_days=request.duration_days,
        growth_pattern=request.growth_pattern,
        peak_hours=[9, 12, 15, 18, 21],  # Default peak hours
        min_per_hour=0,
        max_per_hour=request.total_quantity // 10  # Max 10% per hour
    )
    
    # Create order
    order_data = {
        "order_name": request.order_name,
        "target_url": request.target_url,
        "service_type": request.service_type,
        "total_quantity": request.total_quantity,
        "duration_days": request.duration_days,
        "growth_pattern": request.growth_pattern,
        "api_key": request.api_key,
        "tolerance_pct": request.tolerance_pct,
        "hourly_plan": hourly_plan,
        "created_at": datetime.utcnow(),
        "status": "active",
        "user_id": str(current_user.id)
    }
    
    order = Order(
        order_type="ORGANIC_ORDER",
        service_name=request.order_name,
        user=current_user,
        request_data=order_data,
        cost_kpi=0,  # No KPI cost for execution
        status="ACTIVE"
    )
    order.save()
    
    # Start background task for order execution
    background_tasks.add_task(execute_order_background, str(order.id))
    
    return {
        "message": "Order started successfully!",
        "order_id": str(order.id),
        "order_name": request.order_name,
        "total_quantity": request.total_quantity,
        "kpi_cost": 0,  # No KPI cost
        "estimated_completion": (datetime.utcnow() + timedelta(days=request.duration_days)).isoformat()
    }

@router.get("/organic/growth-plans")
async def get_growth_plans(
    current_user: User = Depends(get_current_user)
):
    """Get user's organic growth plans"""
    
    orders = Order.objects(
        user=current_user, 
        order_type="ORGANIC_GROWTH"
    ).order_by('-created_at')
    
    return {
        "growth_plans": [
            {
                "id": str(order.id),
                "order_name": order.service_name,
                "target_url": order.request_data.get("target_url", ""),
                "total_quantity": order.request_data.get("total_quantity", 0),
                "duration_days": order.request_data.get("duration_days", 0),
                "growth_pattern": order.request_data.get("growth_pattern", "linear"),
                "service_type": order.request_data.get("service_type", "views"),
                "peak_hours": order.request_data.get("peak_hours", []),
                "kpi_cost": order.cost_kpi,
                "status": order.status,
                "created_at": order.created_at,
                "updated_at": order.updated_at
            }
            for order in orders
        ],
        "total": orders.count()
    }

@router.get("/orders")
async def get_orders(
    status: str = None,
    current_user: User = Depends(get_current_user)
):
    """Get user's organic growth orders (legacy endpoint for frontend compatibility)"""
    
    query = Order.objects(user=current_user, order_type__in=["ORGANIC_GROWTH", "ORGANIC_ORDER"])
    
    if status:
        query = query.filter(status=status.upper())
    
    orders = query.order_by('-created_at')
    
    result = []
    for order in orders:
        hourly_plan = order.request_data.get("hourly_plan", [])
        completed_hours = sum(1 for hour in hourly_plan if hour.get("status") == "completed")
        total_hours = len(hourly_plan)
        
        result.append({
            "id": str(order.id),
            "order_name": order.service_name,
            "order_type": order.order_type,
            "status": order.status,
            "target_url": order.request_data.get("target_url"),
            "service_type": order.request_data.get("service_type"),
            "total_quantity": order.request_data.get("total_quantity"),
            "duration_days": order.request_data.get("duration_days"),
            "growth_pattern": order.request_data.get("growth_pattern"),
            "created_at": order.created_at.isoformat(),
            "total_hours": total_hours,
            "completed_hours": completed_hours,
            "progress_percentage": (completed_hours / total_hours * 100) if total_hours > 0 else 0,
            "next_delivery": next((hour["scheduled_at"] for hour in hourly_plan if hour.get("status") == "pending"), None)
        })
    
    return {
        "orders": result,
        "total": len(result)
    }

@router.get("/organic/orders")
async def get_organic_orders(
    status: str = None,
    current_user: User = Depends(get_current_user)
):
    """Get user's organic growth orders"""
    
    query = Order.objects(user=current_user, order_type__in=["ORGANIC_GROWTH", "ORGANIC_ORDER"])
    
    if status:
        query = query.filter(status=status.upper())
    
    orders = query.order_by('-created_at')
    
    result = []
    for order in orders:
        hourly_plan = order.request_data.get("hourly_plan", [])
        completed_hours = sum(1 for hour in hourly_plan if hour.get("status") == "completed")
        total_hours = len(hourly_plan)
        
        result.append({
            "id": str(order.id),
            "order_name": order.service_name,
            "order_type": order.order_type,
            "status": order.status,
            "target_url": order.request_data.get("target_url"),
            "service_type": order.request_data.get("service_type"),
            "total_quantity": order.request_data.get("total_quantity"),
            "duration_days": order.request_data.get("duration_days"),
            "growth_pattern": order.request_data.get("growth_pattern"),
            "created_at": order.created_at.isoformat(),
            "total_hours": total_hours,
            "completed_hours": completed_hours,
            "progress_percentage": (completed_hours / total_hours * 100) if total_hours > 0 else 0,
            "next_delivery": next((hour["scheduled_at"] for hour in hourly_plan if hour.get("status") == "pending"), None)
        })
    
    return {
        "orders": result,
        "total": len(result)
    }

@router.get("/organic/orders/{order_id}")
async def get_organic_order_details(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed organic order information"""
    
    order = Order.objects(id=order_id, user=current_user, order_type__in=["ORGANIC_GROWTH", "ORGANIC_ORDER"]).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    hourly_plan = order.request_data.get("hourly_plan", [])
    
    # Calculate statistics
    completed_hours = sum(1 for hour in hourly_plan if hour.get("status") == "completed")
    failed_hours = sum(1 for hour in hourly_plan if hour.get("status") == "failed")
    pending_hours = sum(1 for hour in hourly_plan if hour.get("status") == "pending")
    total_delivered = sum(hour.get("delivered_quantity", 0) for hour in hourly_plan)
    
    return {
        "order": {
            "id": str(order.id),
            "order_name": order.service_name,
            "order_type": order.order_type,
            "status": order.status,
            "request_data": order.request_data,
            "statistics": {
                "total_hours": len(hourly_plan),
                "completed_hours": completed_hours,
                "failed_hours": failed_hours,
                "pending_hours": pending_hours,
                "success_rate": (completed_hours / len(hourly_plan) * 100) if hourly_plan else 0,
                "total_delivered": total_delivered,
                "delivery_rate": (total_delivered / order.request_data.get("total_quantity", 1) * 100)
            },
            "hourly_plan": hourly_plan
        }
    }

# Background processing function
async def execute_organic_growth(order_id: str):
    """Execute organic growth order in background"""
    
    try:
        order = Order.objects(id=order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found")
            return
        
        hourly_plan = order.request_data.get("hourly_plan", [])
        current_time = datetime.utcnow()
        
        for hour_plan in hourly_plan:
            if hour_plan.get("status") not in ["pending"]:
                continue
            
            scheduled_time = hour_plan["scheduled_at"]
            if isinstance(scheduled_time, str):
                scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            
            # Wait until scheduled time
            if current_time < scheduled_time:
                sleep_seconds = (scheduled_time - current_time).total_seconds()
                if sleep_seconds > 0:
                    await asyncio.sleep(sleep_seconds)
            
            # Execute the hourly delivery
            await execute_hourly_delivery(order_id, hour_plan)
            
            # Update current time
            current_time = datetime.utcnow()
            
            # Small delay between API calls
            await asyncio.sleep(random.uniform(1, 3))
    
    except Exception as e:
        logger.error(f"Error executing organic growth {order_id}: {str(e)}")

async def execute_hourly_delivery(order_id: str, hour_plan: dict):
    """Execute a single hourly delivery"""
    
    try:
        order = Order.objects(id=order_id).first()
        if not order:
            return
        
        # Get API endpoint
        api_endpoint = APIEndpoint.objects(is_active=True).first()
        if not api_endpoint:
            logger.error("No active API endpoint found")
            return
        
        # Prepare API request
        quantity = hour_plan["quantity"]
        target_url = order.request_data.get("target_url")
        service_type = order.request_data.get("service_type")
        api_key = order.request_data.get("api_key")
        
        # Simulate API call (replace with actual API integration)
        success = random.random() > 0.1  # 90% success rate
        delivered_quantity = quantity if success else random.randint(0, quantity)
        
        # Update hour plan
        hour_plan["status"] = "completed" if success else "failed"
        hour_plan["delivered_quantity"] = delivered_quantity
        hour_plan["executed_at"] = datetime.utcnow().isoformat()
        hour_plan["response_data"] = {
            "success": success,
            "requested": quantity,
            "delivered": delivered_quantity,
            "api_response": "Simulated response"
        }
        
        # Save order
        order.save()
        
        logger.info(f"Hourly delivery completed: {delivered_quantity}/{quantity} for order {order_id}")
        
    except Exception as e:
        logger.error(f"Error executing hourly delivery: {str(e)}")
        hour_plan["status"] = "failed"
        hour_plan["error"] = str(e)

def generate_organic_distribution(
    total_quantity: int,
    duration_days: float,
    growth_pattern: str,
    peak_hours: list,
    min_per_hour: int,
    max_per_hour: int
) -> list:
    """Generate hourly distribution for organic growth"""
    
    total_hours = int(duration_days * 24)
    hourly_plan = []
    start_time = datetime.utcnow()
    
    if growth_pattern == "organic":
        # Natural growth with random variations
        base_quantity = total_quantity / total_hours
        
        for hour in range(total_hours):
            # Add organic variations
            variation = random.uniform(0.5, 1.5)
            peak_multiplier = 2.0 if (hour % 24) in peak_hours else 1.0
            
            quantity = int(base_quantity * variation * peak_multiplier)
            quantity = max(min_per_hour, min(quantity, max_per_hour))
            
            scheduled_time = start_time + timedelta(hours=hour)
            
            hourly_plan.append({
                "hour_index": hour,
                "scheduled_at": scheduled_time,
                "quantity": quantity,
                "status": "pending",
                "delivered_quantity": 0
            })
    
    elif growth_pattern == "viral":
        # Explosive growth at the beginning
        remaining_quantity = total_quantity
        for hour in range(total_hours):
            if hour < total_hours * 0.3:  # First 30% of time gets 70% of quantity
                percentage = 0.7 / (total_hours * 0.3)
            else:
                percentage = 0.3 / (total_hours * 0.7)
            
            quantity = int(remaining_quantity * percentage)
            quantity = max(min_per_hour, min(quantity, max_per_hour))
            
            scheduled_time = start_time + timedelta(hours=hour)
            
            hourly_plan.append({
                "hour_index": hour,
                "scheduled_at": scheduled_time,
                "quantity": quantity,
                "status": "pending",
                "delivered_quantity": 0
            })
            
            remaining_quantity -= quantity
    
    elif growth_pattern == "steady":
        # Consistent delivery
        quantity_per_hour = total_quantity // total_hours
        remainder = total_quantity % total_hours
        
        for hour in range(total_hours):
            quantity = quantity_per_hour + (1 if hour < remainder else 0)
            quantity = max(min_per_hour, min(quantity, max_per_hour))
            
            scheduled_time = start_time + timedelta(hours=hour)
            
            hourly_plan.append({
                "hour_index": hour,
                "scheduled_at": scheduled_time,
                "quantity": quantity,
                "status": "pending",
                "delivered_quantity": 0
            })
    
    elif growth_pattern == "burst":
        # Random bursts of activity
        base_quantity = total_quantity / total_hours
        
        for hour in range(total_hours):
            # Random burst pattern
            if random.random() < 0.2:  # 20% chance of burst
                burst_multiplier = random.uniform(2.0, 4.0)
            else:
                burst_multiplier = random.uniform(0.1, 0.8)
            
            quantity = int(base_quantity * burst_multiplier)
            quantity = max(min_per_hour, min(quantity, max_per_hour))
            
            scheduled_time = start_time + timedelta(hours=hour)
            
            hourly_plan.append({
                "hour_index": hour,
                "scheduled_at": scheduled_time,
                "quantity": quantity,
                "status": "pending",
                "delivered_quantity": 0
            })
    
    # Adjust to match total quantity exactly
    current_total = sum(hour["quantity"] for hour in hourly_plan)
    if current_total != total_quantity:
        difference = total_quantity - current_total
        if difference > 0:
            # Distribute remaining quantity
            for i in range(min(difference, len(hourly_plan))):
                hourly_plan[i]["quantity"] += 1
        else:
            # Reduce excess quantity
            for i in range(min(-difference, len(hourly_plan))):
                if hourly_plan[i]["quantity"] > min_per_hour:
                    hourly_plan[i]["quantity"] -= 1
    
    return hourly_plan

@router.post("/orders/{order_id}/execute-now")
async def execute_order_now(
    order_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Execute order immediately (NOW!!! functionality)"""
    try:
        order = Order.objects(id=order_id, user=current_user).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update order status to immediate execution
        order.status = "EXECUTING_NOW"
        order.request_data["order_now"] = True
        order.request_data["execution_started"] = datetime.utcnow().isoformat()
        order.save()
        
        # Start immediate background execution
        background_tasks.add_task(execute_order_immediately, str(order.id))
        
        return {
            "message": "Order execution started immediately!",
            "order_id": str(order.id),
            "execution_type": "immediate",
            "started_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing order now: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute order immediately")

async def execute_order_immediately(order_id: str):
    """Execute order immediately with V4 logic"""
    try:
        order = Order.objects(id=order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found for immediate execution")
            return
        
        # V4-style immediate execution logic
        request_data = order.request_data
        api_url = "https://api.example.com/v1"  # Replace with actual API
        api_key = request_data.get("api_key", "")
        
        if not api_key:
            logger.error(f"No API key for order {order_id}")
            order.status = "FAILED"
            order.save()
            return
        
        # Prepare payload (V4 style)
        payload = {
            "key": api_key,
            "action": "add",
            "service": request_data.get("service_type", "views"),
            "link": request_data.get("target_url", ""),
            "quantity": request_data.get("total_quantity", 0)
        }
        
        logger.info(f"[{order_id}] Executing order NOW: {payload}")
        
        # Send to API with 30-second delay (V4 style)
        await asyncio.sleep(30)
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(api_url, data=payload)
                
                if response.status_code == 200:
                    rjson = response.json()
                    
                    if rjson.get("error") == "Duplicate order":
                        order.status = "DUPLICATE"
                        order.request_data["api_response"] = rjson
                        logger.warning(f"[{order_id}] Duplicate order: {rjson}")
                    elif (str(rjson.get("status", "")).lower() in ["complete", "success"] or 
                          (rjson.get("order") and str(rjson.get("order")).strip())):
                        order.status = "COMPLETED"
                        order.request_data["order_now"] = True
                        order.request_data["done"] = True
                        order.request_data["order_id"] = rjson.get("order") or rjson.get("order_id")
                        order.request_data["api_response"] = rjson
                        logger.info(f"[{order_id}] Order completed: {rjson.get('order')}")
                    else:
                        order.status = "FAILED"
                        order.request_data["api_response"] = rjson
                        logger.warning(f"[{order_id}] Order failed: {rjson}")
                else:
                    order.status = "FAILED"
                    order.request_data["api_response"] = f"HTTP {response.status_code}: {response.text}"
                    logger.warning(f"[{order_id}] HTTP error {response.status_code}")
                    
        except Exception as e:
            order.status = "FAILED"
            order.request_data["api_response"] = str(e)
            logger.error(f"[{order_id}] Exception: {e}")
        
        order.save()
        
    except Exception as e:
        logger.error(f"Error in immediate execution for {order_id}: {e}")
        # Update order status to failed
        try:
            order = Order.objects(id=order_id).first()
            if order:
                order.status = "FAILED"
                order.save()
        except:
            pass

@router.delete("/orders/{order_id}/delete")
async def delete_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an organic order"""
    try:
        order = Order.objects(id=order_id, user=current_user).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order.delete()
        return {"message": "Order deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting order: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete order")
