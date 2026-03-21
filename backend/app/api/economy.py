from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.models.arcade import UserArcadeProfile
from app.models.kpi import KPIHistory
from app.api.auth import get_current_user

router = APIRouter()

class ConversionPackage(BaseModel):
    package_id: str
    source_type: Optional[str] = None # kpi, chips, api_dollar

class CartItem(BaseModel):
    item_id: str
    quantity: int = 1
    source_type: str # kpi, chips, api_dollar

class CheckoutRequest(BaseModel):
    items: list[CartItem]

@router.post("/convert")
async def convert_kpi_to_chips(
    package: ConversionPackage,
    current_user: User = Depends(get_current_user)
):
    """Convert KPI to Chips using package deals"""
    packages = {
        # KPI to Chips (Existing)
        "basic": {"from": "kpi", "to": "chips", "amount_from": 5, "amount_to": 5000, "label": "5,000 Chips"},
        "bonus_10": {"from": "kpi", "to": "chips", "amount_from": 50, "amount_to": 55000, "label": "55,000 Chips (10% Bonus)"},
        "bonus_20": {"from": "kpi", "to": "chips", "amount_from": 500, "amount_to": 600000, "label": "600,000 Chips (20% Bonus)"},
        "mega_50": {"from": "kpi", "to": "chips", "amount_from": 5000, "amount_to": 7500000, "label": "7,500,000 Chips (50% Bonus)"},
        
        # KPI to API$
        "kpi_to_api_1": {"from": "kpi", "to": "api_dollar", "amount_from": 1, "amount_to": 1.0, "label": "1.00 API$"},
        "kpi_to_api_5": {"from": "kpi", "to": "api_dollar", "amount_from": 5, "amount_to": 5.0, "label": "5.00 API$"},
        "kpi_to_api_10": {"from": "kpi", "to": "api_dollar", "amount_from": 10, "amount_to": 10.0, "label": "10.00 API$"},
        "kpi_to_api_50": {"from": "kpi", "to": "api_dollar", "amount_from": 50, "amount_to": 50.0, "label": "50.00 API$"},
        "kpi_to_api_100": {"from": "kpi", "to": "api_dollar", "amount_from": 100, "amount_to": 100.0, "label": "100.00 API$"},
        "kpi_to_api_500": {"from": "kpi", "to": "api_dollar", "amount_from": 500, "amount_to": 500.0, "label": "500.00 API$"},
        
        # Chips to API$ (Retained for backwards compatibility or direct use)
        "chips_to_api_1": {"from": "chips", "to": "api_dollar", "amount_from": 1000, "amount_to": 1.0, "label": "1.00 API$"},
        "chips_to_api_10": {"from": "chips", "to": "api_dollar", "amount_from": 10000, "amount_to": 10.0, "label": "10.00 API$"},
        
        # API$ to Chips
        "api_to_chips_1": {"from": "api_dollar", "to": "chips", "amount_from": 1.0, "amount_to": 1000, "label": "1,000 Chips"},
        "api_to_chips_10": {"from": "api_dollar", "to": "chips", "amount_from": 10.0, "amount_to": 10000, "label": "10,000 Chips"},
    }
    
    print(f"DEBUG: Conversion request for package {package.package_id} from {package.source_type}")
    pkg = packages.get(package.package_id)
    if not pkg:
        print(f"DEBUG: Invalid package: {package.package_id}")
        raise HTTPException(status_code=400, detail=f"Invalid package: {package.package_id}")
        
    # Override source type if provided (for API$ conversion packs)
    source_type = package.source_type or pkg["from"]
    amount_from = pkg["amount_from"]
    
    # If source was overridden (e.g. from KPI to Chips for an API$ package), recalculate amount
    if package.source_type and package.source_type != pkg["from"]:
        if pkg["from"] == "kpi" and package.source_type == "chips":
            # If original was 1 KPI = 1 API$, then for Chips it's 1000 Chips = 1 API$
            # We assume a fixed rate for flexible packs: 1 KPI = 1000 Chips
            amount_from = pkg["amount_from"] * 1000
        elif pkg["from"] == "chips" and package.source_type == "kpi":
            amount_from = pkg["amount_from"] / 1000

    profile = UserArcadeProfile.objects(user=current_user).first()
    if not profile:
        profile = UserArcadeProfile(user=current_user).save()
        
    print(f"DEBUG: Processing {source_type} conversion. Need {amount_from}, Have: KPI={current_user.kpi_current}, Chips={profile.chip_balance}, API$={profile.api_dollar_balance}")
    
    # Check balance based on source type
    if source_type == "kpi":
        if current_user.kpi_current < amount_from:
            raise HTTPException(status_code=400, detail=f"Insufficient KPI balance (Need {amount_from}, have {current_user.kpi_current})")
        current_user.kpi_current -= amount_from
        current_user.save()
    elif source_type == "chips":
        if profile.chip_balance < amount_from:
            raise HTTPException(status_code=400, detail=f"Insufficient Chips balance (Need {amount_from}, have {profile.chip_balance})")
        profile.chip_balance -= amount_from
    elif source_type == "api_dollar":
        if profile.api_dollar_balance < amount_from:
            raise HTTPException(status_code=400, detail=f"Insufficient API$ balance (Need {amount_from}, have {profile.api_dollar_balance})")
        profile.api_dollar_balance -= amount_from
        
    # Process target conversion
    target_type = pkg["to"]
    if target_type == "chips":
        profile.add_chips(pkg["amount_to"])
    elif target_type == "api_dollar":
        profile.add_api_dollars(pkg["amount_to"])
    
    profile.save()
    
    # Track history if KPI was involved
    if source_type == "kpi":
        KPIHistory(
            user=current_user,
            amount=-amount_from,
            balance_after=current_user.kpi_current,
            source="shop_conversion",
            reason=f"Converted to {pkg['label']}"
        ).save()
    
    return {
        "message": f"Successfully converted {amount_from} {source_type.upper()} to {pkg['label']}",
        "new_balance": current_user.kpi_current,
        "new_chips": profile.chip_balance,
        "new_api_dollars": profile.api_dollar_balance
    }

@router.post("/checkout")
async def checkout(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user)
):
    """Process multiple items in a single transaction"""
    packages = {
        # KPI to Chips
        "basic": {"from": "kpi", "to": "chips", "amount_from": 5, "amount_to": 5000, "label": "5,000 Chips"},
        "bonus_10": {"from": "kpi", "to": "chips", "amount_from": 50, "amount_to": 55000, "label": "55,000 Chips (10% Bonus)"},
        "bonus_20": {"from": "kpi", "to": "chips", "amount_from": 500, "amount_to": 600000, "label": "600,000 Chips (20% Bonus)"},
        "mega_50": {"from": "kpi", "to": "chips", "amount_from": 5000, "amount_to": 7500000, "label": "7,500,000 Chips (50% Bonus)"},
        
        # KPI to API$
        "kpi_to_api_1": {"from": "kpi", "to": "api_dollar", "amount_from": 1, "amount_to": 1.0, "label": "1.00 API$"},
        "kpi_to_api_5": {"from": "kpi", "to": "api_dollar", "amount_from": 5, "amount_to": 5.0, "label": "5.00 API$"},
        "kpi_to_api_10": {"from": "kpi", "to": "api_dollar", "amount_from": 10, "amount_to": 10.0, "label": "10.00 API$"},
        "kpi_to_api_50": {"from": "kpi", "to": "api_dollar", "amount_from": 50, "amount_to": 50.0, "label": "50.00 API$"},
        "kpi_to_api_100": {"from": "kpi", "to": "api_dollar", "amount_from": 100, "amount_to": 100.0, "label": "100.00 API$"},
        "kpi_to_api_500": {"from": "kpi", "to": "api_dollar", "amount_from": 500, "amount_to": 500.0, "label": "500.00 API$"},
        
        # Chips to API$
        "chips_to_api_1": {"from": "chips", "to": "api_dollar", "amount_from": 1000, "amount_to": 1.0, "label": "1.00 API$"},
        "chips_to_api_10": {"from": "chips", "to": "api_dollar", "amount_from": 10000, "amount_to": 10.0, "label": "10.00 API$"},
        
        # API$ to Chips
        "api_to_chips_1": {"from": "api_dollar", "to": "chips", "amount_from": 1.0, "amount_to": 1000, "label": "1,000 Chips"},
        "api_to_chips_10": {"from": "api_dollar", "to": "chips", "amount_from": 10.0, "amount_to": 10000, "label": "10,000 Chips"},
    }

    profile = UserArcadeProfile.objects(user=current_user).first()
    if not profile:
        profile = UserArcadeProfile(user=current_user).save()

    total_kpi = 0
    total_chips = 0
    total_api_dollars = 0
    
    award_chips = 0
    award_api_dollars = 0
    
    summary = []
    
    for item in request.items:
        pkg = packages.get(item.item_id)
        if not pkg:
            # Check for non-package items (frames etc) - for now just mock or error if ID starts with num
            if item.item_id.isdigit():
                # Mocking frame purchase with ID 1
                cost = 500 if item.item_id == "1" else 100
                total_kpi += cost * item.quantity
                summary.append(f"{item.quantity}x Item #{item.item_id}")
                continue
            raise HTTPException(status_code=400, detail=f"Invalid item in cart: {item.item_id}")
        
        source = item.source_type
        amount_from = pkg["amount_from"]
        
        # Recalculate if source overridden (like in /convert)
        if source != pkg["from"]:
            if pkg["from"] == "kpi" and source == "chips":
                amount_from = pkg["amount_from"] * 1000
            elif pkg["from"] == "chips" and source == "kpi":
                amount_from = pkg["amount_from"] / 1000
        
        total_cost = amount_from * item.quantity
        if source == "kpi":
            total_kpi += total_cost
        elif source == "chips":
            total_chips += total_cost
        elif source == "api_dollar":
            total_api_dollars += total_cost
            
        # Target awards
        if pkg["to"] == "chips":
            award_chips += pkg["amount_to"] * item.quantity
        elif pkg["to"] == "api_dollar":
            award_api_dollars += pkg["amount_to"] * item.quantity
            
        summary.append(f"{item.quantity}x {pkg['label']}")

    # Check all balances
    if current_user.kpi_current < total_kpi:
        raise HTTPException(status_code=400, detail=f"Insufficient KPI (Need {total_kpi}, have {current_user.kpi_current})")
    if profile.chip_balance < total_chips:
        raise HTTPException(status_code=400, detail=f"Insufficient Chips (Need {total_chips}, have {profile.chip_balance})")
    if profile.api_dollar_balance < total_api_dollars:
        raise HTTPException(status_code=400, detail=f"Insufficient API$ (Need {total_api_dollars}, have {profile.api_dollar_balance})")

    # Deduct and award
    if total_kpi > 0:
        current_user.kpi_current -= total_kpi
        current_user.save()
        KPIHistory(
            user=current_user,
            amount=-total_kpi,
            balance_after=current_user.kpi_current,
            source="shop_checkout",
            reason=f"Checkout: {', '.join(summary[:3])}{'...' if len(summary)>3 else ''}"
        ).save()

    profile.chip_balance -= total_chips
    profile.api_dollar_balance -= total_api_dollars
    
    profile.add_chips(award_chips)
    profile.add_api_dollars(award_api_dollars)
    profile.save()

    return {
        "message": "Checkout successful!",
        "summary": summary,
        "new_balance": current_user.kpi_current,
        "new_chips": profile.chip_balance,
        "new_api_dollars": profile.api_dollar_balance
    }
