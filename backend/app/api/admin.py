from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from app.core.database import redis_client
from app.models.user import User
from app.models.file import EncryptedFile
from app.models.arcade import UserArcadeProfile
from app.models.collaboration import Collaboration
from app.api.auth import get_op_user
from app.services.email_service import email_service
from app.core.security import generate_otp, verify_password, hash_password
import os
import shutil
from datetime import datetime
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models for timezone configuration
class TimezoneConfigRequest(BaseModel):
    timezone: str = "GMT+7"
    auto_order_enabled: bool = False

class NukeDataRequest(BaseModel):
    dev_key: str
    confirmation: str
    target: str = "ENTIRE_SERVER"
    target_user: Optional[str] = None

class PanicRequest(BaseModel):
    password: str

class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "USER"

class UpdateUserRequest(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None

@router.get("/users")
async def get_users(current_user: User = Depends(get_op_user)):
    """Get all users"""
    users = User.objects.all()
    return [
        {
            "id": str(user.id),
            "username": user.username,
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at.isoformat()
        }
        for user in users
    ]

@router.post("/users")
async def create_user(
    request: CreateUserRequest,
    current_user: User = Depends(get_op_user)
):
    """Create a new user"""
    try:
        # Check if username already exists
        if User.objects(username=request.username).first():
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create new user
        hashed_password = hash_password(request.password)
        user = User(
            username=request.username,
            password_hash=hashed_password,
            role=request.role,
            status="ACTIVE"
        )
        user.save()
        
        return {
            "message": "User created successfully",
            "user_id": str(user.id),
            "username": user.username,
            "role": user.role
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    current_user: User = Depends(get_op_user)
):
    """Update user information"""
    try:
        user = User.objects(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields if provided
        if request.role is not None:
            user.role = request.role
        
        if request.status is not None:
            user.status = request.status
        
        user.save()
        
        return {
            "message": "User updated successfully",
            "user_id": str(user.id),
            "username": user.username
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_op_user)
):
    """Delete a user"""
    try:
        user = User.objects(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent deletion of OP users
        if user.role == "OP":
            raise HTTPException(status_code=400, detail="Cannot delete OP users")
        
        # Prevent self-deletion
        if str(user.id) == str(current_user.id):
            raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
        username = user.username
        user.delete()
        
        return {
            "message": "User deleted successfully",
            "username": username
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

@router.get("/stats/overview")
async def get_overview_stats(current_user: User = Depends(get_op_user)):
    """Get system overview statistics"""
    return {
        "totalUsers": User.objects.count(),
        "activeUsers": User.objects(status='ACTIVE').count()
    }

@router.get("/analytics")
async def get_analytics(current_user: User = Depends(get_op_user)):
    """Get system analytics"""
    return {
        "totalUsers": User.objects.count(),
        "activeUsers": User.objects(status='ACTIVE').count()
    }

@router.get("/status/database")
async def check_database_status(current_user: User = Depends(get_op_user)):
    """Check database connection"""
    try:
        User.objects.first()
        return {"status": "connected"}
    except:
        return {"status": "disconnected"}

@router.get("/status/redis")
async def check_redis_status(current_user: User = Depends(get_op_user)):
    """Check Redis connection"""
    try:
        await redis_client.ping()
        return {"status": "connected"}
    except:
        return {"status": "disconnected"}

@router.post("/panic")
async def panic_button(current_user: User = Depends(get_op_user)):
    """Emergency lockdown - kill sessions and enable maintenance mode"""
    # Kill all sessions by setting maintenance mode
    await redis_client.set("MAINTENANCE", "True", ex=86400)  # 24 hours
    
    # Disable file links
    await redis_client.set("LINKS_DISABLED", "True", ex=86400)
    
    return {"message": "Panic mode activated. All sessions invalidated."}

@router.post("/nuke-data")
async def nuke_data_server(request: NukeDataRequest, current_user: User = Depends(get_op_user)):
    """Total server sanitization - DANGEROUS"""
    from app.core.config import settings

    # Verify OP user Role
    if current_user.role != 'OP':
        raise HTTPException(
            status_code=403,
            detail="Forbidden: OP privileges required"
        )
        
    # Verify DEV_KEY parameter
    if request.dev_key != settings.DEV_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid DEV_KEY authorization"
        )

    # Verify confirmation text
    if request.confirmation != "NUKE_SYSTEM":
        raise HTTPException(
            status_code=400,
            detail="Incorrect confirmation text"
        )
    
    # Execute nuke protocol based on target
    try:
        from app.models.drive import DriveFile, DriveFolder, DriveShare, DriveQuota
        
        if request.target in ["ENTIRE_SERVER", "USERS"]:
            UserArcadeProfile.drop_collection()
            if request.target == "USERS":
                # Only delete non-OP users
                User.objects(role__ne="OP").delete()
            
        if request.target in ["ENTIRE_SERVER", "DRIVE"]:
            if request.target_user:
                target_user_obj = User.objects(username=request.target_user).first()
                if target_user_obj:
                    DriveFile.objects(owner=target_user_obj).delete()
                    DriveFolder.objects(owner=target_user_obj).delete()
                    DriveShare.objects(owner=target_user_obj).delete()
                    # optionally reset quota
                    quota = DriveQuota.objects(user=target_user_obj).first()
                    if quota:
                        quota.used_space = 0
                        quota.save()
            else:
                DriveFile.drop_collection()
                DriveFolder.drop_collection()
                DriveShare.drop_collection()
                DriveQuota.drop_collection()
                EncryptedFile.drop_collection()
            
            # Clear file system - entirely if no target_user, though granular file OS delete skips OS wiping for granular user
            if not request.target_user:
                from app.core.storage import storage_service
                for storage_path in storage_service.get_all_storage_paths():
                    storage_paths = [
                        os.path.join(storage_path, "uploads"),
                        os.path.join(storage_path, "safe"), 
                        os.path.join(storage_path, "temp_chat"),
                        os.path.join(storage_path, "DHQ_Root/Drive")
                    ]
                    for path in storage_paths:
                        if os.path.exists(path):
                            shutil.rmtree(path)
                            os.makedirs(path, exist_ok=True)
            
        if request.target in ["ENTIRE_SERVER", "COLLABORATION"]:
            Collaboration.drop_collection()
            
        if request.target in ["ENTIRE_SERVER", "ORDER"]:
            try:
                from app.models.growth_order import GrowthOrder, SubOrder
                GrowthOrder.drop_collection()
                SubOrder.drop_collection()
            except: pass
            
            try:
                from app.models.order import Order
                Order.drop_collection()
            except: pass
            
        if request.target == "ENTIRE_SERVER":
            # Wipe all Users
            User.drop_collection()
            
            # 3. Clean redis specific queues (except critical states)
            keys_to_keep = ["MAINTENANCE", "LINKS_DISABLED", "admin:timezone_config"]
            all_keys = await redis_client.keys("*")
            for key in all_keys:
                if isinstance(key, bytes):
                    key_str = key.decode("utf-8")
                else:
                    key_str = str(key)
                if key_str not in keys_to_keep:
                    await redis_client.delete(key)
                    
            # 4. Re-init OP User to prevent lockout
            import sys
            import subprocess
            try:
                # Use subprocess to run init_op.py independently to avoid import loops if any
                subprocess.run([sys.executable, "/home/haku/projects/DHQ_Root/backend/init_op.py"], check=True)
                logger.info("OP User recreated successfully during ENTIRE_SERVER wipe")
            except Exception as e:
                logger.error(f"Failed to recreate OP user: {e}")
        
        return {"message": f"Nuke protocol for target '{request.target}' completed successfully."}
        
    except Exception as e:
        logger.error(f"Nuke failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Nuke protocol failed: {str(e)}"
        )


@router.post("/maintenance-off")
async def disable_maintenance(current_user: User = Depends(get_op_user)):
    """Disable maintenance mode"""
    await redis_client.delete("MAINTENANCE")
    await redis_client.delete("LINKS_DISABLED")
    return {"message": "Maintenance mode disabled"}

@router.post("/initialize-data")
async def initialize_data(current_user: User = Depends(get_op_user)):
    """Initialize system with sample data (OP only)"""
    
    try:
        # Create sample shop items
        sample_items = [
            {
                "name": "Golden Avatar Frame",
                "type": "Avatar Frame",
                "rarity": "LEGENDARY",
                "price": 500,
                "description": "A stunning golden frame for your avatar",
                "asset_url": "/assets/shop/golden_avatar_frame.png",
                "is_limited": True,
                "stock_quantity": 10,
                "requirements": {"level": 5, "kpi_required": 200},
                "tags": ["avatar", "premium", "golden"]
            },
            {
                "name": "Diamond Banner",
                "type": "Banner Frame",
                "rarity": "EPIC",
                "price": 300,
                "description": "Sparkling diamond banner frame",
                "asset_url": "/assets/shop/diamond_banner.png",
                "is_limited": True,
                "stock_quantity": 25,
                "requirements": {"level": 3, "kpi_required": 100},
                "tags": ["banner", "diamond", "premium"]
            },
            {
                "name": "Fire Avatar",
                "type": "Animated Avatar",
                "rarity": "EPIC",
                "price": 400,
                "description": "Animated fire effect for your avatar",
                "asset_url": "/assets/shop/fire_avatar.gif",
                "is_limited": False,
                "stock_quantity": 0,
                "requirements": {"level": 4, "kpi_required": 150},
                "tags": ["avatar", "animated", "fire"]
            },
            {
                "name": "Elite Role",
                "type": "Role",
                "rarity": "RARE",
                "price": 200,
                "description": "Elite user role with special permissions",
                "asset_url": "/assets/shop/elite_role.png",
                "is_limited": False,
                "stock_quantity": 0,
                "requirements": {"level": 2, "kpi_required": 50},
                "tags": ["role", "elite", "permission"]
            },
            {
                "name": "Chat Badge Pro",
                "type": "Chat Badge",
                "rarity": "COMMON",
                "price": 50,
                "description": "Professional chat badge",
                "asset_url": "/assets/shop/chat_badge_pro.png",
                "is_limited": False,
                "stock_quantity": 0,
                "requirements": {"level": 1, "kpi_required": 10},
                "tags": ["chat", "badge", "common"]
            },
            {
                "name": "Speed Boost",
                "type": "Effect",
                "rarity": "RARE",
                "price": 150,
                "description": "2x KPI earning speed for 1 hour",
                "asset_url": "/assets/shop/speed_boost.png",
                "is_limited": False,
                "stock_quantity": 0,
                "requirements": {"level": 2, "kpi_required": 30},
                "tags": ["effect", "boost", "speed"]
            }
        ]
        
        created_items = []
        for item_data in sample_items:
            from app.models.shop import ShopItem
            existing = ShopItem.objects(name=item_data["name"]).first()
            if not existing:
                item = ShopItem(**item_data)
                item.save()
                created_items.append(item_data["name"])
        
        # Create arcade profile for current user if not exists
        from app.models.arcade import UserArcadeProfile
        existing_profile = UserArcadeProfile.objects(user=current_user).first()
        if not existing_profile:
            profile = UserArcadeProfile(
                user=current_user,
                kpi_balance=1000,
                total_kpi_earned=1000,
                kpi_spent=0,
                level=3,
                experience_points=500,
                games_played=10,
                achievements_unlocked=5,
                login_streak=3,
                last_login=datetime.utcnow()
            )
            profile.save()
            created_profile = True
        else:
            created_profile = False
        
        return {
            "message": "Data initialization completed",
            "created_items": created_items,
            "created_profile": created_profile,
            "total_items": len(created_items)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

# Timezone Configuration Endpoints
@router.get("/timezone-config")
async def get_timezone_config(current_user: User = Depends(get_op_user)):
    """Get current timezone configuration"""
    if not current_user or current_user.role != 'OP':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get from Redis or use default
    try:
        config = await redis_client.hgetall("admin:timezone_config")
        if not config:
            config = {"timezone": "GMT+7", "auto_order_enabled": True}
        
        return JSONResponse({
            "success": True,
            "config": {
                "timezone": config.get("timezone", "GMT+7"),
                "auto_order_enabled": config.get("auto_order_enabled", True)
            }
        })
    except Exception as e:
        logger.error(f"Error loading timezone config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load timezone config: {str(e)}")

@router.post("/timezone-config")
async def update_timezone_config(
    request: TimezoneConfigRequest,
    current_user: User = Depends(get_op_user)
):
    """Update timezone configuration"""
    if not current_user or current_user.role != 'OP':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Store in Redis
        await redis_client.hset("admin:timezone_config", "timezone", request.timezone)
        await redis_client.hset("admin:timezone_config", "auto_order_enabled", request.auto_order_enabled)
        
        logger.info(f"Timezone config updated by {current_user.username}: {request.timezone}, auto_order: {request.auto_order_enabled}")
        
        return JSONResponse({
            "success": True,
            "message": "Timezone configuration updated successfully"
        })
    except Exception as e:
        logger.error(f"Error updating timezone config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update timezone config: {str(e)}")

@router.post("/auto-order-toggle")
async def toggle_auto_order(
    enabled: bool,
    current_user: User = Depends(get_op_user)
):
    """Toggle auto-order placement"""
    if not current_user or current_user.role != 'OP':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        await redis_client.hset("admin:timezone_config", "auto_order_enabled", enabled)
        await redis_client.hset("admin:timezone_config", "auto_order_active", str(enabled))
        await redis_client.hset("admin:timezone_config", "last_check", datetime.utcnow().isoformat())
        
        logger.info(f"Auto-order {'enabled' if enabled else 'disabled'} by {current_user.username}")
        
        return JSONResponse({
            "success": True,
            "active": enabled,
            "message": f"Auto-order placement {'enabled' if enabled else 'disabled'}"
        })
    except Exception as e:
        logger.error(f"Error toggling auto-order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to toggle auto-order: {str(e)}")

@router.get("/auto-order-status")
async def get_auto_order_status(current_user: User = Depends(get_op_user)):
    """Get current auto-order status"""
    if not current_user or current_user.role != 'OP':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get from Redis
    try:
        auto_order_enabled = await redis_client.hget("admin:timezone_config", "auto_order_enabled")
        auto_order_active = await redis_client.hget("admin:timezone_config", "auto_order_active")
        
        return JSONResponse({
            "success": True,
            "active": auto_order_active == "True",
            "last_check": await redis_client.hget("admin:timezone_config", "last_check")
        })
    except Exception as e:
        logger.error(f"Error getting auto-order status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get auto-order status: {str(e)}")

@router.post("/test-auto-order")
async def test_auto_order(current_user: User = Depends(get_op_user)):
    """Test auto-order placement functionality"""
    if not current_user or current_user.role != 'OP':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from app.services.auto_order_service import auto_order_service
        
        # Get current status
        status = await auto_order_service.get_status()
        
        # Count pending sub-orders
        from app.models.growth_order import GrowthOrder, SubOrder
        from datetime import datetime
        
        current_time = datetime.utcnow()
        pending_sub_orders = SubOrder.objects(
            status="Pending",
            scheduled_time__lte=current_time
        )
        
        pending_count = len(pending_sub_orders)
        
        logger.info(f"Auto-order test found {pending_count} pending sub-orders ready for auto-placement")
        
        return JSONResponse({
            "success": True,
            "message": f"Test completed. Found {pending_count} pending sub-orders ready for auto-placement.",
            "pending_count": pending_count,
            "service_status": status
        })
    except Exception as e:
        logger.error(f"Error testing auto-order: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to test auto-order: {str(e)}")
