from fastapi import APIRouter, HTTPException, Depends, Response
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.order_center import OrderCenterOrder, OrderCenterSubOrder
from app.models.user import User
from app.api.auth import get_current_user, get_op_user
from app.services.order_center_service import OrderCenterService
from app.services.service_cache_task import service_cache_task
import io
import json

router = APIRouter()

class OrderCreateRequest(BaseModel):
    name: str
    unit_label: str
    target_link: str
    total_qty: int
    total_time: int
    time_unit: str
    step_mins: int
    tolerance_pct: int
    graph_type: str
    api_service_id: str
    api_server_id: Optional[str] = None
    est_cost: float

class APIServerRequest(BaseModel):
    name: str
    display_name: str
    base_url: str
    is_active: bool = True
    is_external: bool = True
    rate_per_1000: float = 0.0
    priority: int = 1
    api_key: Optional[str] = None

@router.post("/create")
async def create_order(request: OrderCreateRequest, user: User = Depends(get_current_user)):
    try:
        order = await OrderCenterService.create_order(user, request.dict())
        return {"status": "success", "order_id": str(order.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_orders(user: User = Depends(get_current_user)):
    orders = OrderCenterOrder.objects(user=user).order_by('-created_at')
    return [
        {
            "id": str(o.id),
            "name": o.name,
            "status": o.status,
            "created_at": o.created_at,
            "total_qty": o.total_qty,
            "target_link": o.target_link
        } for o in orders
    ]


@router.post("/{order_id:[0-9a-fA-F]{24}}/pause")
async def pause_order(order_id: str, user: User = Depends(get_current_user)):
    success = await OrderCenterService.pause_order(order_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to pause order")
    return {"status": "success"}

@router.post("/{order_id:[0-9a-fA-F]{24}}/resume")
async def resume_order(order_id: str, user: User = Depends(get_current_user)):
    success = await OrderCenterService.resume_order(order_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to resume order")
    return {"status": "success"}

@router.post("/{order_id:[0-9a-fA-F]{24}}/sub-order/{sub_id}/force")
async def force_sub_order(order_id: str, sub_id: str, user: User = Depends(get_current_user)):
    success = await OrderCenterService.force_sub_order(order_id, sub_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to force sub-order")
    return {"status": "success"}

@router.get("/services/cached")
async def get_cached_services(user: User = Depends(get_current_user)):
    services = await service_cache_task.get_cached_services()
    return services

@router.get("/operator/settings")
async def get_operator_settings(user: User = Depends(get_op_user)):
    from app.core.database import redis_client
    import json
    
    timezone = await redis_client.hget("admin:timezone_config", "timezone")
    mock_api_enabled = await redis_client.hget("admin:timezone_config", "mock_api_enabled")
    success_rate = await redis_client.hget("admin:timezone_config", "mock_success_rate")
    sync_interval = await redis_client.hget("admin:timezone_config", "status_sync_interval")
    
    return {
        "timezone": (timezone.decode() if timezone else "GMT+7"),
        "mock_api_enabled": (mock_api_enabled.decode() == "True" if mock_api_enabled else False),
        "mock_success_rate": (int(success_rate.decode()) if success_rate else 100),
        "status_sync_interval": (int(sync_interval.decode()) if sync_interval else 5)
    }

@router.post("/operator/settings")
async def update_operator_settings(settings: dict, user: User = Depends(get_op_user)):
    from app.core.database import redis_client
    
    if "timezone" in settings:
        await redis_client.hset("admin:timezone_config", "timezone", settings["timezone"])
    if "mock_api_enabled" in settings:
        await redis_client.hset("admin:timezone_config", "mock_api_enabled", "True" if settings["mock_api_enabled"] else "False")
    if "mock_success_rate" in settings:
        await redis_client.hset("admin:timezone_config", "mock_success_rate", str(settings["mock_success_rate"]))
    if "status_sync_interval" in settings:
        await redis_client.hset("admin:timezone_config", "status_sync_interval", str(settings["status_sync_interval"]))
        
    return {"status": "success"}

@router.get("/operator/api-servers")
async def list_api_servers(user: User = Depends(get_op_user)):
    from app.models.api_server import APIServer
    servers = APIServer.objects().order_by('priority')
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "display_name": s.display_name,
            "base_url": s.base_url,
            "is_active": s.is_active,
            "is_external": s.is_external,
            "priority": s.priority
        } for s in servers
    ]

@router.post("/operator/api-servers")
async def add_update_api_server(req: APIServerRequest, server_id: Optional[str] = None, user: User = Depends(get_op_user)):
    from app.models.api_server import APIServer
    
    if server_id:
        server = APIServer.objects(id=server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
    else:
        server = APIServer()
        
    server.name = req.name
    server.display_name = req.display_name
    server.base_url = req.base_url
    server.is_active = req.is_active
    server.is_external = req.is_external
    server.rate_per_1000 = req.rate_per_1000
    server.priority = req.priority
    if req.api_key is not None:
        server.api_key = req.api_key
    server.save()
    
    return {"status": "success", "server_id": str(server.id)}

@router.delete("/operator/api-servers/{server_id}")
async def delete_api_server(server_id: str, user: User = Depends(get_op_user)):
    from app.models.api_server import APIServer
    server = APIServer.objects(id=server_id).first()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    server.delete()
    return {"status": "success"}

@router.post("/operator/api-servers/{server_id}/delete")
async def delete_api_server_post(server_id: str, user: User = Depends(get_op_user)):
    return await delete_api_server(server_id, user)

@router.get("/api-servers/active")
async def list_active_servers(user: User = Depends(get_current_user)):
    from app.models.api_server import APIServer
    servers = APIServer.objects(is_active=True).order_by('priority')
    return [
        {
            "id": str(s.id),
            "display_name": s.display_name,
            "has_system_key": bool(s.api_key)
        } for s in servers
    ]

@router.get("/balance")
async def get_server_balance(server_id: Optional[str] = None, user: User = Depends(get_current_user)):
    try:
        from app.services.external_api import ExternalAPIService
        from app.models.api_server import UserAPIKey
        import logging
        logger = logging.getLogger(__name__)
        
        # Try to get user's API key for this server
        api_key = user.personal_api_key
        
        # Robust server_id cleaning for frontend edge cases
        if not server_id or server_id in ["null", "undefined", ""]:
            server_id = None
            
        if server_id:
            try:
                user_key_obj = UserAPIKey.objects(user_id=str(user.id), api_server_id=server_id, is_active=True).first()
                if user_key_obj:
                    api_key = user_key_obj.api_key
                else:
                    # Fallback to system key if provided by OP
                    from app.models.api_server import APIServer
                    import re
                    if re.match(r"^[0-9a-fA-F]{24}$", str(server_id)):
                        server = APIServer.objects(id=server_id).first()
                        if server and server.api_key:
                            api_key = server.api_key
            except Exception as query_err:
                logger.warning(f"Error querying UserAPIKey for server {server_id}: {query_err}")
                # Fallback to system key
                pass
                
        if not api_key:
            # Check if this is the internal server (often passed as empty string or name)
            from app.models.api_server import APIServer
            is_internal = False
            if not server_id:
                is_internal = True
            else:
                try:
                    server = APIServer.objects(id=server_id).first()
                    if server and server.name == 'internal_api_server':
                        is_internal = True
                except:
                    pass
            
            if is_internal:
                return {"balance": f"{user.api_dollar_balance:.2f}", "currency": "USD"}
                
            return {"balance": "0.00", "currency": "USD", "error": "API Key not configured"}
            
        success, data = await ExternalAPIService.check_balance(api_key, server_id)
        
        # If external check failed but it's internal server (unlikely if api_key exists but good to be safe)
        if not success and (not server_id or server_id == 'internal_api_server'):
             return {"balance": f"{user.api_dollar_balance:.2f}", "currency": "USD"}
             
        return data
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Critical error in /balance: {e}")
        return {"balance": "0.00", "currency": "USD", "error": "Internal server error"}

@router.get("/{order_id:[0-9a-fA-F]{24}}/report-pdf")
async def download_report(order_id: str, user: User = Depends(get_current_user)):
    order = OrderCenterOrder.objects(id=order_id, user=user).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom style for dark theme matching
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Heading1'],
            textColor=colors.hexColor("#38bdf8"), # Sky blue
            alignment=1
        )
        
        content = []
        
        # Header
        content.append(Paragraph(f"Order Report: {order.name}", header_style))
        content.append(Spacer(1, 12))
        
        # Order Info
        info_data = [
            ["Order ID", str(order.id)],
            ["Target", order.target_link],
            ["Total Qty", str(order.total_qty)],
            ["Status", order.status],
            ["Graph Type", order.graph_type],
            ["Estimated Cost", f"${order.est_cost:.2f}"]
        ]
        t = Table(info_data, colWidths=[100, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.hexColor("#1e293b")),
            ('TEXTCOLOR', (0,0), (0,-1), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
        ]))
        content.append(t)
        content.append(Spacer(1, 24))
        
        # Sub-orders Table
        content.append(Paragraph("Sub-Orders Distribution", styles['Heading2']))
        sub_data = [["Ordinal", "Qty", "Scheduled Time", "Status", "Cost"]]
        for sub in order.sub_orders:
            sub_data.append([
                str(sub.ordinal_number),
                str(sub.qty),
                sub.scheduled_time.strftime("%Y-%m-%d %H:%M"),
                sub.internal_status,
                f"${sub.cost:.2f}"
            ])
            
        st = Table(sub_data, colWidths=[50, 60, 150, 100, 80])
        st.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.hexColor("#0f172a")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
        ]))
        content.append(st)
        
        # Appendix with RAW JSON
        content.append(PageBreak())
        content.append(Paragraph("Appendix: RAW API Responses", styles['Heading2']))
        
        for sub in order.sub_orders:
            if sub.api_order_ids:
                content.append(Paragraph(f"Sub-Order ID: {sub.id}", styles['Heading3']))
                # In a real system we'd store the full raw response, but here we just have api_order_ids
                raw_json = json.dumps({"sub_id": sub.id, "api_id": sub.api_order_ids, "status": sub.api_status}, indent=2)
                content.append(Paragraph(f"<pre>{raw_json}</pre>", styles['Code']))
                content.append(Spacer(1, 12))

        doc.build(content)
        buffer.seek(0)
        
        return Response(
            content=buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=order_report_{order_id}.pdf"}
        )
        
    except ImportError:
        return {"error": "PDF generation library (reportlab) not found. Contact administrator."}
    except Exception as e:
        return {"error": f"Failed to generate PDF: {str(e)}"}

@router.get("/{order_id:[0-9a-fA-F]{24}}")
async def get_order(order_id: str, user: User = Depends(get_current_user)):
    order = OrderCenterOrder.objects(id=order_id, user=user).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Calculate costs
    actual_cost = sum(sub.cost for sub in order.sub_orders if sub.internal_status == 'Success')
    
    return {
        "id": str(order.id),
        "name": order.name,
        "status": order.status,
        "unit_label": order.unit_label,
        "target_link": order.target_link,
        "total_qty": order.total_qty,
        "total_time": order.total_time,
        "time_unit": order.time_unit,
        "step_mins": order.step_mins,
        "tolerance_pct": order.tolerance_pct,
        "graph_type": order.graph_type,
        "est_cost": order.est_cost,
        "actual_cost": actual_cost,
        "sub_orders": [
            {
                "id": sub.id,
                "ordinal": sub.ordinal_number,
                "qty": sub.qty,
                "scheduled_time": sub.scheduled_time,
                "internal_status": sub.internal_status,
                "api_status": sub.api_status,
                "is_enabled": sub.is_enabled,
                "cost": sub.cost
            } for sub in order.sub_orders
        ]
    }
