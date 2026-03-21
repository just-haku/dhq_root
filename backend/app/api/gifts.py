from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.models.kpi import KPIHistory
from app.models.arcade import UserArcadeProfile, DailyBonusConfig
from app.api.auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.get("/profile")
async def get_gifts_profile(
    current_user: User = Depends(get_current_user)
):
    """Get user's gifting-related profile data"""
    profile = UserArcadeProfile.objects(user=current_user).first()
    if not profile:
        profile = UserArcadeProfile(user=current_user).save()
    
    return {
        "login_streak": profile.login_streak,
        "last_login": profile.last_login.isoformat() if profile.last_login else None,
        "kpi_balance": current_user.kpi_current
    }

@router.get("/config")
async def get_public_bonus_config():
    """Get daily bonus configuration (public)"""
    config = DailyBonusConfig.objects(is_active=True).first()
    if not config:
        config = DailyBonusConfig(percentages=[0.0]*30).save()
    return config

@router.post("/claim")
async def claim_daily_gift(
    current_user: User = Depends(get_current_user)
):
    """Claim daily login gift"""
    profile = UserArcadeProfile.objects(user=current_user).first()
    if not profile:
        profile = UserArcadeProfile(user=current_user)
    
    # Check if already claimed today
    today = datetime.utcnow().date()
    if profile.last_login and profile.last_login.date() == today:
        raise HTTPException(status_code=400, detail="Daily gift already claimed")
    
    # Update login streak and award KPI
    profile.update_login_streak()
    
    # Calculate KPI bonus based on config
    config = DailyBonusConfig.objects(is_active=True).first()
    base_bonus = config.base_bonus if config else 5
    percentages = config.percentages if config else [0.0]*30
    
    # Get percentage for current streak day (1-30)
    streak_idx = min(profile.login_streak - 1, 29)
    bonus_percentage = percentages[streak_idx]
    
    total_kpi = int(base_bonus * (1 + bonus_percentage))
    
    # Award KPI to user
    current_user.kpi_current += total_kpi
    current_user.kpi_lifetime += total_kpi
    current_user.save()
    
    # Create KPI history entry
    KPIHistory(
        user=current_user,
        amount=total_kpi,
        balance_after=current_user.kpi_current,
        source="daily_bonus",
        reason=f"Daily login gift (streak: {profile.login_streak}, multiplier: {1+bonus_percentage}x)"
    ).save()
    
    profile.save()
    
    return {
        "message": "Daily gift claimed!",
        "kpi_awarded": total_kpi,
        "login_streak": profile.login_streak,
        "new_balance": current_user.kpi_current
    }
