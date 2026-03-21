from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
import logging
import secrets
from app.models.api_server import APIServer, UserAPIKey
from app.models.user import User
from app.api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/servers")
async def get_api_servers(
    current_user: User = Depends(get_current_user)
):
    """Get all available API servers"""
    try:
        servers = APIServer.objects(is_active=True).order_by('priority', 'name')
        return {
            "success": True,
            "servers": [
                {
                    "id": str(server.id),
                    "name": server.name,
                    "display_name": server.display_name,
                    "base_url": server.base_url,
                    "api_version": server.api_version,
                    "supports_services": server.supports_services.split(','),
                    "description": server.description,
                    "is_default": server.is_default,
                    "priority": server.priority,
                    "is_active": server.is_active
                }
                for server in servers
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching API servers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch API servers")

@router.get("/user/api-keys")
async def get_user_api_keys(
    current_user: User = Depends(get_current_user)
):
    """Get current user's API keys"""
    try:
        user_keys = UserAPIKey.objects(user_id=str(current_user.id))
        api_keys = {}
        
        for key in user_keys:
            api_keys[key.api_server_id] = key.api_key
            
        return {
            "success": True,
            "api_keys": api_keys
        }
    except Exception as e:
        logger.error(f"Error fetching user API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch API keys")

@router.put("/user/api-keys")
async def update_user_api_key(
    key_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update or create user API key for a server"""
    try:
        server_id = key_data.get("server_id")
        api_key = key_data.get("api_key")
        
        if not server_id:
            raise HTTPException(status_code=400, detail="Server ID is required")
            
        # Check if server exists
        server = APIServer.objects(id=server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="API server not found")
        
        # Update or create the API key
        existing_key = UserAPIKey.objects(
            user_id=str(current_user.id), 
            api_server_id=server_id
        ).first()
        
        if existing_key:
            existing_key.api_key = api_key
            existing_key.updated_at = datetime.utcnow()
            existing_key.save()
        else:
            new_key = UserAPIKey(
                user_id=str(current_user.id),
                api_server_id=server_id,
                api_key=api_key,
                key_name=f"Key for {server.display_name}"
            )
            new_key.save()
        
        return {
            "success": True,
            "message": "API key updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to update API key")

@router.delete("/user/api-keys/{server_id}")
async def delete_api_key_by_server(
    server_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete user API key for a server"""
    try:
        key = UserAPIKey.objects(
            user_id=str(current_user.id), 
            api_server_id=server_id
        ).first()
        
        if not key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        key.delete()
        
        return {
            "success": True,
            "message": "API key deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete API key")

@router.post("/servers")
async def create_api_server(
    server_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new API server (OP only)"""
    try:
        # Check if user is OP (you might want to add role checking)
        # if not current_user.is_op:
        #     raise HTTPException(status_code=403, detail="OP access required")
        
        # Check for duplicate name
        if APIServer.objects(name=server_data['name']).first():
            raise HTTPException(status_code=400, detail="Server name already exists")
        
        # Create new server
        server = APIServer(
            name=server_data['name'],
            display_name=server_data['display_name'],
            base_url=server_data['base_url'],
            api_version=server_data.get('api_version', 'v2'),
            supports_services=server_data.get('supports_services', 'views,likes,comments'),
            description=server_data.get('description', ''),
            is_active=server_data.get('is_active', True),
            is_default=server_data.get('is_default', False),
            priority=server_data.get('priority', 1)
        )
        server.save()
        
        return {
            "success": True,
            "message": "API server created successfully",
            "server_id": str(server.id)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating API server: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API server")

@router.put("/servers/{server_id}")
async def update_api_server(
    server_id: str,
    server_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update an API server (OP only)"""
    try:
        server = APIServer.objects(id=server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="API server not found")
        
        # Update fields
        if 'display_name' in server_data:
            server.display_name = server_data['display_name']
        if 'base_url' in server_data:
            server.base_url = server_data['base_url']
        if 'api_version' in server_data:
            server.api_version = server_data['api_version']
        if 'supports_services' in server_data:
            server.supports_services = server_data['supports_services']
        if 'description' in server_data:
            server.description = server_data['description']
        if 'is_active' in server_data:
            server.is_active = server_data['is_active']
        if 'is_default' in server_data:
            # If setting as default, unset others
            if server_data['is_default']:
                APIServer.objects(is_default=True).update(is_default=False)
            server.is_default = server_data['is_default']
        if 'priority' in server_data:
            server.priority = server_data['priority']
        
        server.updated_at = datetime.utcnow()
        server.save()
        
        return {
            "success": True,
            "message": "API server updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating API server: {e}")
        raise HTTPException(status_code=500, detail="Failed to update API server")

@router.delete("/servers/{server_id}")
async def delete_api_server(
    server_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an API server (OP only)"""
    try:
        server = APIServer.objects(id=server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="API server not found")
        
        # Also delete associated user API keys
        UserAPIKey.objects(api_server_id=server_id).delete()
        
        server.delete()
        
        return {
            "success": True,
            "message": "API server deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting API server: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete API server")

@router.get("/user-keys")
async def get_user_api_keys(
    current_user: User = Depends(get_current_user)
):
    """Get current user's API keys"""
    try:
        keys = UserAPIKey.objects(user_id=str(current_user.id), is_active=True)
        
        # Get server details for each key
        result = []
        for key in keys:
            server = APIServer.objects(id=key.api_server_id).first()
            if server:
                result.append({
                    "id": str(key.id),
                    "api_server_id": key.api_server_id,
                    "server_name": server.display_name,
                    "server_base_url": server.base_url,
                    "key_name": key.key_name or f"Key for {server.display_name}",
                    "api_key": f"{key.api_key[:4]}••••••••",
                    "last_used": key.last_used.isoformat() if key.last_used else None,
                    "usage_count": key.usage_count,
                    "created_at": key.created_at.isoformat()
                })
        
        return {
            "success": True,
            "keys": result
        }
    except Exception as e:
        logger.error(f"Error fetching user API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch API keys")

@router.post("/internal-token/regenerate")
async def regenerate_user_internal_token(
    current_user: User = Depends(get_current_user)
):
    """Generate or regenerate an API key for the Internal API Server"""
    try:
        # Find internal server
        server = APIServer.objects(name='internal_api_server').first()
        if not server:
            raise HTTPException(status_code=404, detail="Internal API server not configured")
        
        # Generate new 32-char key
        new_key = secrets.token_hex(16)
        
        # Update or create
        existing_key = UserAPIKey.objects(
            user_id=str(current_user.id),
            api_server_id=str(server.id)
        ).first()
        
        if existing_key:
            existing_key.api_key = new_key
            existing_key.updated_at = datetime.utcnow()
            existing_key.save()
        else:
            UserAPIKey(
                user_id=str(current_user.id),
                api_server_id=str(server.id),
                api_key=new_key,
                key_name="Internal API Key"
            ).save()
            
        return {
            "success": True,
            "api_key": new_key,
            "message": "Internal API key regenerated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating internal API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to regenerate key")

@router.post("/user-keys")
async def create_user_api_key(
    key_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create or update user API key"""
    try:
        # Check if server exists
        server = APIServer.objects(id=key_data['api_server_id']).first()
        if not server:
            raise HTTPException(status_code=404, detail="API server not found")
        
        # Check if key already exists for this server
        existing_key = UserAPIKey.objects(
            user_id=str(current_user.id),
            api_server_id=key_data['api_server_id']
        ).first()
        
        if existing_key:
            # Update existing key
            existing_key.api_key = key_data['api_key']
            existing_key.key_name = key_data.get('key_name', '')
            existing_key.updated_at = datetime.utcnow()
            existing_key.save()
            
            return {
                "success": True,
                "message": "API key updated successfully"
            }
        else:
            # Create new key
            key = UserAPIKey(
                user_id=str(current_user.id),
                api_server_id=key_data['api_server_id'],
                api_key=key_data['api_key'],
                key_name=key_data.get('key_name', '')
            )
            key.save()
            
            return {
                "success": True,
                "message": "API key saved successfully"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving user API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to save API key")

@router.delete("/user-keys/{key_id}")
async def delete_api_key_by_id(
    key_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete user API key"""
    try:
        key = UserAPIKey.objects(
            id=key_id,
            user_id=str(current_user.id)
        ).first()
        
        if not key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        key.delete()
        
        return {
            "success": True,
            "message": "API key deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete API key")
