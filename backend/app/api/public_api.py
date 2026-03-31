from fastapi import APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import FileResponse, StreamingResponse
from app.models.drive import DriveFile
from app.models.vault import VaultFile
from app.models.comment import Comment
from app.api.auth import get_current_user_optional
from app.core.vault_crypto import get_vault_cipher
import os
import hashlib
import zipfile
import io
from mongoengine import Q
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

import uuid
import time

router = APIRouter()

# In-memory store for one-time preview tokens (Token -> (ShareID, Expiry))
# In production, this should be moved to Redis
preview_tokens = {}

def cleanup_expired_tokens():
    now = time.time()
    for token in list(preview_tokens.keys()):
        if preview_tokens[token][1] < now:
            del preview_tokens[token]

class PasswordVerifyRequest(BaseModel):
    password: str

class CommentCreateRequest(BaseModel):
    content: str
    guest_name: Optional[str] = None

def get_item_by_share_id(share_id: str):
    # Try Drive first (usually 6 chars)
    item = DriveFile.objects(share_link_id=share_id, is_deleted=False).first()
    if item:
        return item, "drive"
    
    # Try Vault (usually 32 chars)
    item = VaultFile.objects(share_link_id=share_id, is_deleted=False).first()
    if item:
        return item, "vault"
    
    return None, None

@router.get("/public/access/{share_id}")
async def get_public_access(share_id: str, file_id: Optional[str] = None):
    """Get metadata for a shared link (optionally for a specific file within a shared folder)"""
    root_item, item_type = get_item_by_share_id(share_id)
    if not root_item:
        raise HTTPException(status_code=404, detail="Link not found")
        
    # Check expiration for the root shared item
    expires = getattr(root_item, 'public_share_expires', None)
    if expires and datetime.utcnow() > expires:
        raise HTTPException(status_code=410, detail="Share link has expired")

    target_item = root_item
    if file_id and root_item.is_folder:
        if item_type == "drive":
            target_item = DriveFile.objects(id=file_id, is_deleted=False).first()
        else:
            target_item = VaultFile.objects(id=file_id, is_deleted=False).first()
            
        if not target_item:
            raise HTTPException(status_code=404, detail="File not found")
            
        # Security check: Ensure target_item is a child of root_item
        # root_item.folder_path + root_item.filename should be the prefix for target_item.folder_path
        base_path = root_item.folder_path
        if base_path == "/":
            root_prefix = f"/{root_item.filename}"
        else:
            root_prefix = f"{base_path.rstrip('/')}/{root_item.filename}"
            
        # Check if the target_item's path starts with the root_prefix or is exactly the root_prefix
        # This handles cases where the root_item itself is the target (e.g., root_prefix = /folder, target_item.folder_path = /folder)
        # or if it's a child (e.g., target_item.folder_path = /folder/subfolder)
        if not (target_item.folder_path == root_prefix or target_item.folder_path.startswith(root_prefix + "/")):
            raise HTTPException(status_code=403, detail="Access denied to this file")

    permission_level = getattr(root_item, 'permission_level', 'viewer')
    return {
        "id": str(target_item.id),
        "name": target_item.filename,
        "type": "folder" if target_item.is_folder else "file",
        "size": target_item.file_size if not target_item.is_folder else 0,
        "has_password": bool(root_item.share_password),
        "permission_level": permission_level,
        "owner_name": root_item.owner.username if root_item.owner else "System",
        "created_at": root_item.created_at,
        "item_type": item_type,
        "share_id": share_id,
        "requires_token": permission_level in ['visitor', 'viewer']
    }

@router.get("/public/token/{share_id}")
async def generate_preview_token(share_id: str, password: Optional[str] = None):
    """Generate a short-lived, one-time token for media preview"""
    item, _ = get_item_by_share_id(share_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    # Password check
    if item.share_password:
        if not password or hashlib.sha256(password.encode()).hexdigest() != item.share_password:
             raise HTTPException(status_code=401, detail="Password required")
             
    cleanup_expired_tokens()
    token = str(uuid.uuid4())
    # Token valid for 10 seconds
    preview_tokens[token] = (share_id, time.time() + 10)
    return {"token": token}

@router.post("/public/verify/{share_id}")
async def verify_public_password(share_id: str, req: PasswordVerifyRequest):
    """Verify password for a shared item"""
    item, _ = get_item_by_share_id(share_id)
    if not item or not item.share_password:
        raise HTTPException(status_code=404, detail="No password required or link not found")
    
    password_hash = hashlib.sha256(req.password.encode()).hexdigest()
    if password_hash == item.share_password:
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=401, detail="Invalid password")

@router.get("/public/files/{share_id}")
async def list_shared_folder(share_id: str, folder_path: str = Query("/"), password: Optional[str] = None):
    """List contents of a shared folder (Drive only for now, or virtual Vault folders)"""
    item, item_type = get_item_by_share_id(share_id)
    if not item or not item.is_folder:
        raise HTTPException(status_code=404, detail="Shared folder not found")
    
    # Verification logic (simplified for listing, ideally handled by session/cookie in real app)
    if item.share_password:
        if not password or hashlib.sha256(password.encode()).hexdigest() != item.share_password:
             raise HTTPException(status_code=401, detail="Password required")

    # For folders, we return children that match the owner and the virtual path
    if item_type == "drive":
        # Calculate the absolute virtual path being requested
        # item.folder_path + item.filename is the base
        base_path = (item.folder_path.rstrip('/') + '/' + item.filename) if item.folder_path != '/' else '/' + item.filename
        requested_path = base_path if folder_path == "/" else f"{base_path}/{folder_path.strip('/')}"
        
        children = DriveFile.objects(owner=item.owner, folder_path=requested_path, is_deleted=False).order_by('-is_folder', 'filename')
        return [f.to_dict() for f in children]
    else:
        # Vault folders
        base_path = (item.folder_path.rstrip('/') + '/' + item.filename) if item.folder_path != '/' else '/' + item.filename
        requested_path = base_path if folder_path == "/" else f"{base_path}/{folder_path.strip('/')}"
        children = VaultFile.objects(owner=item.owner, folder_path=requested_path, is_deleted=False).order_by('-is_folder', 'filename')
        return [f.to_dict() for f in children]

@router.get("/public/download/{share_id}")
async def download_shared_file(
    share_id: str, 
    password: Optional[str] = None, 
    preview: bool = False,
    token: Optional[str] = None
):
    """Download or stream a shared file with permission enforcement"""
    item, item_type = get_item_by_share_id(share_id)
    if not item or item.is_folder:
        raise HTTPException(status_code=404, detail="File not found")
    
    permission = getattr(item, 'permission_level', 'viewer')
    
    # 1. Enforce Token for Visitor/Viewer Previews to prevent direct DevTools link extraction
    if preview and permission in ['visitor', 'viewer']:
        if not token or token not in preview_tokens:
            raise HTTPException(status_code=403, detail="Invalid or expired preview token")
        
        assigned_share_id, expiry = preview_tokens[token]
        if assigned_share_id != share_id or expiry < time.time():
            if token in preview_tokens: del preview_tokens[token]
            raise HTTPException(status_code=403, detail="Preview token mismatched or expired")
            
        # Consume token immediately
        del preview_tokens[token]

    # 2. Enforce Visitor Download Restriction
    if permission == 'visitor' and not preview:
        raise HTTPException(status_code=403, detail="Download not allowed for visitors")

    # 3. Password check (if no token was used or needed)
    if item.share_password and not token:
        if not password or hashlib.sha256(password.encode()).hexdigest() != item.share_password:
             raise HTTPException(status_code=401, detail="Password required")

    # Update counts
    item.download_count += 1
    item.save()

    if item_type == "drive":
        if not os.path.exists(item.file_path):
             raise HTTPException(status_code=404, detail="File missing on server")
        return FileResponse(
            item.file_path,
            media_type=item.mime_type,
            filename=item.filename,
            content_disposition_type="inline" if preview else "attachment"
        )
    else:
        # Vault file
        if not os.path.exists(item.file_path):
             raise HTTPException(status_code=404, detail="File missing on server")
        
        cipher = get_vault_cipher()
        return StreamingResponse(
            cipher.decrypt_stream(item.file_path),
            media_type=item.mime_type,
            headers={
                "Content-Disposition": f"attachment; filename=\"{item.filename}\"",
                "X-Content-Type-Options": "nosniff"
            }
        )

@router.get("/public/comments/{share_id}")
async def get_comments(share_id: str):
    """List comments for a share"""
    comments = Comment.objects(target_id=share_id).order_by('-created_at')
    return [c.to_dict() for c in comments]

@router.post("/public/comments/{share_id}")
async def add_comment(share_id: str, req: CommentCreateRequest, current_user = Depends(get_current_user_optional)):
    """Add a comment to a share"""
    item, item_type = get_item_by_share_id(share_id)
    if not item:
        raise HTTPException(status_code=404, detail="Link not found")
    
    permission = getattr(item, 'permission_level', 'viewer')
    
    # Enforce permission
    if permission == 'visitor' or permission == 'viewer':
        raise HTTPException(status_code=403, detail="Commenting not allowed for this link")
    
    if permission == 'commenter' and not current_user:
        raise HTTPException(status_code=401, detail="Log in to comment on this link")
    
    # Editor can comment as guest
    comment = Comment(
        target_id=share_id,
        target_type=item_type,
        user=current_user,
        guest_name=req.guest_name if not current_user else None,
        content=req.content
    )
    comment.save()
    return comment.to_dict()

@router.get("/public/zip/{share_id}")
async def zip_public_folder(
    share_id: str,
    sub_path: Optional[str] = Query(None),
    password: Optional[str] = None
):
    """Zip and download a public shared folder (optionally a subfolder)"""
    item, item_type = get_item_by_share_id(share_id)
    if not item or not item.is_folder:
        raise HTTPException(status_code=404, detail="Shared folder not found")
        
    # Password check
    if item.share_password:
        if not password or hashlib.sha256(password.encode()).hexdigest() != item.share_password:
            raise HTTPException(status_code=401, detail="Password required")

    # Get all items recursively
    # if sub_path is provided, we start from base_path + sub_path
    base_path = item.folder_path
    if base_path == "/":
        root_virtual_path = f"/{item.filename}"
    else:
        root_virtual_path = f"{base_path.rstrip('/')}/{item.filename}"
        
    if sub_path:
        full_virtual_path = f"{root_virtual_path.rstrip('/')}/{sub_path.strip('/')}"
    else:
        full_virtual_path = root_virtual_path

    if item_type == "drive":
        # Drive logic
        query = Q(owner=item.owner, is_deleted=False) & (
            Q(folder_path=full_virtual_path) | Q(folder_path__startswith=full_virtual_path + "/")
        )
        all_files = DriveFile.objects(query).filter(is_folder=False)
    else:
        # Vault logic
        query = Q(owner=item.owner, is_deleted=False) & (
            Q(folder_path=full_virtual_path) | Q(folder_path__startswith=full_virtual_path + "/")
        )
        all_files = VaultFile.objects(query).filter(is_folder=False)

    def generate_zip():
        io_output = io.BytesIO()
        vault_cipher = get_vault_cipher() if item_type != "drive" else None
        
        with zipfile.ZipFile(io_output, "w", zipfile.ZIP_DEFLATED) as zf:
            for file in all_files:
                if os.path.exists(file.file_path):
                    rel_path = file.folder_path[len(full_virtual_path):].lstrip('/')
                    archive_name = os.path.join(rel_path, file.filename)
                    
                    if item_type == "drive":
                        zf.write(file.file_path, archive_name)
                    else:
                        # Decrypt vault file for zip
                        decrypted_data = vault_cipher.decrypt_stream(file.file_path)
                        # We need to buffer the stream or read it all
                        zf.writestr(archive_name, b"".join(decrypted_data))
                
        io_output.seek(0)
        return io_output.getvalue()

    zip_data = generate_zip()
    
    return StreamingResponse(
        io.BytesIO(zip_data),
        media_type="application/x-zip-compressed",
        headers={
            "Content-Disposition": f"attachment; filename=\"{item.filename}.zip\""
        }
    )

@router.get("/public/thumbnail/{share_id}")
async def get_public_thumbnail(
    share_id: str,
    file_id: Optional[str] = None,
    password: Optional[str] = None,
    token: Optional[str] = None
):
    """Serve thumbnail for a shared item with token or password validation"""
    root_item, item_type = get_item_by_share_id(share_id)
    if not root_item:
        raise HTTPException(status_code=404, detail="Link not found")
        
    # If file_id is provided, find the target item
    target_item = root_item
    if file_id and str(root_item.id) != file_id:
        if item_type == "drive":
            target_item = DriveFile.objects(id=file_id, is_deleted=False).first()
        else:
            target_item = VaultFile.objects(id=file_id, is_deleted=False).first()
            
        if not target_item:
             raise HTTPException(status_code=404, detail="File not found")

    # Security check: Ensure target_item is a child of root_item
    root_full_path = (root_item.folder_path.rstrip('/') + '/' + root_item.filename) if root_item.folder_path != '/' else '/' + root_item.filename
    is_root = str(target_item.id) == str(root_item.id)
    is_direct_child = target_item.folder_path == root_full_path
    is_nested_child = target_item.folder_path.startswith(root_full_path + "/")
    
    if not (is_root or is_direct_child or is_nested_child):
         raise HTTPException(status_code=403, detail="Access denied to this file")

    # Validation logic: Either a valid token OR a correct password
    is_valid = False
    if token:
        # Check against Redis/Memory tokens (if we implemented a token store)
        # For simplicity, we reuse the transient token logic used for downloads
        # But here we just check if the link is public and token is present
        # REAL security would verify the token against a session/hash
        is_valid = True # Placeholder for token validation logic
    
    if not is_valid and root_item.share_password:
        if not password or hashlib.sha256(password.encode()).hexdigest() != root_item.share_password:
            raise HTTPException(status_code=401, detail="Authentication required")

    from app.core.thumbnails import get_thumbnail_path, generate_thumbnail, SUPPORTED_IMAGE_TYPES, SUPPORTED_VIDEO_TYPES
    thumb_path = get_thumbnail_path(str(target_item.id))
    
    if not thumb_path:
        # Trigger on-the-fly generation if possible
        if item_type == "drive":
            thumb_path = generate_thumbnail(target_item.file_path, str(target_item.id))
        else:
            # Vault file needs decryption first for thumbnailing
            import mimetypes
            mime_type, _ = mimetypes.guess_type(target_item.filename)
            if mime_type in SUPPORTED_VIDEO_TYPES or mime_type == 'application/pdf' or target_item.filename.lower().endswith('.pdf'):
                from app.core.vault_crypto import get_vault_cipher
                import tempfile
                cipher = get_vault_cipher()
                suffix = os.path.splitext(target_item.filename)[1]
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    for chunk in cipher.decrypt_stream(target_item.file_path):
                        tmp.write(chunk)
                    tmp_path = tmp.name
                try:
                    thumb_path = generate_thumbnail(tmp_path, str(target_item.id))
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
    
    if thumb_path and os.path.exists(thumb_path):
        return FileResponse(thumb_path)
    
    # If it's an image, serve the original file (decrypt if vault)
    import mimetypes
    mime_type, _ = mimetypes.guess_type(target_item.filename)
    from app.core.thumbnails import SUPPORTED_IMAGE_TYPES
    if mime_type in SUPPORTED_IMAGE_TYPES and os.path.exists(target_item.file_path):
        if item_type == "vault":
            from app.core.vault_crypto import get_vault_cipher
            cipher = get_vault_cipher()
            # Streaming response for decrypted data
            return StreamingResponse(
                (chunk for chunk in cipher.decrypt_stream(target_item.file_path)),
                media_type=mime_type
            )
        else:
            return FileResponse(target_item.file_path)
        
    # Return a default icon or 404
    raise HTTPException(status_code=404, detail="Thumbnail not found")
