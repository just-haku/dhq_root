from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, BackgroundTasks, Request, Form
from fastapi.responses import FileResponse, StreamingResponse
from app.models.user import User
from app.models.drive import DriveFile, DriveQuota, DriveFileShare
from app.api.auth import get_current_user, get_op_user
from app.core.thumbnails import generate_thumbnail, get_thumbnail_path
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import os
import uuid
import mimetypes
import io
from PIL import Image
from mongoengine import Q
import asyncio
import hashlib
import secrets
import base64

# Optional dependency for share access
async def get_current_user_optional():
    try:
        return await get_current_user()
    except:
        return None

import string
import random

def generate_short_id(length=6):
    """Generate a random Base62 string for share links"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

router = APIRouter()

# Configuration
from app.core.storage import storage_service

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
DEFAULT_QUOTA = 30 * 1024 * 1024 * 1024  # 30GB

# Ensure directories exist
for storage_path in storage_service.get_all_storage_paths():
    try:
        os.makedirs(os.path.join(storage_path, "DHQ_Root/Drive"), exist_ok=True)
        os.makedirs(os.path.join(storage_path, "thumbnails"), exist_ok=True)
    except Exception as e:
        print(f"WARNING: Could not initialize directories in {storage_path} - {e}")

# Pydantic models
class FolderCreateRequest(BaseModel):
    name: str
    parent_folder: Optional[str] = None
    description: Optional[str] = None

class FileShareRequest(BaseModel):
    file_id: str
    access_level: str = "only_me"  # "only_me", "specific_users", "internal", "public"
    share_type: str = "read"  # "read" or "write"
    specific_usernames: List[str] = []
    expires_hours: Optional[int] = None
    share_password: Optional[str] = None

class ShareAccessRequest(BaseModel):
    share_token: str
    password: Optional[str] = None

class QuotaAllocationRequest(BaseModel):
    username: str
    additional_quota_gb: int

class QuotaSetRequest(BaseModel):
    username: str
    total_quota_gb: int

class FileMoveRequest(BaseModel):
    file_id: str
    target_folder: Optional[str] = None

class FileRenameRequest(BaseModel):
    file_id: str
    new_name: str

# Helper functions
def get_user_quota(user: User) -> DriveQuota:
    """Get or create user quota"""
    def _get_role_quota(role: str) -> int:
        if role == "OP":
            return 50 * 1024 * 1024 * 1024  # 50GB
        elif role == "AD":
            return 30 * 1024 * 1024 * 1024   # 30GB
        return DEFAULT_QUOTA                  # 30GB

    try:
        quota = DriveQuota.objects(user=user).first()
        if not quota:
            quota = DriveQuota(user=user, total_quota=_get_role_quota(user.role))
            quota.save()
        return quota
    except Exception as e:
        print(f"Error getting quota: {e}")
        # Fallback to creating new quota
        quota = DriveQuota(user=user, total_quota=_get_role_quota(user.role))
        quota.save()
        return quota

def check_quota(user: User, file_size: int) -> bool:
    """Check if user has enough quota"""
    quota = get_user_quota(user)
    return quota.available_space >= file_size

def update_quota_usage(user: User, size_change: int):
    """Update user quota usage"""
    quota = get_user_quota(user)
    quota.used_space = max(0, quota.used_space + size_change)
    quota.save()

def get_user_drive_path(user: User) -> str:
    """Get legacy user's drive directory path"""
    primary_storage = storage_service.get_all_storage_paths()[0]
    return os.path.join(primary_storage, "DHQ_Root/Drive", str(user.id))

def ensure_user_directory(user: User):
    """Ensure user's drive directory exists dynamically in available storage"""
    storage_path = storage_service.get_available_storage_path()
    user_dir = os.path.join(storage_path, "DHQ_Root/Drive", str(user.id))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def generate_share_token(file_id: str, user_id: str) -> str:
    """Generate encrypted share token"""
    # Create a unique token using file_id, user_id, and timestamp
    timestamp = str(int(datetime.utcnow().timestamp()))
    raw_data = f"{file_id}:{user_id}:{timestamp}:{secrets.token_urlsafe(16)}"
    
    # Hash the data to create a secure token
    token = hashlib.sha256(raw_data.encode()).hexdigest()
    
    # Add a prefix to identify it as a share token
    return f"dhq_share_{token[:32]}"

def generate_share_link(share_token: str) -> str:
    """Generate encrypted share link"""
    # Base64 encode the token for URL safety
    encoded_token = base64.urlsafe_b64encode(share_token.encode()).decode()
    return f"https://haku.io.vn/shared/{encoded_token}"

def verify_share_token(share_token: str) -> Optional[str]:
    """Verify and decode share token"""
    try:
        # Remove prefix if present
        if share_token.startswith("dhq_share_"):
            share_token = share_token[10:]
        
        # Try to decode from base64
        try:
            decoded = base64.urlsafe_b64decode(share_token.encode()).decode()
        except:
            decoded = share_token
        
        return decoded
    except Exception:
        return None

# ==================== DRIVE ENDPOINTS ====================

@router.get("/drive/files")
async def get_drive_files(
    folder_path: str = "/",
    view_mode: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get user's drive files"""
    
    # Get files based on view_mode
    if view_mode == "trash":
        # Get all trashed items
        all_trashed = DriveFile.objects(
            owner=current_user,
            is_deleted=True
        ).order_by('-modified_at')
        
        # Build set of trashed folder paths — anything whose parent folder is also
        # in trash should be hidden (it's a "child" of a trashed folder, not user-deleted directly)
        trashed_folder_paths = set()
        for item in all_trashed:
            if item.is_folder:
                # A folder's "namespace" encompasses everything under folder_path/filename
                base = (item.folder_path.rstrip('/') + '/' + item.filename) if item.folder_path != '/' else '/' + item.filename
                trashed_folder_paths.add(base)
        
        # Only show items that are NOT inside a trashed folder
        files = []
        for item in all_trashed:
            # Check if this item lives inside any trashed folder
            item_folder = item.folder_path.rstrip('/')
            is_child_of_trashed_folder = any(
                item_folder == tp or item_folder.startswith(tp + '/')
                for tp in trashed_folder_paths
                if item.id != item.id  # Always False placeholder
            )
            # More reliable: check if the item's folder_path starts with a trashed folder path
            is_hidden = False
            for tp in trashed_folder_paths:
                if item_folder == tp or item_folder.startswith(tp + '/'):
                    is_hidden = True
                    break
            if not is_hidden:
                files.append(item)
    elif view_mode == "starred":

        files = DriveFile.objects(
            owner=current_user,
            is_starred=True,
            is_deleted=False
        ).order_by('-is_folder', 'filename')
    elif view_mode == "recent":
        files = DriveFile.objects(
            owner=current_user,
            is_deleted=False,
            is_folder=False
        ).order_by('-last_accessed')[:50]
    else:
        # Default folder view
        files = DriveFile.objects(
            owner=current_user,
            folder_path=folder_path,
            is_deleted=False
        ).order_by('-is_folder', 'filename')
    
    # Get user quota info - inline to avoid async issues
    try:
        quota = DriveQuota.objects(user=current_user).first()
        if not quota:
            quota = DriveQuota(user=current_user, total_quota=DEFAULT_QUOTA)
            quota.save()
        
        total = quota.total_quota or DEFAULT_QUOTA
        additional = quota.additional_quota or 0
        used = quota.used_space or 0
        
        quota_data = {
            "used_space": used,
            "total_quota": total,
            "additional_quota": additional,
            "available_space": total + additional - used,
            "usage_percentage": round((used / (total + additional) * 100), 2) if (total + additional) > 0 else 0
        }
    except Exception as e:
        print(f"Quota error: {e}")
        quota_data = {
            "used_space": 0,
            "total_quota": DEFAULT_QUOTA,
            "additional_quota": 0,
            "available_space": DEFAULT_QUOTA,
            "usage_percentage": 0
        }
    
    return {
        "files": [file.to_dict() for file in files],
        "folder_path": folder_path,
        "quota": quota_data,
        "total": len(files)
    }

@router.get("/drive/quota")
async def api_get_user_quota(
    current_user: User = Depends(get_current_user)
):
    """Get user's quota information"""
    quota = get_user_quota(current_user)
    return quota.to_dict()

@router.post("/drive/quota/sync")
async def api_sync_user_quota(
    current_user: User = Depends(get_current_user)
):
    """Force re-sync user's quota physically from filesystem"""
    # Reset to zero and recompute from actual files in the DB
    used_space = 0
    try:
        # Sum actual file sizes from non-deleted files in the database
        active_files = DriveFile.objects(
            owner=current_user,
            is_deleted=False,
            is_folder=False
        )
        for f in active_files:
            used_space += f.file_size or 0
    except Exception as e:
        # Fallback: walk the filesystem across all storages
        for storage_path in storage_service.get_all_storage_paths():
            user_drive_dir = os.path.join(storage_path, "DHQ_Root/Drive", str(current_user.id))
            if os.path.exists(user_drive_dir):
                for root, dirs, files in os.walk(user_drive_dir):
                    for file in files:
                        used_space += os.path.getsize(os.path.join(root, file))
    
    quota = get_user_quota(current_user)
    quota.used_space = used_space
    quota.save()
    return {
        "used_space": quota.used_space,
        "total_quota": quota.total_quota,
        "additional_quota": quota.additional_quota or 0,
        "available_space": quota.available_space,
        "usage_percentage": round(quota.usage_percentage, 2)
    }


@router.post("/drive/folder")
async def create_folder(
    request: FolderCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new folder"""
    
    # Check if folder already exists
    existing = DriveFile.objects(
        owner=current_user,
        folder_path=request.parent_folder or "/",
        filename=request.name,
        is_folder=True,
        is_deleted=False
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Folder already exists")
    
    # Create folder
    folder = DriveFile(
        filename=request.name,
        stored_filename="",  # Folders don't have stored files
        file_path="",        # Folders don't have file paths
        mime_type="folder",
        file_size=0,
        owner=current_user,
        folder_path=request.parent_folder or "/",
        parent_folder=request.parent_folder,
        is_folder=True,
        description=request.description
    )
    folder.save()
    
    return {"message": "Folder created successfully", "folder": folder.to_dict()}

@router.post("/drive/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder_path: str = Form("/"),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """Upload file to drive"""
    
    try:
        # Check for duplicate filename in the same folder first (saves reading time)
        existing_file = DriveFile.objects(
            owner=current_user,
            folder_path=folder_path,
            filename=file.filename,
            is_deleted=False,
            is_folder=False
        ).first()
        
        if existing_file:
            raise HTTPException(
                status_code=409,
                detail=f"A file named \"{file.filename}\" already exists in this folder. Rename the file or choose a different location."
            )

        # Check quota availability
        quota_obj = DriveQuota.objects(user=current_user).first()
        if not quota_obj:
            quota_obj = DriveQuota(user=current_user, total_quota=DEFAULT_QUOTA)
            quota_obj.save()
        
        available_space = quota_obj.available_space
        
        # Ensure user directory exists
        user_dir = ensure_user_directory(current_user)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        stored_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(user_dir, stored_filename)
        
        # Save file using streaming (chunked reading) to save memory
        file_size = 0
        try:
            with open(file_path, "wb") as buffer:
                while True:
                    chunk = await file.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    
                    file_size += len(chunk)
                    
                    # Check size limits while uploading
                    if file_size > MAX_FILE_SIZE:
                        raise HTTPException(
                            status_code=413,
                            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024*1024)}GB"
                        )
                        
                    if file_size > available_space:
                        raise HTTPException(
                            status_code=413,
                            detail=f"Not enough quota. Available: {available_space // (1024*1024)}MB"
                        )
                        
                    buffer.write(chunk)
        except Exception as e:
            # Clean up partial file on failure
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
        
        # Generate thumbnail if it's an image
        thumbnail_path = generate_thumbnail(file_path, file_id)
        has_thumbnail = thumbnail_path is not None
        
        # Create file record
        drive_file = DriveFile(
            filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            mime_type=file.content_type,
            file_size=file_size,
            owner=current_user,
            folder_path=folder_path,
            description=description,
            tags=tags.split(',') if tags else [],
            has_thumbnail=has_thumbnail,
            thumbnail_path=thumbnail_path
        )
        drive_file.save()
        
        # Update quota usage
        quota_obj.used_space += file_size
        quota_obj.save()
        
        return {
            "message": "File uploaded successfully",
            "file": drive_file.to_dict()
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Detailed Upload Error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/drive/download/{file_id}")
async def download_file(
    file_id: str,
    share_token: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Download file from drive"""
    
    file = DriveFile.objects(id=file_id, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check permissions
    has_access = False
    
    # Owner always has access
    if current_user and str(file.owner.id) == str(current_user.id):
        has_access = True
    
    # Check if shared with user
    elif current_user:
        user_share = next((share for share in file.shares if str(share.shared_with.id) == str(current_user.id)), None)
        if user_share:
            has_access = True
        
        # Check if user is in allowed users list
        elif file.allowed_users and any(str(user.id) == str(current_user.id) for user in file.allowed_users):
            has_access = True
    
    # Check share token access
    elif share_token:
        # Verify share token
        if file.share_token == share_token:
            # Check if link has expired
            if file.public_share_expires and datetime.utcnow() > file.public_share_expires:
                raise HTTPException(status_code=410, detail="Share link has expired")
            has_access = True
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if file.is_folder:
        raise HTTPException(status_code=400, detail="Cannot download folder")
    
    try:
        # Update access info
        file.last_accessed = datetime.utcnow()
        file.download_count += 1
        file.save()
        
        # Return file
        return FileResponse(
            file.file_path,
            media_type=file.mime_type,
            filename=file.filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.post("/drive/share")
async def share_file(
    request: FileShareRequest,
    current_user: User = Depends(get_current_user)
):
    """Share file with enhanced Google Drive-like settings"""
    
    file = DriveFile.objects(id=request.file_id, owner=current_user, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Update file access level
        file.access_level = request.access_level
        
        # Clear existing shares and allowed users
        file.shares = []
        file.allowed_users = []
        
        # Handle specific users
        if request.access_level == "specific_users":
            from app.models.user import User as UserModel
            for username in request.specific_usernames:
                target_user = UserModel.objects(username=username).first()
                if target_user:
                    file.allowed_users.append(target_user)
                    
                    # Create share record
                    share = DriveFileShare(
                        shared_with=target_user,
                        shared_by=current_user,
                        share_type=request.share_type,
                        expires_at=datetime.utcnow() + timedelta(hours=request.expires_hours) if request.expires_hours else None,
                        access_level="specific_users"
                    )
                    file.shares.append(share)
        
        # Generate share token and link for internal/public access
        if request.access_level in ["internal", "public"]:
            if not file.share_link_id:
                # generate unique ID
                while True:
                    new_id = generate_short_id()
                    if not DriveFile.objects(share_link_id=new_id).first():
                        break
                file.share_link_id = new_id
                file.share_token = generate_share_token(str(file.id), str(current_user.id))
            
            # The public route is now the short url
            file.public_share_link = f"https://haku.io.vn/{file.share_link_id}"
            
            if request.expires_hours:
                file.public_share_expires = datetime.utcnow() + timedelta(hours=request.expires_hours)
            else:
                file.public_share_expires = None
            
            # Set password if provided
            if request.share_password:
                file.share_password = hashlib.sha256(request.share_password.encode()).hexdigest()
            else:
                file.share_password = None
        
        # Save the file
        file.save()
        
        return {
            "message": "File shared successfully",
            "file": file.to_dict(),
            "share_link": file.public_share_link if file.access_level in ["internal", "public"] else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Share failed: {str(e)}")

@router.get("/drive/shared/{short_id}")
async def access_shared_file(
    short_id: str,
    password: Optional[str] = None
):
    """Access shared file via encrypted short link"""
    
    try:
        # Find file by short ID
        file = DriveFile.objects(share_link_id=short_id, is_deleted=False).first()
        if not file:
            raise HTTPException(status_code=404, detail="Shared file not found")
        
        # Check if link has expired
        if file.public_share_expires and datetime.utcnow() > file.public_share_expires:
            raise HTTPException(status_code=410, detail="Share link has expired")
        
        # Check password protection
        if file.share_password:
            if not password:
                raise HTTPException(status_code=401, detail="Password required")
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash != file.share_password:
                raise HTTPException(status_code=401, detail="Invalid password")
        
        # Update access count
        file.last_accessed = datetime.utcnow()
        file.download_count += 1
        file.save()
        
        # Verify the file actually exists on disk
        if not os.path.exists(file.file_path):
            raise HTTPException(status_code=404, detail="File content not found on server")
            
        return FileResponse(
            path=file.file_path,
            filename=file.filename,
            media_type=file.mime_type,
            content_disposition_type="inline" # Allows previewing natively if possible
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Access failed: {str(e)}")

async def delete_folder_contents(folder, current_user):
    """Recursively soft-delete all contents of a folder"""
    folder_base = folder.folder_path + folder.filename if folder.folder_path != "/" else "/" + folder.filename
    folder_prefix = folder_base + "/"
    # Find all files in this folder and subfolders
    contents = DriveFile.objects(
        Q(owner=current_user) &
        Q(is_deleted=False) &
        (Q(folder_path=folder_base) | Q(folder_path__startswith=folder_prefix))
    )
    
    for content in contents:
        if content.is_folder:
            # Recursively delete subfolder contents
            await delete_folder_contents(content, current_user)
        
        # Soft delete the database record
        content.is_deleted = True
        content.modified_at = datetime.utcnow()
        content.save()

@router.delete("/drive/file/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete file or folder"""
    
    file = DriveFile.objects(id=file_id, owner=current_user, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        if file.is_folder:
            # Soft-Delete folder and all contents
            await delete_folder_contents(file, current_user)
        
        # Soft delete the file/folder
        file.is_deleted = True
        file.modified_at = datetime.utcnow()
        file.save()
        
        return {"message": "File moved to trash successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.delete("/drive/folder/{folder_id}/contents")
async def clear_folder(
    folder_id: str,
    current_user: User = Depends(get_current_user)
):
    """Clear all contents of a folder without deleting the folder itself"""
    
    folder = DriveFile.objects(id=folder_id, owner=current_user, is_deleted=False, is_folder=True).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    try:
        # Soft Delete all contents
        await delete_folder_contents(folder, current_user)
        
        return {"message": "Folder moved to trash successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear folder failed: {str(e)}")

@router.post("/drive/star/{file_id}")
async def toggle_star(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Toggle starred status for a file or folder"""
    file = DriveFile.objects(id=file_id, owner=current_user, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        file.is_starred = not getattr(file, 'is_starred', False)
        file.save()
        return {"message": f"{'Starred' if file.is_starred else 'Unstarred'} successfully", "is_starred": file.is_starred}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status update failed: {str(e)}")

@router.post("/drive/label/{file_id}")
async def set_labels(
    file_id: str,
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Set labels for a file or folder"""
    file = DriveFile.objects(id=file_id, owner=current_user, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        labels = request.get('labels', [])
        file.labels = labels
        file.save()
        return {"message": "Labels updated successfully", "labels": file.labels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Label update failed: {str(e)}")

@router.post("/drive/file/{file_id}/restore")
async def restore_file(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Restore soft-deleted file or folder"""
    file = DriveFile.objects(id=file_id, owner=current_user, is_deleted=True).first()
    if not file:
        raise HTTPException(status_code=404, detail="Deleted file not found")
        
    try:
        # Before restoring, we must ensure quota permits restoring size
        if not file.is_folder:
            quota = DriveQuota.objects(user=current_user).first()
            if quota and (quota.used_space + file.file_size) > (quota.total_quota + quota.additional_quota):
                raise HTTPException(status_code=413, detail="Not enough quota to restore file")
                
            if quota:
                quota.used_space += file.file_size
                quota.save()
        else:
            # Note: For simplicity, we assume restoring folder restores everything in it immediately
            # In a robust implementation, we recursively check children quota before permitting.
            pass
            
        file.is_deleted = False
        file.save()
        
        return {"message": "File restored successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")

@router.delete("/drive/trash")
async def empty_trash(
    current_user: User = Depends(get_current_user)
):
    """Permanently delete all files in the trash"""
    deleted_files = DriveFile.objects(owner=current_user, is_deleted=True)
    
    freed_space = 0
    deleted_count = 0
    
    try:
        for file in deleted_files:
            if not file.is_folder and file.file_path and os.path.exists(file.file_path):
                try:
                    file_size = os.path.getsize(file.file_path)
                    os.remove(file.file_path)
                    freed_space += file_size
                except Exception as e:
                    print(f"Failed to remove physical file {file.file_path}: {e}")
            
            file.delete()
            deleted_count += 1
            
        if freed_space > 0:
            update_quota_usage(current_user, -freed_space)
        return {"message": "Trash emptied successfully", "deleted_count": deleted_count, "freed_space": freed_space}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to empty trash: {str(e)}")

@router.delete("/drive/trash/{file_id}")
async def delete_trash_item(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Permanently delete a single file or folder from the trash"""
    file = DriveFile.objects(id=file_id, owner=current_user, is_deleted=True).first()
    if not file:
        raise HTTPException(status_code=404, detail="Deleted file not found")
        
    freed_space = 0
    try:
        # If folder, recursively physical delete mapped contents
        if file.is_folder:
            # Recursively find all nested items matching this folder root
            folder_base = file.folder_path + file.filename if file.folder_path != "/" else "/" + file.filename
            folder_prefix = folder_base + "/"
            contents = DriveFile.objects(
                Q(owner=current_user) &
                Q(is_deleted=True) &
                (Q(folder_path=folder_base) | Q(folder_path__startswith=folder_prefix))
            )
            for content in contents:
                if not content.is_folder and content.file_path and os.path.exists(content.file_path):
                    try:
                        file_size = os.path.getsize(content.file_path)
                        os.remove(content.file_path)
                        freed_space += file_size
                    except Exception as e:
                        print(f"Failed to remove physical child file {content.file_path}: {e}")
                content.delete()
        
        else:
            if file.file_path and os.path.exists(file.file_path):
                try:
                    file_size = os.path.getsize(file.file_path)
                    os.remove(file.file_path)
                    freed_space += file_size
                except Exception as e:
                    print(f"Failed to remove physical file {file.file_path}: {e}")
                    
        file.delete()
        
        if freed_space > 0:
            update_quota_usage(current_user, -freed_space)
            
        return {"message": "File permanently deleted", "freed_space": freed_space}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete permanently: {str(e)}")

@router.get("/drive/folders/all")
async def get_all_folders(
    current_user: User = Depends(get_current_user)
):
    """Get all folders for move operations"""
    
    folders = DriveFile.objects(
        owner=current_user,
        is_folder=True,
        is_deleted=False
    ).order_by('filename')
    
    return {
        "folders": [
            {
                "id": str(folder.id),
                "filename": folder.filename,
                "folder_path": folder.folder_path
            }
            for folder in folders
        ]
    }

@router.post("/drive/update-access")
async def update_file_access(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Update file access settings"""
    
    file_id = request.get('file_id')
    access_level = request.get('access_level')
    password = request.get('password')
    
    file = DriveFile.objects(id=file_id, owner=current_user, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file.access_level = access_level
        file.share_password = password if password else None
        file.modified_at = datetime.utcnow()
        file.save()
        
        return {"message": "Access updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update access failed: {str(e)}")

@router.post("/drive/add-user-access")
async def add_user_access(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Add user access to file"""
    
    file_id = request.get('file_id')
    username = request.get('username')
    
    file = DriveFile.objects(id=file_id, owner=current_user, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        from app.models.user import User as UserModel
        target_user = UserModel.objects(username=username).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not file.allowed_users:
            file.allowed_users = []
        
        # Check if user already has access
        user_ids = [str(user.id) for user in file.allowed_users]
        if str(target_user.id) not in user_ids:
            file.allowed_users.append(target_user)
            file.modified_at = datetime.utcnow()
            file.save()
        
        return {"message": "User access added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Add user access failed: {str(e)}")

@router.post("/drive/remove-user-access")
async def remove_user_access(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """Remove user access from file"""
    
    file_id = request.get('file_id')
    user_id = request.get('user_id')
    
    file = DriveFile.objects(id=file_id, owner=current_user, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        if file.allowed_users:
            file.allowed_users = [
                user for user in file.allowed_users 
                if str(user.id) != user_id
            ]
            file.modified_at = datetime.utcnow()
            file.save()
        
        return {"message": "User access removed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Remove user access failed: {str(e)}")

@router.get("/drive/thumbnail/{file_id}")
async def get_thumbnail(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get thumbnail for a file"""
    file = DriveFile.objects(id=file_id, owner=current_user, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if not file.has_thumbnail or not file.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    if not os.path.exists(file.thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail file not found")
    
    # If the file is a video, the generated thumbnail is always a JPEG frame
    mime = "image/jpeg" if file.mime_type and file.mime_type.startswith('video/') else file.mime_type
    
    return FileResponse(
        file.thumbnail_path,
        media_type=mime
    )

@router.post("/drive/copy")
async def copy_file(
    request: FileMoveRequest,
    current_user: User = Depends(get_current_user)
):
    """Copy file or folder to another location"""
    
    file = DriveFile.objects(id=request.file_id, owner=current_user, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Create copy with new location
        new_file = DriveFile(
            filename=file.filename,
            stored_filename=file.stored_filename if not file.is_folder else "",
            file_path=file.file_path if not file.is_folder else "",
            mime_type=file.mime_type,
            file_size=file.file_size,
            owner=current_user,
            folder_path=request.target_folder if request.target_folder else "/",
            parent_folder=request.target_folder,
            is_folder=file.is_folder,
            description=file.description,
            tags=file.tags
        )
        
        # If it's a file, copy the actual file
        if not file.is_folder and file.file_path and os.path.exists(file.file_path):
            new_stored_filename = f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
            new_file_path = os.path.join(get_user_drive_path(current_user), new_stored_filename)
            
            import shutil
            shutil.copy2(file.file_path, new_file_path)
            
            new_file.stored_filename = new_stored_filename
            new_file.file_path = new_file_path
        
        new_file.save()
        
        # If it's a folder, recursively copy contents
        if file.is_folder:
            await copy_folder_contents(file, new_file, current_user)
        
        return {"message": "File copied successfully", "file": new_file.to_dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copy failed: {str(e)}")

@router.post("/drive/move")
async def move_file(
    request: FileMoveRequest,
    current_user: User = Depends(get_current_user)
):
    """Move file or folder to another location"""
    
    file = DriveFile.objects(id=request.file_id, owner=current_user, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Update location
        file.folder_path = request.target_folder if request.target_folder else "/"
        file.parent_folder = request.target_folder
        file.modified_at = datetime.utcnow()
        file.save()
        
        return {"message": "File moved successfully", "file": file.to_dict()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Move failed: {str(e)}")

async def copy_folder_contents(source_folder, target_folder, current_user):
    """Recursively copy folder contents"""
    source_path = source_folder.file_path + source_folder.filename + "/"
    target_path = target_folder.file_path + target_folder.filename + "/"
    
    contents = DriveFile.objects(
        owner=current_user,
        folder_path=source_path,
        is_deleted=False
    )
    
    for content in contents:
        new_content = DriveFile(
            filename=content.filename,
            stored_filename=content.stored_filename if not content.is_folder else "",
            file_path=content.file_path if not content.is_folder else "",
            mime_type=content.mime_type,
            file_size=content.file_size,
            owner=current_user,
            folder_path=target_path,
            parent_folder=target_folder.id,
            is_folder=content.is_folder,
            description=content.description,
            tags=content.tags
        )
        
        # Copy actual file if it's not a folder
        if not content.is_folder and content.file_path and os.path.exists(content.file_path):
            new_stored_filename = f"{uuid.uuid4()}{os.path.splitext(content.filename)[1]}"
            new_file_path = os.path.join(get_user_drive_path(current_user), new_stored_filename)
            
            import shutil
            shutil.copy2(content.file_path, new_file_path)
            
            new_content.stored_filename = new_stored_filename
            new_content.file_path = new_file_path
        
        new_content.save()
        
        # Recursively copy subfolder contents
        if content.is_folder:
            await copy_folder_contents(content, new_content, current_user)

# ==================== OP ADMIN ENDPOINTS ====================

@router.get("/drive/admin/users")
async def get_all_users_quota(
    current_user: User = Depends(get_op_user)
):
    """Get all users' quota information (OP only)"""
    
    from app.models.user import User as UserModel
    users = UserModel.objects()
    
    quota_info = []
    for user in users:
        try:
            quota = DriveQuota.objects(user=user).first()
            if not quota:
                quota = DriveQuota(user=user, total_quota=DEFAULT_QUOTA)
                quota.save()
            
            quota_info.append({
                'id': str(quota.id),
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'display_name': user.display_name
                },
                'used_space': quota.used_space,
                'total_quota': quota.total_quota,
                'additional_quota': quota.additional_quota,
                'available_space': quota.total_quota + quota.additional_quota - quota.used_space,
                'usage_percentage': round((quota.used_space / (quota.total_quota + quota.additional_quota) * 100), 2) if (quota.total_quota + quota.additional_quota) > 0 else 0
            })
        except Exception as e:
            print(f"Error getting quota for user {user.username}: {e}")
    
    return {"users": quota_info, "total": len(quota_info)}

@router.post("/drive/admin/allocate-quota")
async def allocate_quota(
    request: QuotaAllocationRequest,
    current_user: User = Depends(get_op_user)
):
    """Allocate additional quota to user (OP only)"""
    
    from app.models.user import User as UserModel
    target_user = UserModel.objects(username=request.username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        quota = DriveQuota.objects(user=target_user).first()
        if not quota:
            quota = DriveQuota(user=target_user, total_quota=DEFAULT_QUOTA)
            quota.save()
        
        additional_bytes = request.additional_quota_gb * 1024 * 1024 * 1024
        quota.additional_quota += additional_bytes
        quota.save()
        
        return {
            "message": f"Allocated {request.additional_quota_gb}GB to {request.username}",
            "quota": {
                'id': str(quota.id),
                'user': {
                    'id': str(target_user.id),
                    'username': target_user.username,
                    'display_name': target_user.display_name
                },
                'used_space': quota.used_space,
                'total_quota': quota.total_quota,
                'additional_quota': quota.additional_quota,
                'available_space': quota.total_quota + quota.additional_quota - quota.used_space,
                'usage_percentage': round((quota.used_space / (quota.total_quota + quota.additional_quota) * 100), 2) if (quota.total_quota + quota.additional_quota) > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Allocation failed: {str(e)}")

@router.get("/drive/admin/user/{username}")
async def get_user_files(
    username: str,
    current_user: User = Depends(get_op_user)
):
    """Get user's files (OP only)"""
    
    from app.models.user import User as UserModel
    target_user = UserModel.objects(username=username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    files = DriveFile.objects(
        owner=target_user,
        is_deleted=False
    ).order_by('-created_at')
    
    try:
        quota = DriveQuota.objects(user=target_user).first()
        if not quota:
            quota = DriveQuota(user=target_user, total_quota=DEFAULT_QUOTA)
            quota.save()
        
        quota_data = {
            'id': str(quota.id),
            'user': {
                'id': str(target_user.id),
                'username': target_user.username,
                'display_name': target_user.display_name
            },
            'used_space': quota.used_space,
            'total_quota': quota.total_quota,
            'additional_quota': quota.additional_quota,
            'available_space': quota.total_quota + quota.additional_quota - quota.used_space,
            'usage_percentage': round((quota.used_space / (quota.total_quota + quota.additional_quota) * 100), 2) if (quota.total_quota + quota.additional_quota) > 0 else 0
        }
    except Exception as e:
        print(f"Error getting quota for user {username}: {e}")
        quota_data = None
    
    return {
        "user": {
            "id": str(target_user.id),
            "username": target_user.username,
            "display_name": target_user.display_name
        },
        "files": [file.to_dict() for file in files],
        "quota": quota_data,
        "total": len(files)
    }

@router.post("/drive/admin/set-quota")
async def set_quota(
    request: QuotaSetRequest,
    current_user: User = Depends(get_op_user)
):
    """Set absolute quota for user (OP only)"""
    from app.models.user import User as UserModel
    target_user = UserModel.objects(username=request.username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        quota = DriveQuota.objects(user=target_user).first()
        if not quota:
            quota = DriveQuota(user=target_user, total_quota=DEFAULT_QUOTA)
            quota.save()
        
        # We override total_quota to the new value, reset additional_quota to 0
        quota.total_quota = request.total_quota_gb * 1024 * 1024 * 1024
        quota.additional_quota = 0
        quota.save()
        
        return {
            "message": f"Quota set to {request.total_quota_gb}GB for {request.username}",
            "quota": {
                'id': str(quota.id),
                'user': {
                    'id': str(target_user.id),
                    'username': target_user.username,
                    'display_name': target_user.display_name
                },
                'used_space': quota.used_space,
                'total_quota': quota.total_quota,
                'additional_quota': quota.additional_quota,
                'available_space': quota.total_quota + quota.additional_quota - quota.used_space,
                'usage_percentage': round((quota.used_space / (quota.total_quota + quota.additional_quota) * 100), 2) if (quota.total_quota + quota.additional_quota) > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Set quota failed: {str(e)}")

@router.delete("/drive/admin/file/{file_id}")
async def admin_delete_file(
    file_id: str,
    current_user: User = Depends(get_op_user)
):
    """Delete any user's file or folder (OP only)"""
    file = DriveFile.objects(id=file_id, is_deleted=False).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        owner = file.owner
        if file.is_folder:
            # Delete folder and all contents
            total_size_freed = await delete_folder_contents(file, owner)
            # Update quota for deleted files in folder
            try:
                quota = DriveQuota.objects(user=owner).first()
                if quota:
                    quota.used_space = max(0, quota.used_space - total_size_freed)
                    quota.save()
            except Exception as e:
                print(f"Error updating quota after folder delete: {e}")
        
        # Soft delete the file/folder
        file.is_deleted = True
        file.modified_at = datetime.utcnow()
        file.save()
        
        # Update quota usage for single file
        if not file.is_folder:
            try:
                quota = DriveQuota.objects(user=owner).first()
                if quota:
                    quota.used_space = max(0, quota.used_space - file.file_size)
                    quota.save()
            except Exception as e:
                print(f"Error updating quota after file delete: {e}")
        
        return {"message": "Admin file deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
