from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.models.order import APIEndpoint, Order
from app.models.user import User
from app.models.kpi import KPIHistory
from app.api.auth import get_current_user, get_op_user
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import httpx
import json
import asyncio

router = APIRouter()

# Pydantic models for requests
class CreateAPIEndpointRequest(BaseModel):
    name: str
    description: str = ""
    endpoint_url: str
    method: str = "POST"
    auth_type: str = "API_KEY"
    api_key: str = ""
    headers: dict = {}
    request_template: dict = {}
    success_criteria: dict = {}
    response_mapping: dict = {}
    cost_kpi: int = 0
    cost_currency: float = 0.0
    is_public: bool = False

class UpdateAPIEndpointRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    endpoint_url: Optional[str] = None
    method: Optional[str] = None
    auth_type: Optional[str] = None
    api_key: Optional[str] = None
    headers: Optional[dict] = None
    request_template: Optional[dict] = None
    success_criteria: Optional[dict] = None
    response_mapping: Optional[dict] = None
    cost_kpi: Optional[int] = None
    cost_currency: Optional[float] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None

class CreateOrderRequest(BaseModel):
    endpoint_id: str
    request_data: dict = {}

# API Endpoint Management (OP only)
@router.get("/endpoints")
async def get_api_endpoints(current_user: User = Depends(get_current_user)):
    """Get available API endpoints"""
    
    # Get endpoints - OP sees all, users see only public ones
    if current_user.role == 'OP':
        endpoints = APIEndpoint.objects()
    else:
        endpoints = APIEndpoint.objects(is_public=True, is_active=True)
    
    return {
        "endpoints": [endpoint.to_dict() for endpoint in endpoints],
        "total": len(endpoints)
    }

@router.post("/endpoints")
async def create_api_endpoint(
    request: CreateAPIEndpointRequest,
    current_user: User = Depends(get_op_user)
):
    """Create a new API endpoint (OP only)"""
    
    endpoint = APIEndpoint(
        name=request.name,
        description=request.description,
        endpoint_url=request.endpoint_url,
        method=request.method,
        auth_type=request.auth_type,
        api_key=request.api_key,  # In production, this should be encrypted
        headers=request.headers,
        request_template=request.request_template,
        success_criteria=request.success_criteria,
        response_mapping=request.response_mapping,
        cost_kpi=request.cost_kpi,
        cost_currency=request.cost_currency,
        is_public=request.is_public,
        created_by=current_user
    )
    endpoint.save()
    
    return {
        "message": "API endpoint created successfully!",
        "endpoint": endpoint.to_dict()
    }

@router.put("/endpoints/{endpoint_id}")
async def update_api_endpoint(
    endpoint_id: str,
    request: UpdateAPIEndpointRequest,
    current_user: User = Depends(get_op_user)
):
    """Update an API endpoint (OP only)"""
    
    endpoint = APIEndpoint.objects(id=endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Update fields that are provided
    if request.name is not None:
        endpoint.name = request.name
    if request.description is not None:
        endpoint.description = request.description
    if request.endpoint_url is not None:
        endpoint.endpoint_url = request.endpoint_url
    if request.method is not None:
        endpoint.method = request.method
    if request.auth_type is not None:
        endpoint.auth_type = request.auth_type
    if request.api_key is not None:
        endpoint.api_key = request.api_key
    if request.headers is not None:
        endpoint.headers = request.headers
    if request.request_template is not None:
        endpoint.request_template = request.request_template
    if request.success_criteria is not None:
        endpoint.success_criteria = request.success_criteria
    if request.response_mapping is not None:
        endpoint.response_mapping = request.response_mapping
    if request.cost_kpi is not None:
        endpoint.cost_kpi = request.cost_kpi
    if request.cost_currency is not None:
        endpoint.cost_currency = request.cost_currency
    if request.is_public is not None:
        endpoint.is_public = request.is_public
    if request.is_active is not None:
        endpoint.is_active = request.is_active
    
    endpoint.updated_at = datetime.utcnow()
    endpoint.save()
    
    return {
        "message": "API endpoint updated successfully!",
        "endpoint": endpoint.to_dict()
    }

@router.delete("/endpoints/{endpoint_id}")
async def delete_api_endpoint(
    endpoint_id: str,
    current_user: User = Depends(get_op_user)
):
    """Delete an API endpoint (OP only)"""
    
    endpoint = APIEndpoint.objects(id=endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    endpoint_name = endpoint.name
    endpoint.delete()
    
    return {
        "message": f"API endpoint '{endpoint_name}' deleted successfully!"
    }

# Order Management
async def process_order(order_id: str):
    """Background task to process an order"""
    try:
        order = Order.objects(id=order_id).first()
        if not order:
            return
        
        order.status = 'PROCESSING'
        order.save()
        
        if order.api_endpoint:
            await execute_api_call(order)
        else:
            # Handle other order types
            order.status = 'COMPLETED'
            order.response_data = {"message": "Order processed successfully"}
        
        order.updated_at = datetime.utcnow()
        order.completed_at = datetime.utcnow()
        order.save()
        
    except Exception as e:
        order.status = 'FAILED'
        order.error_message = str(e)
        order.updated_at = datetime.utcnow()
        order.save()

async def execute_api_call(order: Order):
    """Execute the actual API call"""
    endpoint = order.api_endpoint
    
    # Prepare headers
    headers = endpoint.headers.copy()
    
    # Add authentication
    if endpoint.auth_type == 'API_KEY' and endpoint.api_key:
        headers['X-API-Key'] = endpoint.api_key
    elif endpoint.auth_type == 'BEARER_TOKEN' and endpoint.api_key:
        headers['Authorization'] = f'Bearer {endpoint.api_key}'
    
    # Prepare request data
    request_data = endpoint.request_template.copy()
    request_data.update(order.request_data)
    
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=endpoint.method,
            url=endpoint.endpoint_url,
            headers=headers,
            json=request_data if endpoint.method in ['POST', 'PUT'] else None,
            params=request_data if endpoint.method == 'GET' else None
        )
        
        order.response_data = {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'body': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
        
        # Check success criteria
        if endpoint.success_criteria:
            # Simple success check - can be expanded
            if 'status_code' in endpoint.success_criteria:
                expected_codes = endpoint.success_criteria['status_code']
                if isinstance(expected_codes, int):
                    expected_codes = [expected_codes]
                
                if response.status_code not in expected_codes:
                    order.status = 'FAILED'
                    order.error_message = f"API returned status code {response.status_code}"
                    return
        
        order.status = 'COMPLETED'

@router.post("/orders")
async def create_order(
    request: CreateOrderRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Create a new order"""
    
    # Get the API endpoint
    endpoint = APIEndpoint.objects(id=request.endpoint_id).first()
    if not endpoint:
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    if not endpoint.is_active:
        raise HTTPException(status_code=400, detail="API endpoint is not active")
    
    if not endpoint.is_public and current_user.role != 'OP':
        raise HTTPException(status_code=403, detail="Access denied to this endpoint")
    
    # Check if user has enough KPI
    if current_user.kpi_current < endpoint.cost_kpi:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient KPI points. Need {endpoint.cost_kpi} KPI."
        )
    
    # Deduct KPI cost
    current_user.kpi_current -= endpoint.cost_kpi
    current_user.save()
    
    # Create KPI history entry
    KPIHistory(
        user=current_user,
        amount=-endpoint.cost_kpi,
        balance_after=current_user.kpi_current,
        source="order_cost",
        reason=f"Order for {endpoint.name}",
        related_entity_type="order"
    ).save()
    
    # Create order
    order = Order(
        order_type='API_CALL',
        service_name=endpoint.name,
        api_endpoint=endpoint,
        user=current_user,
        request_data=request.request_data,
        cost_kpi=endpoint.cost_kpi,
        cost_currency=endpoint.cost_currency,
        paid_kpi=endpoint.cost_kpi,
        status='PENDING'
    )
    order.save()
    
    # Process order in background
    background_tasks.add_task(process_order, str(order.id))
    
    return {
        "message": "Order created successfully!",
        "order": order.to_dict()
    }

@router.get("/orders")
async def get_orders(
    status: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get user's orders"""
    
    query = Order.objects(user=current_user)
    
    if status:
        query = query.filter(status=status)
    
    orders = query.order_by('-created_at').limit(limit)
    
    return {
        "orders": [order.to_dict() for order in orders],
        "total": len(orders)
    }

@router.get("/orders/all")
async def get_all_orders(
    status: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_op_user)
):
    """Get all orders (OP only)"""
    
    query = Order.objects()
    
    if status:
        query = query.filter(status=status)
    
    orders = query.order_by('-created_at').limit(limit)
    
    return {
        "orders": [order.to_dict() for order in orders],
        "total": len(orders)
    }

@router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific order details"""
    
    order = Order.objects(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check access - OP can see all, users can only see their own
    if current_user.role != 'OP' and order.user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "order": order.to_dict()
    }
