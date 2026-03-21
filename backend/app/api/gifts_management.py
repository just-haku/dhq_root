from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.api.auth import get_op_user
from app.models.arcade import UserArcadeProfile, DailyBonusConfig
from pydantic import BaseModel
from typing import List

router = APIRouter()

class KPIGiftRequest(BaseModel):
    user_id: str
    amount: int
    description: str = "KPI Gift from Admin"

class DailyBonusConfigRequest(BaseModel):
    base_bonus: int
    percentages: List[float]

@router.post("/gift")
async def gift_kpi(request: KPIGiftRequest, op_user: User = Depends(get_op_user)):
    """Admin tool to gift KPI to users"""
    profile = UserArcadeProfile.objects(user=request.user_id).first()
    if not profile:
        # Create profile if not exists
        user = User.objects(id=request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        profile = UserArcadeProfile(user=user).save()
        
    profile.add_kpi(request.amount, 'BONUS', description=request.description)
    profile.save()
    return {"message": f"Gifted {request.amount} KPI to user {request.user_id}"}

@router.get("/bonus-config")
async def get_bonus_config(op_user: User = Depends(get_op_user)):
    """Get daily bonus configuration"""
    config = DailyBonusConfig.objects(is_active=True).first()
    if not config:
        config = DailyBonusConfig(percentages=[0.0]*30).save()
    
    return {
        "base_bonus": config.base_bonus,
        "percentages": config.percentages,
        "is_active": config.is_active
    }

@router.get("/user-balance/{user_id}")
async def get_user_balance(user_id: str, op_user: User = Depends(get_op_user)):
    """Admin tool to view a user's current chips and KPI. user_id can be id or username."""
    # Find user first
    user = User.objects(username=user_id).first()
    if not user:
        # Fallback to secondary search if primary key is not what we think
        user = User.objects(id=user_id).first()
        
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")

    profile = UserArcadeProfile.objects(user=user).first()
    if not profile:
        profile = UserArcadeProfile(user=user).save()
    
    return {
        "kpi_balance": user.kpi_current, # Pull from main user model per new sync rule
        "chip_balance": profile.chip_balance,
        "username": user.username
    }

@router.post("/bonus-config")
async def update_bonus_config(request: DailyBonusConfigRequest, op_user: User = Depends(get_op_user)):
    """Update daily bonus configuration"""
    config = DailyBonusConfig.objects(is_active=True).first()
    if not config:
        config = DailyBonusConfig()
    
    config.base_bonus = request.base_bonus
    config.percentages = request.percentages[:30]
    config.save()
    return {"message": "Daily bonus configuration updated"}

@router.get("/users/search")
async def search_users(query: str, op_user: User = Depends(get_op_user)):
    """Search for users by username or email for gifting"""
    users = User.objects(username__icontains=query).limit(10)
    if not users:
        users = User.objects(email__icontains=query).limit(10)
    
    return [{"id": str(u.id), "username": u.username, "display_name": u.display_name} for u in users]
