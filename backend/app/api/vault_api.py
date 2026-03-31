from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse
from app.models.user import User
from app.api.auth import get_op_user
from app.models.vault import VaultFile
from app.core.vault_crypto import get_vault_cipher, CHUNK_SIZE
from app.core.storage import storage_service
import os
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import hashlib

class FolderCreate(BaseModel):
    name: str
    folder_path: str = "/"

async def apply_recursive_vault_access(parent_folder, access_level, permission_level, share_password, expires, allowed_users):
    """Recursively update access levels for all children in a vault folder"""
    # Calculate child path prefix
    if parent_folder.folder_path == "/":
        child_prefix = f"/{parent_folder.filename}/"
        direct_child_path = f"/{parent_folder.filename}"
    else:
        child_prefix = f"{parent_folder.folder_path.rstrip('/')}/{parent_folder.filename}/"
        direct_child_path = f"{parent_folder.folder_path.rstrip('/')}/{parent_folder.filename}"

    # Find all children recursively using folder_path prefix
    from mongoengine import Q
    query = Q(owner=parent_folder.owner, is_deleted=False) & (
        Q(folder_path=direct_child_path) | Q(folder_path__startswith=child_prefix)
    )
    
    children = VaultFile.objects(query)
    for child in children:
        child.access_level = access_level
        child.permission_level = permission_level
        child.share_password = share_password
        child.public_share_expires = expires
        child.allowed_users = allowed_users
        # For vault, we use a unique share_link_id per file if public, 
        # but for recursive simplicity, we might want them to share the same root share_id 
        # or have their own. If they are 'public', they need a share_link_id.
        if access_level != 'private' and not child.share_link_id:
            import secrets
            child.share_link_id = secrets.token_urlsafe(32)[:32]
        elif access_level == 'private':
            child.share_link_id = None
            
        child.save()

class VaultShareRequest(BaseModel):
    access_level: str = "private"  # "private", "internal", "public"
    permission_level: str = "viewer"  # "visitor", "viewer", "commenter", "editor"
    expires_hours: Optional[int] = None
    password: Optional[str] = None
    specific_usernames: List[str] = []

class VaultRenameRequest(BaseModel):
    file_id: str
    new_name: str

class ShareVerifyRequest(BaseModel):
    password: str

router = APIRouter()

@router.get("/nautilus/ping")
async def ping_vault():
    return {"status": "ok", "service": "secure-vault"}

@router.post("/nautilus/upload")
async def upload_to_vault(
    file: UploadFile = File(...),
    folder_path: str = Form("/"),
    current_user: User = Depends(get_op_user)
):
    """Encrypt and upload file to Vault (OP Only)"""
    primary_storage = storage_service.storages[0]
    vault_dir = os.path.join(primary_storage, "vault", str(current_user.id))
    os.makedirs(vault_dir, exist_ok=True)
    
    stored_filename = f"VLT_{uuid.uuid4().hex}"
    stored_path = os.path.join(vault_dir, stored_filename)
    
    temp_path = f"/tmp/{stored_filename}.tmp"
    try:
        with open(temp_path, "wb") as buffer:
            import shutil
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(temp_path)
        cipher = get_vault_cipher()
        cipher.encrypt_file(temp_path, stored_path)
        encrypted_size = os.path.getsize(stored_path)
        
        # Inherit access settings from parent folder
        parent_path = folder_path.rstrip('/') or '/'
        # To find parent folder object, we need to split path
        if folder_path != '/':
            parts = folder_path.strip('/').split('/')
            p_name = parts[-1]
            p_path = '/' + '/'.join(parts[:-1])
            if p_path == '//': p_path = '/'
            parent = VaultFile.objects(owner=current_user, filename=p_name, folder_path=p_path, is_folder=True).first()
            if parent:
                access_level = parent.access_level
                permission_level = parent.permission_level
                allowed_users = parent.allowed_users
                share_password = parent.share_password
                expires = parent.public_share_expires
            else:
                access_level = 'private'
                permission_level = 'viewer'
                allowed_users = []
                share_password = None
                expires = None
        else:
            access_level = 'private'
            permission_level = 'viewer'
            allowed_users = []
            share_password = None
            expires = None

        vfile = VaultFile(
            filename=file.filename,
            stored_filename=stored_filename,
            file_path=stored_path,
            mime_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            encrypted_size=encrypted_size,
            owner=current_user,
            folder_path=folder_path,
            access_level=access_level,
            permission_level=permission_level,
            allowed_users=allowed_users,
            share_password=share_password,
            public_share_expires=expires
        )
        if access_level != 'private':
            import secrets
            vfile.share_link_id = secrets.token_urlsafe(32)[:32]
        vfile.save()
        
        return {
            "message": "File encrypted and vaulted successfully",
            "file": vfile.to_dict()
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/nautilus/files")
async def list_vault_files(
    folder_path: str = Query("/"),
    filter: Optional[str] = Query(None),
    current_user: User = Depends(get_op_user)
):
    """List encrypted files in user's vault with filtering"""
    if filter == 'starred':
        files = VaultFile.objects(owner=current_user, is_starred=True, is_deleted=False).order_by('-created_at')
    elif filter == 'recent':
        files = VaultFile.objects(owner=current_user, is_deleted=False).order_by('-last_accessed')[:20]
    else:
        files = VaultFile.objects(owner=current_user, folder_path=folder_path, is_deleted=False).order_by('-is_folder', 'filename')
        
    return [f.to_dict() for f in files]

@router.post("/nautilus/mkdir")
async def create_vault_folder(
    data: FolderCreate,
    current_user: User = Depends(get_op_user)
):
    """Create a virtual folder entry in the Vault"""
    # Inherit access settings from parent folder
    if data.folder_path != '/':
        parts = data.folder_path.strip('/').split('/')
        p_name = parts[-1]
        p_path = '/' + '/'.join(parts[:-1])
        if p_path == '//': p_path = '/'
        parent = VaultFile.objects(owner=current_user, filename=p_name, folder_path=p_path, is_folder=True).first()
        if parent:
            access_level = parent.access_level
            permission_level = parent.permission_level
            allowed_users = parent.allowed_users
            share_password = parent.share_password
            expires = parent.public_share_expires
        else:
            access_level = 'private'
            permission_level = 'viewer'
            allowed_users = []
            share_password = None
            expires = None
    else:
        access_level = 'private'
        permission_level = 'viewer'
        allowed_users = []
        share_password = None
        expires = None

    vfolder = VaultFile(
        filename=data.name,
        stored_filename=f"DIR_{uuid.uuid4().hex}",
        file_path="VIRTUAL",
        mime_type="application/x-directory",
        file_size=0,
        owner=current_user,
        folder_path=data.folder_path,
        is_folder=True,
        access_level=access_level,
        permission_level=permission_level,
        allowed_users=allowed_users,
        share_password=share_password,
        public_share_expires=expires
    )
    if access_level != 'private':
        import secrets
        vfolder.share_link_id = secrets.token_urlsafe(32)[:32]
    vfolder.save()
    return vfolder.to_dict()

@router.patch("/nautilus/star/{file_id}")
async def toggle_vault_star(
    file_id: str,
    current_user: User = Depends(get_op_user)
):
    """Toggle starred status of a vault item"""
    vfile = VaultFile.objects(id=file_id, owner=current_user).first()
    if not vfile:
        raise HTTPException(status_code=404, detail="Item not found")
        
    vfile.is_starred = not vfile.is_starred
    vfile.save()
    return {"is_starred": vfile.is_starred}

@router.get("/nautilus/source/{file_id}")
async def download_from_vault(
    file_id: str,
    current_user: User = Depends(get_op_user)
):
    """Stream decrypt and download file from Vault"""
    vfile = VaultFile.objects(id=file_id, owner=current_user, is_deleted=False).first()
    if not vfile:
        raise HTTPException(status_code=404, detail="File not found")
    
    if vfile.is_folder:
        raise HTTPException(status_code=400, detail="Cannot download a folder")
        
    if not os.path.exists(vfile.file_path):
        raise HTTPException(status_code=404, detail="Physical file missing")
    
    vfile.last_accessed = datetime.utcnow()
    vfile.save()
    
    cipher = get_vault_cipher()
    return StreamingResponse(
        cipher.decrypt_stream(vfile.file_path),
        media_type=vfile.mime_type,
        headers={
            "Content-Disposition": f"inline; filename=\"{vfile.filename}\"",
            "Accept-Ranges": "bytes",
            "X-Stream-Type": "Encrypted-Media-Segment",
            "Cache-Control": "no-cache"
        }
    )

@router.get("/nautilus/thumbnail/{file_id}")
async def get_vault_thumbnail(
    file_id: str,
    current_user: User = Depends(get_op_user)
):
    """Get thumbnail for a vault file with decryption"""
    vfile = VaultFile.objects(id=file_id, owner=current_user, is_deleted=False).first()
    if not vfile:
        raise HTTPException(status_code=404, detail="File not found")
        
    from app.core.thumbnails import get_thumbnail_path, generate_thumbnail, SUPPORTED_IMAGE_TYPES, SUPPORTED_VIDEO_TYPES
    thumb_path = get_thumbnail_path(str(vfile.id), encrypted=True)
    
    if not thumb_path:
        # Trigger on-the-fly generation if possible
        import mimetypes
        mime_type, _ = mimetypes.guess_type(vfile.filename)
        if mime_type in SUPPORTED_VIDEO_TYPES or mime_type == 'application/pdf' or vfile.filename.lower().endswith('.pdf'):
            # Vault file needs decryption first for thumbnailing
            import tempfile
            cipher = get_vault_cipher()
            suffix = os.path.splitext(vfile.filename)[1]
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                for chunk in cipher.decrypt_stream(vfile.file_path):
                    tmp.write(chunk)
                tmp_path = tmp.name
            try:
                raw_thumb_path = generate_thumbnail(tmp_path, str(vfile.id))
                if raw_thumb_path and os.path.exists(raw_thumb_path):
                    enc_thumb_path = raw_thumb_path + ".enc"
                    cipher.encrypt_file(raw_thumb_path, enc_thumb_path)
                    os.remove(raw_thumb_path)
                    thumb_path = enc_thumb_path
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
    
    import mimetypes
    mime_type, _ = mimetypes.guess_type(vfile.filename)

    if thumb_path and os.path.exists(thumb_path):
        cipher = get_vault_cipher()
        return StreamingResponse(
            cipher.decrypt_stream(thumb_path),
            media_type="image/jpeg"
        )
    
    # If no thumbnail but it's an image, decrypt and serve original as thumbnail
    if mime_type in SUPPORTED_IMAGE_TYPES and os.path.exists(vfile.file_path):
        cipher = get_vault_cipher()
        return StreamingResponse(
            cipher.decrypt_stream(vfile.file_path),
            media_type=mime_type
        )
        
    raise HTTPException(status_code=404, detail="Thumbnail not available")

@router.get("/nautilus/file/{file_id}")
async def get_vault_file_metadata(
    file_id: str,
    current_user: User = Depends(get_op_user)
):
    """Fetch metadata for a single vault item"""
    item = VaultFile.objects(id=file_id, owner=current_user, is_deleted=False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item.to_dict()

@router.post("/nautilus/share/{file_id}")
async def share_vault_file(
    file_id: str,
    request: VaultShareRequest,
    current_user: User = Depends(get_op_user)
):
    """Enable and configure sharing for a vault file"""
    vfile = VaultFile.objects(id=file_id, owner=current_user).first()
    if not vfile:
        raise HTTPException(status_code=404, detail="File not found")
        
    # Block master root folder sharing
    # User's root vault is essentially folder_path='/' and filename='Vault' or similar?
    # In DHQ, the user's root is usually named after their username in storage, but in the virtual vault, 
    # if folder_path is '/' and filename is the user's base vault name, we block it.
    if vfile.is_folder and vfile.folder_path == "/":
         # Root folders are usually not allowed to be shared publicly to prevent full account exposure
         raise HTTPException(status_code=403, detail="Cannot share master root folder")

    vfile.access_level = request.access_level
    vfile.permission_level = request.permission_level
    
    share_password = None
    expires = None
    
    if request.access_level != "private":
        if not vfile.share_link_id:
            vfile.share_link_id = secrets.token_urlsafe(32)[:32]
            
        if request.expires_hours:
            expires = datetime.utcnow() + timedelta(hours=request.expires_hours)
            vfile.public_share_expires = expires
        else:
            vfile.public_share_expires = None
            
        if request.password:
            share_password = hashlib.sha256(request.password.encode()).hexdigest()
            vfile.share_password = share_password
        else:
            vfile.share_password = None
            
        if request.specific_usernames:
            from app.models.user import User as UserModel
            vfile.allowed_users = []
            for username in request.specific_usernames:
                target = UserModel.objects(username=username).first()
                if target:
                    vfile.allowed_users.append(target)
    else:
        vfile.share_link_id = None
        vfile.share_password = None
        vfile.public_share_expires = None
        vfile.allowed_users = []
        
    vfile.save()

    # Recursive update for folders
    if vfile.is_folder:
        await apply_recursive_vault_access(
            vfile, 
            vfile.access_level, 
            vfile.permission_level, 
            vfile.share_password,
            vfile.public_share_expires,
            vfile.allowed_users
        )
    return vfile.to_dict()

@router.get("/nautilus/s/{share_id}")
async def access_shared_vault_file(
    share_id: str,
    password: Optional[str] = Query(None)
):
    """Public access to shared encrypted vault file"""
    vfile = VaultFile.objects(share_link_id=share_id, is_deleted=False).first()
    if not vfile:
        raise HTTPException(status_code=404, detail="Shared link not found")
        
    # Check expiration
    if vfile.public_share_expires and datetime.utcnow() > vfile.public_share_expires:
        raise HTTPException(status_code=410, detail="Share link has expired")
        
    # Check password
    if vfile.share_password:
        if not password:
            return {"status": "password_required", "filename": vfile.filename}
            
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if password_hash != vfile.share_password:
            raise HTTPException(status_code=401, detail="Invalid password")
            
    # Success, stream decrypted
    if vfile.is_folder:
        raise HTTPException(status_code=400, detail="Cannot share folders currently")
        
    if not os.path.exists(vfile.file_path):
        raise HTTPException(status_code=404, detail="Physical file missing")
        
    vfile.last_accessed = datetime.utcnow()
    vfile.download_count += 1
    vfile.save()
    
    cipher = get_vault_cipher()
    mask_mime = "video/MP2T" if "video" in vfile.mime_type else "application/octet-stream"
    
    return StreamingResponse(
        cipher.decrypt_stream(vfile.file_path),
        media_type=mask_mime,
        headers={
            "Content-Disposition": f"attachment; filename=\"{vfile.filename}\"",
            "X-Content-Type-Options": "nosniff",
            "X-Stream-Type": "Encrypted-Media-Segment",
            "Cache-Control": "no-cache"
        }
    )

@router.post("/nautilus/v/{share_id}")
async def verify_share_password(
    share_id: str,
    request: ShareVerifyRequest
):
    """Verify password for a shared link before downloading"""
    vfile = VaultFile.objects(share_link_id=share_id, is_deleted=False).first()
    if not vfile:
        raise HTTPException(status_code=404, detail="Link not found")
        
    password_hash = hashlib.sha256(request.password.encode()).hexdigest()
    if password_hash == vfile.share_password:
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=401, detail="Invalid password")

@router.delete("/nautilus/purge/{file_id}")
async def delete_vault_file(
    file_id: str,
    current_user: User = Depends(get_op_user)
):
    """Permanently delete file or folder from Vault"""
    vfile = VaultFile.objects(id=file_id, owner=current_user).first()
    if not vfile:
        raise HTTPException(status_code=404, detail="File not found")
        
    if vfile.is_folder:
        folder_base = vfile.folder_path if vfile.folder_path != '/' else ''
        target_path = f"{folder_base}/{vfile.filename}"
        
        descendants = VaultFile.objects(
            owner=current_user,
            folder_path__startswith=target_path
        )
        for child in descendants:
            if not child.is_folder and os.path.exists(child.file_path):
                os.remove(child.file_path)
                from app.core.thumbnails import delete_thumbnail
                delete_thumbnail(str(child.id), encrypted=True)
            child.delete()
    else:
        if os.path.exists(vfile.file_path):
            os.remove(vfile.file_path)
            from app.core.thumbnails import delete_thumbnail
            delete_thumbnail(str(vfile.id), encrypted=True)
            
    vfile.delete()
    return {"message": "Vault item deleted permanently"}

@router.patch("/nautilus/rename")
async def rename_vault_file(
    request: VaultRenameRequest,
    current_user: User = Depends(get_op_user)
):
    """Rename a file or folder in Vault"""
    vfile = VaultFile.objects(id=request.file_id, owner=current_user).first()
    if not vfile:
        raise HTTPException(status_code=404, detail="File not found")
        
    vfile.filename = request.new_name
    vfile.save()
    return {"message": "Renamed successfully", "new_name": vfile.filename}
