from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.models.kpi_bonus import DailyKPIBonus, KPIBonusCycle, KPIBonusConfig
from app.models.arcade import UserKPIHistory
from app.api.auth import get_current_user
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class BonusClaimResponse(BaseModel):
    success: bool
    message: str
    amount_claimed: Optional[int] = None
    new_kpi_total: Optional[int] = None

@router.get("/dashboard")
async def get_kpi_bonus_dashboard(current_user: User = Depends(get_current_user)):
    """Get KPI bonus dashboard information"""
    
    try:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get or create user's bonus cycle
        from app.models.kpi_bonus import KPIBonusCycle
        cycle = KPIBonusCycle.objects(user=current_user).first()
        if not cycle:
            cycle = KPIBonusCycle(
                user=current_user,
                current_cycle_start=today,
                current_day=1
            )
            cycle.save()
        
        # Get today's bonus
        from app.models.kpi_bonus import DailyKPIBonus
        daily_bonus = DailyKPIBonus.objects(
            user=current_user,
            date=today
        ).first()
        
        # Check if user can claim today
        can_claim = False
        bonus_amount = 0
        
        if daily_bonus and not daily_bonus.is_claimed:
            can_claim = True
            bonus_amount = daily_bonus.final_amount
        
        return {
            "success": True,
            "current_kpi": current_user.kpi_current,
            "current_cycle_day": cycle.current_day,
            "can_claim_today": can_claim,
            "today_bonus_amount": bonus_amount,
            "last_claim_date": daily_bonus.claimed_at.isoformat() if daily_bonus and daily_bonus.claimed_at else None
        }
    except Exception as e:
        print(f"KPI Bonus Dashboard Error: {e}")
        return {
            "success": True,
            "current_kpi": current_user.kpi_current,
            "current_cycle_day": 1,
            "can_claim_today": False,
            "today_bonus_amount": 0,
            "last_claim_date": None
        }

@router.get("/daily-bonus")
async def get_daily_bonus(current_user: User = Depends(get_current_user)):
    """Get today's daily KPI bonus information"""
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get or create user's bonus cycle
    cycle = KPIBonusCycle.objects(user=current_user).first()
    if not cycle:
        cycle = KPIBonusCycle(
            user=current_user,
            current_cycle_start=today,
            current_day=1
        )
        cycle.save()
    
    # Check if we need to start a new cycle
    if cycle.current_day > 30:
        cycle.current_day = 1
        cycle.current_cycle_start = today
        cycle.total_claimed_this_cycle = 0
        cycle.total_available_this_cycle = 0
        cycle.total_cycles_completed += 1
        cycle.current_streak = 0
        cycle.save()
    
    # Get today's bonus
    daily_bonus = DailyKPIBonus.objects(
        user=current_user,
        date=today
    ).first()
    
    config = KPIBonusConfig.get_config()
    
    # Create today's bonus if it doesn't exist
    if not daily_bonus:
        is_wednesday = today.weekday() == 2  # Wednesday is 2 in Python (0=Monday)
        bonus_calc = config.calculate_daily_amount(cycle.current_day, is_wednesday)
        
        daily_bonus = DailyKPIBonus(
            user=current_user,
            date=today,
            base_amount=bonus_calc['base_amount'],
            bonus_multiplier=bonus_calc['multiplier'],
            final_amount=bonus_calc['final_amount'],
            day_number=cycle.current_day,
            is_wednesday=bonus_calc['is_wednesday'],
            is_special_day=bonus_calc['is_special_day']
        )
        daily_bonus.save()
        
        # Update cycle total available
        cycle.total_available_this_cycle += daily_bonus.final_amount
        cycle.save()
    
    return {
        "daily_bonus": daily_bonus.to_dict(),
        "cycle": cycle.to_dict(),
        "can_claim": not daily_bonus.is_claimed and not daily_bonus.is_expired,
        "expires_in_hours": config.expiry_hours
    }

@router.post("/claim-bonus", response_model=BonusClaimResponse)
async def claim_daily_bonus(current_user: User = Depends(get_current_user)):
    """Claim today's daily KPI bonus"""
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get today's bonus
    daily_bonus = DailyKPIBonus.objects(
        user=current_user,
        date=today
    ).first()
    
    if not daily_bonus:
        return BonusClaimResponse(
            success=False,
            message="No bonus available for today"
        )
    
    if daily_bonus.is_claimed:
        return BonusClaimResponse(
            success=False,
            message="Bonus already claimed today"
        )
    
    if daily_bonus.is_expired:
        return BonusClaimResponse(
            success=False,
            message="Bonus has expired"
        )
    
    # Check if bonus is expired (24 hours from creation)
    config = KPIBonusConfig.get_config()
    expiry_time = daily_bonus.created_at + timedelta(hours=config.expiry_hours)
    if datetime.utcnow() > expiry_time:
        daily_bonus.is_expired = True
        daily_bonus.save()
        return BonusClaimResponse(
            success=False,
            message="Bonus has expired"
        )
    
    # Claim the bonus
    daily_bonus.is_claimed = True
    daily_bonus.claimed_at = datetime.utcnow()
    daily_bonus.save()
    
    # Update user's KPI
    current_user.kpi_current += daily_bonus.final_amount
    current_user.save()
    
    # Update cycle
    cycle = KPIBonusCycle.objects(user=current_user).first()
    if cycle:
        cycle.total_claimed_this_cycle += daily_bonus.final_amount
        cycle.total_lifetime_claimed += daily_bonus.final_amount
        
        # Update streak
        if cycle.last_claim_date:
            yesterday = today - timedelta(days=1)
            if cycle.last_claim_date.date() == yesterday.date():
                cycle.current_streak += 1
            else:
                cycle.current_streak = 1
        else:
            cycle.current_streak = 1
        
        cycle.longest_streak = max(cycle.longest_streak, cycle.current_streak)
        cycle.last_claim_date = datetime.utcnow()
        
        # Move to next day
        if cycle.current_day < 30:
            cycle.current_day += 1
        else:
            # Start new cycle
            cycle.current_day = 1
            cycle.current_cycle_start = today + timedelta(days=1)
            cycle.total_claimed_this_cycle = 0
            cycle.total_available_this_cycle = 0
            cycle.total_cycles_completed += 1
            cycle.current_streak = 0
        
        cycle.best_cycle_amount = max(cycle.best_cycle_amount, cycle.total_claimed_this_cycle)
        cycle.save()
    
    # Add to KPI history
    UserKPIHistory(
        user=current_user,
        kpi_amount=daily_bonus.final_amount,
        source_type='BONUS',
        source_id=str(daily_bonus.id),
        description=f"Daily KPI Bonus - Day {daily_bonus.day_number}"
    ).save()
    
    return BonusClaimResponse(
        success=True,
        message=f"Successfully claimed {daily_bonus.final_amount} KPI points!",
        amount_claimed=daily_bonus.final_amount,
        new_balance=current_user.kpi_current
    )

@router.get("/bonus-history")
async def get_bonus_history(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get KPI bonus history for the user"""
    
    end_date = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
    start_date = end_date - timedelta(days=days-1)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    bonuses = DailyKPIBonus.objects(
        user=current_user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    # Generate 30-day graph data
    graph_data = []
    current_date = start_date
    
    for i in range(days):
        day_bonus = None
        for bonus in bonuses:
            if bonus.date.date() == current_date.date():
                day_bonus = bonus
                break
        
        graph_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'day_number': i + 1,
            'available': day_bonus is not None,
            'amount': day_bonus.final_amount if day_bonus else 0,
            'claimed': day_bonus.is_claimed if day_bonus else False,
            'expired': day_bonus.is_expired if day_bonus else False,
            'is_wednesday': current_date.weekday() == 2,
            'base_amount': day_bonus.base_amount if day_bonus else 0,
            'multiplier': day_bonus.bonus_multiplier if day_bonus else 1.0
        })
        
        current_date += timedelta(days=1)
    
    # Calculate statistics
    total_available = sum(item['amount'] for item in graph_data)
    total_claimed = sum(item['amount'] for item in graph_data if item['claimed'])
    claim_rate = (total_claimed / total_available * 100) if total_available > 0 else 0
    
    return {
        'graph_data': graph_data,
        'statistics': {
            'total_available': total_available,
            'total_claimed': total_claimed,
            'claim_rate': round(claim_rate, 2),
            'days_claimed': sum(1 for item in graph_data if item['claimed']),
            'days_missed': sum(1 for item in graph_data if item['available'] and not item['claimed'] and not item['expired'])
        }
    }

@router.get("/cycle-info")
async def get_cycle_info(current_user: User = Depends(get_current_user)):
    """Get current cycle information"""
    
    cycle = KPIBonusCycle.objects(user=current_user).first()
    if not cycle:
        return {
            "message": "No cycle found",
            "cycle": None
        }
    
    # Get upcoming bonuses for next 7 days
    upcoming_bonuses = []
    config = KPIBonusConfig.get_config()
    
    for i in range(7):
        future_day = cycle.current_day + i
        if future_day > 30:
            future_day = future_day - 30  # Wrap around to next cycle
        
        future_date = datetime.utcnow() + timedelta(days=i)
        is_wednesday = future_date.weekday() == 2
        
        bonus_calc = config.calculate_daily_amount(future_day, is_wednesday)
        
        upcoming_bonuses.append({
            'day_number': future_day,
            'date': future_date.strftime('%Y-%m-%d'),
            'amount': bonus_calc['final_amount'],
            'is_wednesday': bonus_calc['is_wednesday'],
            'is_special_day': bonus_calc['is_special_day'],
            'multiplier': bonus_calc['multiplier']
        })
    
    return {
        "cycle": cycle.to_dict(),
        "upcoming_bonuses": upcoming_bonuses,
        "progress_percentage": (cycle.current_day / 30) * 100
    }

@router.get("/system-config")
async def get_system_config(current_user: User = Depends(get_current_user)):
    """Get system configuration (public info only)"""
    
    config = KPIBonusConfig.get_config()
    
    return {
        "base_daily_amount": config.base_daily_amount,
        "daily_increment": config.daily_increment,
        "wednesday_multiplier": config.wednesday_multiplier,
        "cycle_length_days": config.cycle_length_days,
        "expiry_hours": config.expiry_hours,
        "max_daily_amount": config.max_daily_amount,
        "is_system_active": config.is_system_active,
        "special_days": [
            {
                "day_number": day["day_number"],
                "name": day["name"],
                "description": day["description"],
                "multiplier": day["multiplier"]
            }
            for day in config.special_days
        ]
    }
