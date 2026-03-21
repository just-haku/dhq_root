from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.api.auth import get_current_user, get_op_user
from app.models.arcade import UserArcadeProfile
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class UserApprovalRequest(BaseModel):
    reason: Optional[str] = None

class AdminUserUpdateRequest(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None

@router.get("/admin/users")
async def admin_get_users(
    status: Optional[str] = None,
    role: Optional[str] = None,
    current_user: User = Depends(get_op_user)
):
    """List all users with optional filters (OP only)"""
    query = {}
    if status:
        query['status'] = status
    if role:
        query['role'] = role
        
    users = User.objects(**query)
    
    return {
        "users": [
            {
                "username": u.username,
                "display_name": u.display_name or u.username,
                "avatar_url": u.avatar_url,
                "role": u.role,
                "status": u.status,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login": u.last_login.isoformat() if u.last_login else None
            }
            for u in users
        ]
    }

@router.post("/admin/users/{username}/approve")
async def admin_approve_user(
    username: str,
    current_user: User = Depends(get_op_user)
):
    """Approve a pending user (OP only)"""
    user = User.objects(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.status = "ACTIVE"
    user.save()
    return {"message": f"User {username} approved successfully"}

@router.post("/admin/users/{username}/decline")
async def admin_decline_user(
    username: str,
    request: UserApprovalRequest,
    current_user: User = Depends(get_op_user)
):
    """Decline a pending user registration (OP only)"""
    user = User.objects(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.status = "DECLINED"
    user.save()
    return {"message": f"User {username} declined successfully"}

@router.patch("/admin/users/{username}")
async def admin_update_user(
    username: str,
    request: AdminUserUpdateRequest,
    current_user: User = Depends(get_op_user)
):
    """Update user role/status (OP only)"""
    user = User.objects(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if request.role is not None:
        if request.role in ('OP', 'AD', 'USER'):
            user.role = request.role
    if request.status is not None:
        if request.status in ('PENDING', 'ACTIVE', 'DECLINED'):
            user.status = request.status
            
    user.save()
    return {
        "message": f"User {username} updated successfully",
        "user": {
            "username": user.username,
            "role": user.role,
            "status": user.status
        }
    }

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
import logging
from app.services.email_watcher import email_watcher
import os
import uuid
import shutil

class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None

class AppearanceUpdateRequest(BaseModel):
    active_theme: Optional[str] = None
    side_menu_layout: Optional[str] = None

class EmailCredentialsRequest(BaseModel):
    email: str
    password: str

class AIProvidersRequest(BaseModel):
    providers: List[dict]

@router.get("/profile")
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get full profile of the current user including arcade stats"""
    arcade_profile = UserArcadeProfile.objects(user=current_user).first()
    if not arcade_profile:
        arcade_profile = UserArcadeProfile(user=current_user)
        arcade_profile.save()
        
    return {
        "username": current_user.username,
        "display_name": current_user.display_name or current_user.username,
        "email": current_user.email or "",
        "avatar_url": current_user.avatar_url,
        "banner_url": current_user.banner_url,
        "role": current_user.role,
        "status": current_user.status,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "kpi_current": current_user.kpi_current,
        "chip_balance": arcade_profile.chip_balance,
        "api_dollar_balance": arcade_profile.api_dollar_balance,
        "active_theme": arcade_profile.active_theme,
        "unlocked_themes": arcade_profile.unlocked_themes,
        "side_menu_layout": arcade_profile.side_menu_layout,
        "email_creds": {
            "email": current_user.email_creds.get("email", "") if current_user.email_creds else "",
            "has_password": bool(current_user.email_creds.get("password")) if current_user.email_creds else False
        },
        "ai_providers": [
            {
                "type": p.get("type", ""),
                "api_key": p.get("api_key", "")
            }
            for p in (current_user.ai_providers or [])
        ]
    }

@router.patch("/appearance")
async def update_appearance(
    request: AppearanceUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user's appearance preferences"""
    arcade_profile = UserArcadeProfile.objects(user=current_user).first()
    if not arcade_profile:
        arcade_profile = UserArcadeProfile(user=current_user)
        
    if request.active_theme is not None:
        if request.active_theme in arcade_profile.unlocked_themes:
            arcade_profile.active_theme = request.active_theme
        else:
            raise HTTPException(status_code=403, detail="Theme not unlocked")
            
    if request.side_menu_layout is not None:
        if request.side_menu_layout in ('list', 'grid'):
            arcade_profile.side_menu_layout = request.side_menu_layout
            
    arcade_profile.save()
    return {
        "message": "Appearance updated successfully",
        "active_theme": arcade_profile.active_theme,
        "side_menu_layout": arcade_profile.side_menu_layout
    }

@router.patch("/profile")
async def update_user_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile information"""
    if request.display_name is not None:
        current_user.display_name = request.display_name
    if request.email is not None:
        current_user.email = request.email
    
    current_user.save()
    return {"message": "Profile updated successfully", "user": {
        "display_name": current_user.display_name,
        "email": current_user.email
    }}

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and set user avatar"""
    # Create directory if it doesn't exist
    upload_dir = "uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    filename = f"{current_user.username}_{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update user record (external URL path)
    old_avatar = current_user.avatar_url
    current_user.avatar_url = f"/api/uploads/avatars/{filename}"
    current_user.save()
    
    # Optional: cleanup old avatar file
    if old_avatar and old_avatar.startswith("/uploads/"):
        old_path = old_avatar.lstrip("/")
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except:
                pass

    return {"message": "Avatar uploaded successfully", "avatar_url": current_user.avatar_url}

@router.post("/banner")
async def upload_banner(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and set user banner"""
    upload_dir = "uploads/banners"
    os.makedirs(upload_dir, exist_ok=True)
    
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    filename = f"{current_user.username}_{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    old_banner = current_user.banner_url
    current_user.banner_url = f"/api/uploads/banners/{filename}"
    current_user.save()
    
    if old_banner and old_banner.startswith("/uploads/"):
        old_path = old_banner.lstrip("/")
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except:
                pass

    return {"message": "Banner uploaded successfully", "banner_url": current_user.banner_url}

@router.get("/list")
async def get_users_list(current_user: User = Depends(get_current_user)):
    """Simple list of active users for search/share modals"""
    users = User.objects(status="ACTIVE")
    return [
        {
            "username": u.username,
            "display_name": u.display_name or u.username,
            "avatar_url": u.avatar_url
        }
        for u in users
    ]

@router.post("/avatar/reset")
async def reset_avatar(current_user: User = Depends(get_current_user)):
    """Reset user avatar to default (None)"""
    old_avatar = current_user.avatar_url
    current_user.avatar_url = None
    current_user.save()
    
    # Optional cleanup
    if old_avatar and old_avatar.startswith("/uploads/"):
        old_path = old_avatar.lstrip("/")
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except:
                pass
                
    return {"message": "Avatar reset successfully", "avatar_url": None}

@router.patch("/credentials/email")
async def update_email_credentials(
    request: EmailCredentialsRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user's email IMAP credentials"""
    current_user.email_creds = {
        "email": request.email,
        "password": request.password
    }
    current_user.save()
    
    # Restart the real-time watcher with new credentials
    email_watcher.start_user_watcher(current_user)
    
    return {"message": "Email credentials updated successfully"}

@router.patch("/credentials/ai")
async def update_ai_providers(
    request: AIProvidersRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user's AI provider configurations"""
    current_user.ai_providers = request.providers
    current_user.save()
    return {"message": "AI providers updated successfully"}
