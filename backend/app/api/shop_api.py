from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from app.models.shop import ShopItem, UserPurchase
from app.models.user import User
from app.api.auth import get_current_user, get_op_user
from app.core.notifications import send_notification
from app.core.storage import storage_service
import os
import uuid
import json

router = APIRouter()

@router.get("/shop/items")
async def get_shop_items():
    """Get active shop items"""
    items = ShopItem.objects(is_active=True).order_by('type', 'price')
    return [json.loads(item.to_json()) for item in items]

@router.post("/shop/purchase")
async def purchase_item(item_id: str, current_user: User = Depends(get_current_user)):
    """Purchase an item from the shop"""
    item = ShopItem.objects(id=item_id, is_active=True).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Check if user has enough currency (depends on item.type, here assuming KPI for simplicity)
    # The user might have different balances. For now let's use KPI balance.
    if current_user.kpi_current < item.price:
        raise HTTPException(status_code=400, detail="Insufficient KPI balance")
        
    # Deduct price
    current_user.kpi_current -= item.price
    
    # Add to inventory
    purchase = {
        "item_id": str(item.id),
        "name": item.name,
        "type": item.type,
        "purchased_at": str(uuid.uuid4()) # Unique purchase ID
    }
    current_user.inventory.append(purchase)
    current_user.save()
    
    # Record purchase
    log = UserPurchase(
        user_id=current_user.username,
        item_id=str(item.id),
        item_name=item.name,
        item_type=item.type,
        price_paid=item.price
    )
    log.save()
    
    import asyncio
    asyncio.create_task(send_notification(
        user_id=current_user.username,
        message=f"Purchase successful: {item.name}",
        n_type="ORDER",
        link="/shop"
    ))
    
    return {"message": "Purchase successful", "item": item.name}

# --- Operator Shop Management ---

@router.post("/admin/shop/items")
async def create_shop_item(
    name: str = Form(...),
    type: str = Form(...),
    price: int = Form(...),
    description: Optional[str] = Form(None),
    asset: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_op_user)
):
    """Create a new shop item with optional asset upload"""
    asset_url = None
    if asset:
        # Save asset to shop directory
        ext = asset.filename.split('.')[-1]
        filename = f"SHOP_{uuid.uuid4().hex}.{ext}"
        storage_path = storage_service.storages[0]
        shop_dir = os.path.join(storage_path, "shop_assets")
        os.makedirs(shop_dir, exist_ok=True)
        file_path = os.path.join(shop_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(await asset.read())
        asset_url = f"/api/uploads/shop/{filename}"
        
    item = ShopItem(
        name=name,
        type=type,
        price=price,
        description=description,
        asset_url=asset_url
    )
    item.save()
    return {"message": "Item created", "id": str(item.id)}

@router.delete("/admin/shop/items/{item_id}")
async def delete_shop_item(item_id: str, current_user: User = Depends(get_op_user)):
    """Delete a shop item"""
    item = ShopItem.objects(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.delete()
    return {"message": "Deleted"}
