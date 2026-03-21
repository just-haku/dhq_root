from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.models.order import APIEndpoint, Order
from app.models.user import User
from app.models.kpi import KPIHistory
from app.api.auth import get_current_user, get_op_user
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import httpx
import json
import asyncio
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for enhanced ordering
class TimelineStep(BaseModel):
    time_offset_hours: float
    amount: int
    tolerance_pct: float = 0
    enabled: bool = True

class CreateCollaborationRequest(BaseModel):
    name: str
    service_id: str
    service_name: str
    link: str
    total_days: float
    step_hours: float
    tolerance_pct: float
    final_a: int
    timeline: List[TimelineStep]

class GrowthCurveRequest(BaseModel):
    initial_quantity: int
    final_quantity: int
    total_days: float
    growth_type: str = "exponential"  # linear, exponential, logarithmic, crooked
    tolerance_pct: float = 0

class OrderStatusUpdate(BaseModel):
    order_id: str
    status: str
    response_data: Optional[Dict[str, Any]] = None

# Enhanced ordering endpoints
@router.post("/collaborations")
async def create_collaboration(
    request: CreateCollaborationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Create a new collaboration with timeline-based ordering"""
    
    # Calculate KPI cost for creating collaboration
    kpi_cost = max(10, len(request.timeline) * 2)  # 2 KPI per timeline step, minimum 10
    
    if current_user.kpi_current < kpi_cost:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient KPI points. Need {kpi_cost} KPI to create collaboration."
        )
    
    # Deduct KPI cost
    current_user.kpi_current -= kpi_cost
    current_user.save()
    
    # Create KPI history entry
    KPIHistory(
        user=current_user,
        amount=-kpi_cost,
        balance_after=current_user.kpi_current,
        source="collaboration_creation",
        reason=f"Created collaboration: {request.name}"
    ).save()
    
    # Create collaboration document (similar to V4 structure)
    collaboration_data = {
        "name": request.name,
        "user_id": str(current_user.id),
        "service_id": request.service_id,
        "service_name": request.service_name,
        "link": request.link,
        "total_days": request.total_days,
        "step_hours": request.step_hours,
        "tolerance_pct": request.tolerance_pct,
        "total_quantity": request.final_a,
        "created_at": datetime.utcnow(),
        "status": "active",
        "timeline": []
    }
    
    # Process timeline steps
    start_time = datetime.utcnow()
    for i, step in enumerate(request.timeline):
        if not step.enabled:
            continue
            
        scheduled_at = start_time + timedelta(hours=step.time_offset_hours)
        
        timeline_step = {
            "step_index": i,
            "time_offset_hours": step.time_offset_hours,
            "scheduled_at": scheduled_at,
            "quantity": step.amount,
            "tolerance_pct": step.tolerance_pct,
            "status": "pending",
            "order_id": None,
            "attempts": 0,
            "last_attempt": None,
            "response_data": None
        }
        
        collaboration_data["timeline"].append(timeline_step)
    
    # Store collaboration in database (using Order model for now)
    # In a full implementation, you'd create a separate Collaboration model
    collaboration_order = Order(
        order_type="COLLABORATION",
        service_name=request.name,
        user=current_user,
        request_data=collaboration_data,
        cost_kpi=kpi_cost,
        status="ACTIVE"
    )
    collaboration_order.save()
    
    # Schedule background task for order processing
    background_tasks.add_task(process_collaboration_timeline, str(collaboration_order.id))
    
    return {
        "message": "Collaboration created successfully!",
        "collaboration_id": str(collaboration_order.id),
        "name": request.name,
        "timeline_steps": len(collaboration_data["timeline"]),
        "kpi_cost": kpi_cost,
        "first_order_at": collaboration_data["timeline"][0]["scheduled_at"].isoformat() if collaboration_data["timeline"] else None
    }

@router.post("/growth-curve")
async def calculate_growth_curve(request: GrowthCurveRequest):
    """Calculate growth curve based on V4 algorithms"""
    
    try:
        if request.growth_type == "linear":
            curve_data = calculate_linear_growth(
                request.initial_quantity, 
                request.final_quantity, 
                request.total_days
            )
        elif request.growth_type == "exponential":
            curve_data = calculate_exponential_growth(
                request.initial_quantity, 
                request.final_quantity, 
                request.total_days
            )
        elif request.growth_type == "logarithmic":
            curve_data = calculate_logarithmic_growth(
                request.initial_quantity, 
                request.final_quantity, 
                request.total_days
            )
        elif request.growth_type == "crooked":
            curve_data = calculate_crooked_growth(
                request.initial_quantity, 
                request.final_quantity, 
                request.total_days
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid growth type")
        
        return {
            "growth_type": request.growth_type,
            "curve_data": curve_data,
            "initial_quantity": request.initial_quantity,
            "final_quantity": request.final_quantity,
            "total_days": request.total_days,
            "tolerance_pct": request.tolerance_pct
        }
        
    except Exception as e:
        logger.error(f"Error calculating growth curve: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate growth curve")

@router.get("/collaborations")
async def get_collaborations(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get user's collaborations"""
    
    query = Order.objects(user=current_user, order_type="COLLABORATION")
    
    if status:
        query = query.filter(status=status)
    
    collaborations = query.order_by('-created_at')
    
    result = []
    for collab in collaborations:
        timeline = collab.request_data.get("timeline", [])
        completed_steps = sum(1 for step in timeline if step.get("status") == "completed")
        total_steps = len(timeline)
        
        result.append({
            "id": str(collab.id),
            "name": collab.service_name,
            "status": collab.status,
            "created_at": collab.created_at.isoformat(),
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "progress_percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            "next_order_at": next((step["scheduled_at"] for step in timeline if step.get("status") == "pending"), None)
        })
    
    return {
        "collaborations": result,
        "total": len(result)
    }

@router.get("/collaborations/{collaboration_id}")
async def get_collaboration_details(
    collaboration_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed collaboration information"""
    
    collaboration = Order.objects(id=collaboration_id, user=current_user, order_type="COLLABORATION").first()
    if not collaboration:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    
    timeline = collaboration.request_data.get("timeline", [])
    
    # Calculate statistics
    completed_steps = sum(1 for step in timeline if step.get("status") == "completed")
    failed_steps = sum(1 for step in timeline if step.get("status") == "failed")
    pending_steps = sum(1 for step in timeline if step.get("status") == "pending")
    
    return {
        "collaboration": {
            "id": str(collaboration.id),
            "name": collaboration.service_name,
            "status": collaboration.status,
            "created_at": collaboration.created_at.isoformat(),
            "request_data": collaboration.request_data,
            "statistics": {
                "total_steps": len(timeline),
                "completed_steps": completed_steps,
                "failed_steps": failed_steps,
                "pending_steps": pending_steps,
                "success_rate": (completed_steps / len(timeline) * 100) if timeline else 0
            },
            "timeline": timeline
        }
    }

@router.post("/collaborations/{collaboration_id}/update-status")
async def update_order_status(
    collaboration_id: str,
    step_index: int,
    update: OrderStatusUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update status for a specific order in collaboration"""
    
    collaboration = Order.objects(id=collaboration_id, user=current_user, order_type="COLLABORATION").first()
    if not collaboration:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    
    timeline = collaboration.request_data.get("timeline", [])
    if step_index >= len(timeline):
        raise HTTPException(status_code=400, detail="Invalid step index")
    
    step = timeline[step_index]
    step["status"] = update.status
    step["response_data"] = update.response_data
    step["last_attempt"] = datetime.utcnow().isoformat()
    
    collaboration.save()
    
    return {
        "message": "Order status updated successfully",
        "collaboration_id": collaboration_id,
        "step_index": step_index,
        "new_status": update.status
    }

# Background processing functions
async def process_collaboration_timeline(collaboration_id: str):
    """Background task to process collaboration timeline (similar to V4 logic)"""
    
    try:
        collaboration = Order.objects(id=collaboration_id).first()
        if not collaboration:
            logger.error(f"Collaboration {collaboration_id} not found")
            return
        
        timeline = collaboration.request_data.get("timeline", [])
        current_time = datetime.utcnow()
        
        for step in timeline:
            if step.get("status") not in ["pending"]:
                continue
            
            scheduled_time = step["scheduled_at"]
            if isinstance(scheduled_time, str):
                scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            
            # Check if it's time to execute this step
            if current_time >= scheduled_time:
                await execute_timeline_step(collaboration_id, step)
                
                # Small delay between orders to avoid overwhelming the API
                await asyncio.sleep(1)
    
    except Exception as e:
        logger.error(f"Error processing collaboration timeline {collaboration_id}: {str(e)}")

async def execute_timeline_step(collaboration_id: str, step: Dict[str, Any]):
    """Execute a single timeline step (similar to V4 order execution)"""
    
    try:
        # Get API endpoint for this service
        # This would be configured based on the service_id
        api_endpoint = APIEndpoint.objects(is_active=True).first()
        if not api_endpoint:
            logger.error("No active API endpoint found")
            return
        
        # Prepare order payload
        order_payload = {
            "key": api_endpoint.api_key,
            "action": "order",
            "service": step.get("service_id", "default"),
            "quantity": step["quantity"],
            "link": step.get("link", ""),
            "tolerance": step.get("tolerance_pct", 0)
        }
        
        # Execute API call
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_endpoint.endpoint_url,
                data=order_payload,
                timeout=30
            )
            
            # Update step with response
            step["attempts"] += 1
            step["last_attempt"] = datetime.utcnow().isoformat()
            step["response_data"] = {
                "status_code": response.status_code,
                "body": response.text[:1000]  # Limit response size
            }
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    step["status"] = "completed"
                    step["order_id"] = response_data.get("order_id")
                    logger.info(f"Order completed successfully: {response_data.get('order_id')}")
                except:
                    step["status"] = "completed"
                    logger.info("Order completed but response parsing failed")
            else:
                step["status"] = "failed"
                logger.error(f"Order failed with status {response.status_code}")
        
        # Update collaboration in database
        collaboration = Order.objects(id=collaboration_id).first()
        if collaboration:
            collaboration.save()
            
    except Exception as e:
        logger.error(f"Error executing timeline step: {str(e)}")
        step["status"] = "failed"
        step["response_data"] = {"error": str(e)}

# Growth calculation algorithms (from V4)
def calculate_linear_growth(initial: int, final: int, days: float) -> List[Dict]:
    """Calculate linear growth curve"""
    points = []
    steps = int(days * 24)  # Hourly steps
    
    for i in range(steps + 1):
        progress = i / steps
        value = initial + (final - initial) * progress
        points.append({
            "hour": i,
            "value": int(value),
            "progress": progress
        })
    
    return points

def calculate_exponential_growth(initial: int, final: int, days: float) -> List[Dict]:
    """Calculate exponential growth curve"""
    points = []
    steps = int(days * 24)
    
    # Calculate growth rate
    if initial > 0:
        growth_rate = (final / initial) ** (1 / steps) - 1
    else:
        growth_rate = 1
    
    for i in range(steps + 1):
        value = initial * ((1 + growth_rate) ** i)
        points.append({
            "hour": i,
            "value": int(value),
            "progress": i / steps
        })
    
    return points

def calculate_logarithmic_growth(initial: int, final: int, days: float) -> List[Dict]:
    """Calculate logarithmic growth curve"""
    points = []
    steps = int(days * 24)
    
    for i in range(steps + 1):
        progress = i / steps
        # Logarithmic growth: fast initial growth, then slowing down
        value = initial + (final - initial) * (1 - (1 - progress) ** 2)
        points.append({
            "hour": i,
            "value": int(value),
            "progress": progress
        })
    
    return points

def calculate_crooked_growth(initial: int, final: int, days: float) -> List[Dict]:
    """Calculate crooked growth curve (V4's special algorithm)"""
    points = []
    steps = int(days * 24)
    
    for i in range(steps + 1):
        progress = i / steps
        
        # Crooked algorithm: non-linear with random variations
        base_value = initial + (final - initial) * progress
        
        # Add some "crookedness" - variations that make it look more natural
        variation = 0
        if progress > 0.1 and progress < 0.9:
            # Add random variations in the middle section
            import random
            variation = random.uniform(-0.1, 0.1) * (final - initial)
        
        value = max(0, base_value + variation)
        points.append({
            "hour": i,
            "value": int(value),
            "progress": progress
        })
    
    return points
