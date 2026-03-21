from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.models.test_api import TestAPIConfig, APILog
from app.models.user import User
from app.api.auth import get_current_user, get_op_user
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import httpx
import asyncio
import random
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for requests
class CreateTestAPIConfigRequest(BaseModel):
    name: str
    description: str = ""
    is_enabled: bool = False
    mock_responses: bool = True
    intercept_growth_orders: bool = False  # New field
    real_api_url: str = ""
    real_api_key: str = ""
    success_response: dict = {"order": 99999}
    error_response: dict = {"error": "Test error message"}
    add_order_template: dict = {
        "key": "{api_key}",
        "action": "add", 
        "service": "{service_id}",
        "link": "{link}",
        "quantity": "{quantity}"
    }
    status_template: dict = {
        "key": "{api_key}",
        "action": "status",
        "order": "{order_id}"
    }
    balance_template: dict = {
        "key": "{api_key}",
        "action": "balance"
    }
    response_delay_ms: int = 1000
    failure_rate_percent: int = 0
    log_requests: bool = True
    log_responses: bool = True

class UpdateTestAPIConfigRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    mock_responses: Optional[bool] = None
    intercept_growth_orders: Optional[bool] = None  # New field
    real_api_url: Optional[str] = None
    real_api_key: Optional[str] = None
    success_response: Optional[dict] = None
    error_response: Optional[dict] = None
    add_order_template: Optional[dict] = None
    status_template: Optional[dict] = None
    balance_template: Optional[dict] = None
    response_delay_ms: Optional[int] = None
    failure_rate_percent: Optional[int] = None
    log_requests: Optional[bool] = None
    log_responses: Optional[bool] = None

class TestOrderRequest(BaseModel):
    action: str  # "add", "status", or "balance"
    api_key: str
    service_id: Optional[str] = None
    link: Optional[str] = None
    quantity: Optional[int] = None
    order_id: Optional[str] = None

# Test API Config Management (OP only)
@router.get("/test-configs")
async def get_test_api_configs(current_user: User = Depends(get_op_user)):
    """Get all test API configurations (OP only)"""
    
    configs = TestAPIConfig.objects()
    
    return {
        "configs": [config.to_dict() for config in configs],
        "total": len(configs)
    }

@router.post("/test-configs")
async def create_test_api_config(
    request: CreateTestAPIConfigRequest,
    current_user: User = Depends(get_op_user)
):
    """Create a new test API configuration (OP only)"""
    
    config = TestAPIConfig(
        name=request.name,
        description=request.description,
        is_enabled=request.is_enabled,
        mock_responses=request.mock_responses,
        real_api_url=request.real_api_url,
        real_api_key=request.real_api_key,
        success_response=request.success_response,
        error_response=request.error_response,
        add_order_template=request.add_order_template,
        status_template=request.status_template,
        balance_template=request.balance_template,
        response_delay_ms=request.response_delay_ms,
        failure_rate_percent=request.failure_rate_percent,
        log_requests=request.log_requests,
        log_responses=request.log_responses,
        created_by=current_user
    )
    config.save()
    
    return {
        "message": "Test API configuration created successfully!",
        "config": config.to_dict()
    }

@router.put("/test-configs/{config_id}")
async def update_test_api_config(
    config_id: str,
    request: UpdateTestAPIConfigRequest,
    current_user: User = Depends(get_op_user)
):
    """Update a test API configuration (OP only)"""
    
    config = TestAPIConfig.objects(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Test API configuration not found")
    
    # Update fields that are provided
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    config.updated_at = datetime.utcnow()
    config.save()
    
    return {
        "message": "Test API configuration updated successfully!",
        "config": config.to_dict()
    }

@router.delete("/test-configs/{config_id}")
async def delete_test_api_config(
    config_id: str,
    current_user: User = Depends(get_op_user)
):
    """Delete a test API configuration (OP only)"""
    
    config = TestAPIConfig.objects(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Test API configuration not found")
    
    config_name = config.name
    config.delete()
    
    return {
        "message": f"Test API configuration '{config_name}' deleted successfully!"
    }

# Test API Endpoint
@router.post("/test-api")
async def test_api_endpoint(
    request: TestOrderRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Test API endpoint that simulates the external SMM API
    Based on the API documentation from your images
    """
    
    # Get the active test configuration
    config = TestAPIConfig.objects(is_enabled=True).first()
    if not config:
        raise HTTPException(
            status_code=503, 
            detail="No test API configuration is currently enabled"
        )
    
    # Create log entry
    log_entry = APILog(
        endpoint_name=config.name,
        method="POST",
        url="/api/test-api",
        request_body=request.dict(),
        user=current_user,
        is_test_mode=True
    )
    
    start_time = datetime.utcnow()
    
    try:
        # Simulate API delay
        if config.response_delay_ms > 0:
            await asyncio.sleep(config.response_delay_ms / 1000)
        
        # Simulate random failures
        if config.failure_rate_percent > 0:
            if random.randint(1, 100) <= config.failure_rate_percent:
                log_entry.response_status = 500
                log_entry.response_body = config.error_response
                log_entry.mock_response_used = True
                log_entry.response_timestamp = datetime.utcnow()
                log_entry.duration_ms = (log_entry.response_timestamp - start_time).total_seconds() * 1000
                
                if config.log_requests:
                    log_entry.save()
                
                return config.error_response
        
        # Process the request based on action
        response_data = {}
        
        if request.action == "add":
            if not all([request.service_id, request.link, request.quantity]):
                raise HTTPException(
                    status_code=400,
                    detail="Missing required parameters for add action: service_id, link, quantity"
                )
            
            # Use the success response template
            response_data = config.success_response.copy()
            if "order" in response_data:
                # Generate a random order ID for testing
                response_data["order"] = random.randint(100000, 999999)
            
            log_entry.order_id = str(response_data.get("order", ""))
            
        elif request.action == "status":
            if not request.order_id:
                raise HTTPException(
                    status_code=400,
                    detail="Missing required parameter for status action: order_id"
                )
            
            # Mock status response based on your API documentation
            response_data = {
                "charge": "10.0000",
                "start_count": "100",
                "status": random.choice(["Pending", "Processing", "In progress", "Completed", "Partial", "Canceled"]),
                "remains": "90"
            }
            
            log_entry.order_id = request.order_id
            
        elif request.action == "balance":
            # Mock balance response based on your API documentation
            response_data = {
                "balance": f"{random.uniform(10, 1000):.4f}",
                "currency": "USD"
            }
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported action: {request.action}. Supported actions: add, status, balance"
            )
        
        # Update log entry
        log_entry.response_status = 200
        log_entry.response_body = response_data
        log_entry.mock_response_used = config.mock_responses
        log_entry.response_timestamp = datetime.utcnow()
        log_entry.duration_ms = (log_entry.response_timestamp - start_time).total_seconds() * 1000
        
        if config.log_requests:
            log_entry.save()
        
        return response_data
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in test API endpoint: {e}")
        
        # Log the error
        log_entry.response_status = 500
        log_entry.response_body = {"error": str(e)}
        log_entry.response_timestamp = datetime.utcnow()
        log_entry.duration_ms = (log_entry.response_timestamp - start_time).total_seconds() * 1000
        
        if config.log_requests:
            log_entry.save()
        
        raise HTTPException(status_code=500, detail="Internal server error")

# API Logs (OP only)
@router.get("/logs")
async def get_api_logs(
    limit: int = 100,
    endpoint_name: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: User = Depends(get_op_user)
):
    """Get API logs (OP only)"""
    
    query = APILog.objects()
    
    if endpoint_name:
        query = query.filter(endpoint_name=endpoint_name)
    
    if user_id:
        query = query.filter(user=user_id)
    
    logs = query.order_by('-request_timestamp').limit(limit)
    
    return {
        "logs": [log.to_dict() for log in logs],
        "total": len(logs)
    }

@router.get("/logs/stats")
async def get_api_log_stats(current_user: User = Depends(get_op_user)):
    """Get API log statistics (OP only)"""
    
    total_requests = APILog.objects().count()
    test_requests = APILog.objects(is_test_mode=True).count()
    
    # Get recent activity (last 24 hours)
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_requests = APILog.objects(request_timestamp__gte=yesterday).count()
    
    # Get success rate
    success_requests = APILog.objects(response_status=200).count()
    success_rate = (success_requests / total_requests * 100) if total_requests > 0 else 0
    
    # Get average response time
    logs_with_duration = APILog.objects(duration_ms__ne=None)
    avg_response_time = 0
    if logs_with_duration:
        total_duration = sum(log.duration_ms for log in logs_with_duration)
        avg_response_time = total_duration / len(logs_with_duration)
    
    return {
        "total_requests": total_requests,
        "test_requests": test_requests,
        "recent_requests_24h": recent_requests,
        "success_rate_percent": round(success_rate, 2),
        "avg_response_time_ms": round(avg_response_time, 2)
    }

@router.delete("/logs/clear")
async def clear_api_logs(
    older_than_hours: int = 24,
    current_user: User = Depends(get_op_user)
):
    """Clear old API logs (OP only)"""
    
    from datetime import timedelta
    cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
    
    deleted_count = APILog.objects(request_timestamp__lt=cutoff_time).delete()
    
    return {
        "message": f"Deleted {deleted_count} log entries older than {older_than_hours} hours"
    }
