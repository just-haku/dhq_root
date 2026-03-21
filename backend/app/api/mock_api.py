from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse
import random
import uuid

router = APIRouter()

@router.post("/api/v2")
async def mock_smm_api(
    request: Request,
    key: str = Form(...),
    action: str = Form(...)
):
    """Internal Mock SMM Panel Server"""
    
    # Common result for all mock responses
    base_response = {"test": "True"}
    
    if action == "services":
        return JSONResponse({
            **base_response,
            "services": [
                {"service": "101", "name": "YT Views [Low Drop]", "type": "Default", "category": "YouTube", "rate": "1.5", "min": "100", "max": "500000"},
                {"service": "102", "name": "FB Page Likes", "type": "Default", "category": "Facebook", "rate": "10.0", "min": "50", "max": "10000"},
                {"service": "103", "name": "IG Followers [Instant]", "type": "Default", "category": "Instagram", "rate": "0.5", "min": "10", "max": "1000000"},
                {"service": "104", "name": "TikTok Video Views", "type": "Default", "category": "TikTok", "rate": "0.1", "min": "500", "max": "2000000"},
            ]
        })
        
    if action == "add":
        # Form may contain service, link, quantity
        return JSONResponse({
            **base_response,
            "order": str(random.randint(100000, 999999))
        })
        
    if action == "status":
        order_ids = (await request.form()).get("order", "").split(",")
        results = {}
        for oid in order_ids:
            if not oid: continue
            results[oid] = {
                "charge": str(round(random.uniform(0.1, 5.0), 2)),
                "status": random.choice(["Completed", "Processing", "In progress", "Pending"]),
                "remains": "0"
            }
        
        if len(order_ids) == 1:
            return JSONResponse({**base_response, **results[order_ids[0]]})
        return JSONResponse({**base_response, **results})
        
    if action == "balance":
        return JSONResponse({
            **base_response,
            "balance": "100.00",
            "currency": "USD"
        })
        
    return JSONResponse({"error": "Invalid action"}, status_code=400)
