from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from app.models.user import User
from app.models.kpi import KPIHistory
from app.models.arcade import (
    UserArcadeProfile, ShopItemDefinition, AchievementDefinition, UserKPIHistory, LeaderboardEntry, DailyBonusConfig
)
from app.models.shop import ShopItem, UserPurchase
from app.api.auth import get_current_user, get_op_user
from typing import List, Optional
from datetime import datetime, timedelta
from app.services.achievements import check_theme_unlocks

router = APIRouter()

# Pydantic models
class GameSessionRequest(BaseModel):
    game_type: str
    score: int
    duration_seconds: int
    difficulty: str = "MEDIUM"

class StartGameRequest(BaseModel):
    game_type: str
    difficulty: str = "MEDIUM"

class PurchaseItemRequest(BaseModel):
    item_id: str

# Profile endpoints
@router.get("/profile")
async def get_arcade_profile(
    current_user: User = Depends(get_current_user)
):
    """Get user's arcade profile"""
    
    profile = UserArcadeProfile.objects(user=current_user).first()
    if not profile:
        # Create profile if it doesn't exist
        profile = UserArcadeProfile(user=current_user)
        profile.save()
    
    return profile.to_dict()

# Shop endpoints
@router.get("/shop/items")
async def get_shop_items(
    item_type: Optional[str] = None,
    rarity: Optional[str] = None
):
    """Get available shop items"""
    
    query = ShopItem.objects(is_active=True)
    
    if item_type:
        query = query.filter(item_type=item_type)
    
    if rarity:
        query = query.filter(rarity=rarity)
    
    items = []
    now = datetime.utcnow()
    
    for item in query:
        # Check if item is currently available
        if item.available_start and item.available_start > now:
            continue
        if item.available_end and item.available_end < now:
            continue
            
        # Check if item is in stock (for limited items)
        if item.is_limited and item.stock_quantity <= 0:
            continue
            
        # Calculate current price
        current_price = item.price
        if item.sale_price and item.sale_end and item.sale_end > now:
            current_price = item.sale_price
            
        item_data = {
            'id': str(item.id),
            'name': item.name,
            'description': item.description,
            'price': current_price,
            'original_price': item.price,
            'item_type': item.item_type,
            'icon': item.icon,
            'rarity': item.rarity,
            'sale_end': item.sale_end.isoformat() if item.sale_end else None,
            'available_start': item.available_start.isoformat() if item.available_start else None,
            'available_end': item.available_end.isoformat() if item.available_end else None,
            'is_limited': item.is_limited,
            'stock_quantity': item.stock_quantity,
            'requirements': item.requirements,
            'tags': item.tags,
            'created_at': item.created_at.isoformat()
        }
        
        if item.effect_type:
            item_data['effect_type'] = item.effect_type
            item_data['effect_value'] = item.effect_value
            item_data['effect_duration_hours'] = item.effect_duration_hours
        
        items.append(item_data)
    
    return {
        "items": items,
        "total": len(items)
    }

@router.post("/shop/purchase/{item_id}")
async def purchase_item(
    item_id: str,
    current_user: User = Depends(get_current_user)
):
    """Purchase an item from the shop"""
    item = ShopItem.objects(id=item_id, is_active=True).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check availability
    now = datetime.utcnow()
    if item.available_start and item.available_start > now:
        raise HTTPException(status_code=400, detail="Item not yet available")
    if item.available_end and item.available_end < now:
        raise HTTPException(status_code=400, detail="Item no longer available")
    
    # Check stock
    if item.is_limited and item.stock_quantity <= 0:
        raise HTTPException(status_code=400, detail="Item out of stock")
    
    # Check if already owned
    existing_purchase = UserPurchase.objects(
        user_id=str(current_user.id), 
        item_id=item_id, 
        is_active=True
    ).first()
    if existing_purchase:
        raise HTTPException(status_code=400, detail="Item already owned")
    
    # Calculate price
    current_price = item.price
    if item.sale_price and item.sale_start and item.sale_end:
        if item.sale_start <= now <= item.sale_end:
            current_price = item.sale_price
    
    # Check KPI balance
    if current_user.kpi_current < current_price:
        raise HTTPException(status_code=400, detail="Insufficient KPI points")
    
    # Check requirements
    if item.requirements:
        if "kpi_required" in item.requirements:
            if current_user.kpi_current < item.requirements["kpi_required"]:
                raise HTTPException(status_code=400, detail="KPI requirement not met")
    
    # Process purchase
    current_user.kpi_current -= current_price
    current_user.save()
    
    # Create purchase record
    purchase = UserPurchase(
        user_id=str(current_user.id),
        item_id=item_id,
        item_name=item.name,
        item_type=item.type,
        price_paid=current_price,
        metadata={"asset_url": item.asset_url}
    )
    purchase.save()
    
    # Update stock for limited items
    if item.is_limited:
        item.stock_quantity -= 1
        item.save()
    
    # Create KPI history
    KPIHistory(
        user=current_user,
        amount=-current_price,
        balance_after=current_user.kpi_current,
        source="shop_purchase",
        reason=f"Purchased {item.name}"
    ).save()
    
    return {
        "message": "Item purchased successfully!",
        "item": {
            "id": str(item.id),
            "name": item.name,
            "type": item.type,
            "asset_url": item.asset_url
        },
        "price_paid": current_price,
        "new_balance": current_user.kpi_current
    }

@router.get("/shop/inventory")
async def get_user_inventory(current_user: User = Depends(get_current_user)):
    """Get user's purchased items"""
    purchases = UserPurchase.objects(user_id=str(current_user.id), is_active=True).order_by('-purchased_at')
    
    items = []
    for purchase in purchases:
        # Get item details
        item = ShopItem.objects(id=purchase.item_id).first()
        if item:
            items.append({
                "purchase_id": str(purchase.id),
                "item_id": str(item.id),
                "name": purchase.item_name,
                "type": purchase.item_type,
                "asset_url": purchase.metadata.get("asset_url"),
                "price_paid": purchase.price_paid,
                "purchased_at": purchase.purchased_at.isoformat(),
                "is_active": purchase.is_active
            })
    
    return {"items": items}
class CreateShopItemRequest(BaseModel):
    name: str
    description: str
    cost_kpi: int
    item_type: str
    icon: str = "🎁"
    rarity: str = "COMMON"
    effect_type: Optional[str] = None
    effect_value: Optional[str] = None
    effect_duration_hours: Optional[int] = None
    is_limited: bool = False
    current_stock: Optional[int] = None

class UpdateShopItemRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cost_kpi: Optional[int] = None
    item_type: Optional[str] = None
    icon: Optional[str] = None
    rarity: Optional[str] = None
    effect_type: Optional[str] = None
    effect_value: Optional[str] = None
    effect_duration_hours: Optional[int] = None
    is_limited: Optional[bool] = None
    current_stock: Optional[int] = None
    is_active: Optional[bool] = None

@router.post("/shop/items")
async def create_shop_item(
    request: CreateShopItemRequest,
    current_user: User = Depends(get_op_user)
):
    """Create a new shop item (OP only)"""
    
    item = ShopItemDefinition(
        name=request.name,
        description=request.description,
        cost_kpi=request.cost_kpi,
        item_type=request.item_type,
        icon=request.icon,
        rarity=request.rarity,
        effect_type=request.effect_type,
        effect_value=request.effect_value,
        effect_duration_hours=request.effect_duration_hours,
        is_limited=request.is_limited,
        current_stock=request.current_stock if request.is_limited else None
    )
    item.save()
    
    return {
        "message": "Shop item created successfully!",
        "item": {
            "id": str(item.id),
            "name": item.name,
            "description": item.description,
            "cost_kpi": item.cost_kpi,
            "item_type": item.item_type,
            "icon": item.icon,
            "rarity": item.rarity
        }
    }

@router.put("/shop/items/{item_id}")
async def update_shop_item(
    item_id: str,
    request: UpdateShopItemRequest,
    current_user: User = Depends(get_op_user)
):
    """Update an existing shop item (OP only)"""
    
    item = ShopItemDefinition.objects(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Shop item not found")
    
    # Update fields that are provided
    if request.name is not None:
        item.name = request.name
    if request.description is not None:
        item.description = request.description
    if request.cost_kpi is not None:
        item.cost_kpi = request.cost_kpi
    if request.item_type is not None:
        item.item_type = request.item_type
    if request.icon is not None:
        item.icon = request.icon
    if request.rarity is not None:
        item.rarity = request.rarity
    if request.effect_type is not None:
        item.effect_type = request.effect_type
    if request.effect_value is not None:
        item.effect_value = request.effect_value
    if request.effect_duration_hours is not None:
        item.effect_duration_hours = request.effect_duration_hours
    if request.is_limited is not None:
        item.is_limited = request.is_limited
    if request.current_stock is not None:
        item.current_stock = request.current_stock
    if request.is_active is not None:
        item.is_active = request.is_active
    
    item.save()
    
    return {
        "message": "Shop item updated successfully!",
        "item": item.to_dict()
    }

@router.delete("/shop/items/{item_id}")
async def delete_shop_item(
    item_id: str,
    current_user: User = Depends(get_op_user)
):
    """Delete a shop item (OP only)"""
    
    item = ShopItemDefinition.objects(id=item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Shop item not found")
    
    item_name = item.name
    item.delete()
    
    return {
        "message": f"Shop item '{item_name}' deleted successfully!"
    }

# Gaming endpoints
@router.post("/games/start")
async def start_game(
    request: StartGameRequest,
    current_user: User = Depends(get_current_user)
):
    """Start a game session (costs KPI points)"""
    
    # Calculate cost based on difficulty
    difficulty_costs = {'EASY': 2, 'MEDIUM': 5, 'HARD': 10, 'EXTREME': 20}
    game_cost = difficulty_costs.get(request.difficulty, 5)
    
    # Check if user has enough KPI
    if current_user.kpi_current < game_cost:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient KPI points. Need {game_cost} KPI to play {request.difficulty} difficulty."
        )
    
    # Deduct KPI cost
    current_user.kpi_current -= game_cost
    current_user.save()
    
    # Create KPI history entry for cost
    KPIHistory(
        user=current_user,
        amount=-game_cost,
        balance_after=current_user.kpi_current,
        source="game_cost",
        reason=f"Started {request.game_type} ({request.difficulty} difficulty)"
    ).save()
    
    return {
        "message": "Game started!",
        "game_type": request.game_type,
        "difficulty": request.difficulty,
        "kpi_cost": game_cost,
        "new_balance": current_user.kpi_current
    }

@router.post("/games/session")
async def submit_game_session(
    request: GameSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """Submit a gaming session"""
    
    # Calculate KPI earned based on performance
    base_kpi = 10
    difficulty_multiplier = {'EASY': 0.5, 'MEDIUM': 1.0, 'HARD': 1.5, 'EXTREME': 2.0}
    score_multiplier = min(request.score / 1000, 5.0)  # Cap at 5x multiplier
    
    kpi_earned = int(base_kpi * difficulty_multiplier.get(request.difficulty, 1.0) * score_multiplier)
    
    # Create game session
    session = GameSession(
        user=current_user,
        game_type=request.game_type,
        score=request.score,
        kpi_earned=kpi_earned,
        duration_seconds=request.duration_seconds,
        difficulty=request.difficulty
    )
    session.save()
    
    # Award KPI to user
    current_user.kpi_current += kpi_earned
    current_user.kpi_lifetime += kpi_earned
    current_user.save()
    
    # Create KPI history entry for earnings
    KPIHistory(
        user=current_user,
        amount=kpi_earned,
        balance_after=current_user.kpi_current,
        source="game_win",
        reason=f"Completed {request.game_type} (score: {request.score}, difficulty: {request.difficulty})",
        related_entity_type="game",
        related_entity_id=str(session.id)
    ).save()
    
    # Update user profile
    profile = UserArcadeProfile.objects(user=current_user).first()
    if not profile:
        profile = UserArcadeProfile(user=current_user)
        profile.save()
    
    profile.games_played += 1
    profile.total_game_time += request.duration_seconds
    profile.add_kpi(kpi_earned, 'GAME', str(session.id), f"Played {request.game_type}")
    profile.save()
    
    # Update leaderboards
    update_leaderboard(current_user, request.game_type, request.score, kpi_earned)
    
    # Check for theme unlocks
    check_theme_unlocks(current_user, profile)
    
    return {
        "message": "Game session recorded!",
        "kpi_earned": kpi_earned,
        "new_balance": current_user.kpi_current,
        "games_played": profile.games_played
    }

@router.get("/games/leaderboard")
async def get_leaderboard(
    game_type: Optional[str] = None,
    period_type: str = "ALL_TIME",
    limit: int = 10
):
    """Get leaderboard entries"""
    
    query = LeaderboardEntry.objects(period_type=period_type)
    
    if game_type:
        query = query.filter(game_type=game_type)
    
    # Get top entries
    entries = query.order_by('-score').limit(limit)
    
    leaderboard = []
    for rank, entry in enumerate(entries, 1):
        leaderboard.append({
            'rank': rank,
            'user': {
                'id': str(entry.user.id),
                'username': entry.user.username,
                'display_name': entry.user.display_name
            },
            'score': entry.score,
            'kpi_earned': entry.kpi_earned,
            'game_type': entry.game_type,
            'achieved_at': entry.achieved_at.isoformat()
        })
    
    return leaderboard

# Achievements endpoints
@router.get("/achievements")
async def get_achievements(
    current_user: User = Depends(get_current_user)
):
    """Get user's achievements"""
    
    profile = UserArcadeProfile.objects(user=current_user).first()
    if not profile:
        profile = UserArcadeProfile(user=current_user)
        profile.save()
    
    # Get all achievement definitions
    all_achievements = AchievementDefinition.objects(is_active=True)
    
    # Mark which ones are unlocked
    unlocked_ids = [ach.achievement_id for ach in profile.achievements]
    
    achievements = []
    for ach_def in all_achievements:
        is_unlocked = str(ach_def.id) in unlocked_ids
        user_ach = None
        
        if is_unlocked:
            user_ach = next((a for a in profile.achievements if a.achievement_id == str(ach_def.id)), None)
        
        achievement_data = {
            'id': str(ach_def.id),
            'name': ach_def.name,
            'description': ach_def.description,
            'icon': ach_def.icon,
            'points_awarded': ach_def.points_awarded,
            'achievement_type': ach_def.achievement_type,
            'is_unlocked': is_unlocked,
            'is_hidden': ach_def.is_hidden and not is_unlocked
        }
        
        if user_ach:
            achievement_data['unlocked_at'] = user_ach.unlocked_at.isoformat()
        
        # Add progress information
        progress = calculate_achievement_progress(current_user, ach_def)
        achievement_data['progress'] = progress
        
        achievements.append(achievement_data)
    
    return achievements

@router.get("/achievements/definitions")
async def get_achievement_definitions():
    """Get all achievement definitions"""
    
    achievements = AchievementDefinition.objects(is_active=True)
    
    return [
        {
            'id': str(ach.id),
            'name': ach.name,
            'description': ach.description,
            'icon': ach.icon,
            'points_awarded': ach.points_awarded,
            'achievement_type': ach.achievement_type,
            'criteria_field': ach.criteria_field,
            'criteria_value': ach.criteria_value,
            'is_hidden': ach.is_hidden
        }
        for ach in achievements
    ]

# KPI History endpoints
@router.get("/kpi/history")
async def get_kpi_history(
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    source_type: Optional[str] = None
):
    """Get user's KPI earning history"""
    
    query = UserKPIHistory.objects(user=current_user)
    
    if source_type:
        query = query.filter(source_type=source_type)
    
    history = query.order_by('-timestamp').limit(limit)
    
    return [
        {
            'id': str(entry.id),
            'kpi_amount': entry.kpi_amount,
            'source_type': entry.source_type,
            'source_id': entry.source_id,
            'description': entry.description,
            'timestamp': entry.timestamp.isoformat()
        }
        for entry in history
    ]

# Utility functions
def update_leaderboard(user: User, game_type: str, score: int, kpi_earned: int):
    """Update leaderboard entries"""
    
    # Update all-time leaderboard
    existing = LeaderboardEntry.objects(
        user=user, 
        game_type=game_type, 
        period_type='ALL_TIME'
    ).first()
    
    if existing and score > existing.score:
        existing.score = score
        existing.kpi_earned = kpi_earned
        existing.achieved_at = datetime.utcnow()
        existing.save()
    elif not existing:
        entry = LeaderboardEntry(
            user=user,
            game_type=game_type,
            score=score,
            kpi_earned=kpi_earned,
            period_type='ALL_TIME'
        )
        entry.save()

def calculate_achievement_progress(user: User, achievement: AchievementDefinition) -> dict:
    """Calculate progress towards an achievement"""
    
    profile = UserArcadeProfile.objects(user=user).first()
    if not profile:
        return {'current': 0, 'target': achievement.criteria_value, 'percentage': 0}
    
    current_value = 0
    
    if achievement.criteria_field == 'login_streak':
        current_value = profile.login_streak
    elif achievement.criteria_field == 'games_played':
        current_value = profile.games_played
    elif achievement.criteria_field == 'kpi_balance':
        current_value = profile.kpi_balance
    
    percentage = min(100, int((current_value / achievement.criteria_value) * 100))
    
    return {
        'current': current_value,
        'target': achievement.criteria_value,
        'percentage': percentage
    }

