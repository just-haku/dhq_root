#!/usr/bin/env python3
"""
Test API Server for DHQ Integration Testing
Runs on port 8002 to avoid conflicts with Socket.IO (port 8001)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import time
import asyncio
from datetime import datetime
import json

app = FastAPI(title="DHQ Test API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OrderRequest(BaseModel):
    action: str
    key: str
    service: str
    link: str
    quantity: int

class StatusRequest(BaseModel):
    action: str
    key: str
    orders: str

class BalanceRequest(BaseModel):
    action: str
    key: str

# Test data store
test_orders = {}
order_counter = 100000

@app.get("/")
async def root():
    return {"message": "DHQ Test API Server", "port": 8002, "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v2")
async def handle_smm_request(request: dict):
    """
    Handle SMM API requests with configurable behavior
    """
    global order_counter
    
    action = request.get('action', '')
    
    if action == 'add':
        return await handle_add_order(request)
    elif action == 'status':
        return await handle_check_status(request)
    elif action == 'balance':
        return await handle_check_balance(request)
    else:
        return {"error": f"Unknown action: {action}"}

async def handle_add_order(request: dict):
    """Handle order creation with configurable delays and failures"""
    global order_counter
    
    # Check for failure rate override in request
    failure_rate = 0.1  # Default 10% failure
    if 'failure_rate' in request:
        try:
            failure_rate = float(request['failure_rate']) / 100.0
        except:
            pass  # Use default if invalid
    
    # Simulate processing delay
    delay = random.uniform(0.5, 3.0)  # 0.5-3 second delay
    await asyncio.sleep(delay)
    
    # Simulate failures based on configured rate
    if random.random() < failure_rate:
        return {
            "error": "Test API simulated failure",
            "error_code": "SIMULATED_ERROR"
        }
    
    # Generate order
    order_id = order_counter
    order_counter += 1
    
    # Store order for status checks
    test_orders[str(order_id)] = {
        "order": order_id,
        "status": "Pending",
        "start_count": 0,
        "remains": request.get('quantity', 0),
        "created_at": datetime.utcnow().isoformat(),
        "service": request.get('service', ''),
        "link": request.get('link', '')
    }
    
    return {
        "order": order_id,
        "status": "Pending",
        "start_count": 0,
        "remains": request.get('quantity', 0)
    }

async def handle_check_status(request: dict):
    """Handle order status check"""
    order_id = request.get('orders', '')
    
    if order_id not in test_orders:
        return {"error": "Order not found"}
    
    order = test_orders[order_id]
    
    # Simulate order progress
    if order["status"] == "Pending":
        # Randomly progress the order
        if random.random() < 0.3:  # 30% chance to progress
            progress = random.randint(100, min(500, order["remains"]))
            order["start_count"] += progress
            order["remains"] -= progress
            
            if order["remains"] == 0:
                order["status"] = "Completed"
    
    return order

async def handle_check_balance(request: dict):
    """Handle balance check"""
    return {
        "balance": random.randint(100, 10000),
        "currency": "USD"
    }

@app.get("/test-api")
async def test_endpoint():
    """Direct test endpoint for the DHQ test system"""
    return {
        "message": "Test API endpoint working",
        "timestamp": datetime.utcnow().isoformat(),
        "order_count": len(test_orders)
    }

@app.get("/test-orders")
async def list_test_orders():
    """List all test orders for debugging"""
    return {
        "orders": test_orders,
        "total": len(test_orders)
    }

@app.delete("/test-orders")
async def clear_test_orders():
    """Clear all test orders"""
    global test_orders, order_counter
    test_orders.clear()
    order_counter = 100000
    return {"message": "All test orders cleared"}

if __name__ == "__main__":
    import uvicorn
    print("🧪 Starting DHQ Test API Server on port 8002...")
    print("📝 This server simulates SMM API behavior for testing")
    print("🔗 Available endpoints:")
    print("   POST /api/v2 - Main SMM API endpoint")
    print("   GET /test-api - Direct test endpoint")
    print("   GET /test-orders - List test orders")
    print("   DELETE /test-orders - Clear test orders")
    print("   GET /health - Health check")
    print("")
    
    uvicorn.run("test_api_server:app", host="0.0.0.0", port=8002, reload=True)
