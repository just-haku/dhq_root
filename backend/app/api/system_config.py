from fastapi import APIRouter, Depends, HTTPException, Header
from app.models.user import User
from app.models.system import SystemConfig
from app.api.auth import get_op_user, get_language
from app.socketio_server import sio
from datetime import datetime
from pydantic import BaseModel

class FeatureUpdate(BaseModel):
    ps_disable_ai: bool
    ps_disable_uploads: bool
    ps_disable_gcode: bool

router = APIRouter()

@router.get("/config")
async def get_system_config():
    config = SystemConfig.get_config()
    return {
        "power_mode": config.power_mode, 
        "last_updated": config.last_updated.isoformat(),
        "ps_disable_ai": config.ps_disable_ai,
        "ps_disable_uploads": config.ps_disable_uploads,
        "ps_disable_gcode": config.ps_disable_gcode
    }

@router.put("/mode")
async def update_working_mode(mode: str, current_user: User = Depends(get_op_user)):
    """Manually update the system power mode (OP only)"""
    if mode not in ["normal", "power_saver"]:
        raise HTTPException(status_code=400, detail="Invalid mode")
        
    config = SystemConfig.get_config()
    
    if config.power_mode != mode:
        config.power_mode = mode
        config.last_updated = datetime.utcnow()
        config.save()
        
        # Broadcast the change globally
        await sio.emit('power_mode_changed', {'mode': mode})
        
    return {"status": "success", "power_mode": config.power_mode}

@router.put("/features")
async def update_power_features(features: FeatureUpdate, current_user: User = Depends(get_op_user)):
    """Update granular power saver feature flags (OP only)"""
    config = SystemConfig.get_config()
    config.ps_disable_ai = features.ps_disable_ai
    config.ps_disable_uploads = features.ps_disable_uploads
    config.ps_disable_gcode = features.ps_disable_gcode
    config.last_updated = datetime.utcnow()
    config.save()
    
    # Broadcast to clients
    await sio.emit('power_features_changed', {
        'ps_disable_ai': config.ps_disable_ai,
        'ps_disable_uploads': config.ps_disable_uploads,
        'ps_disable_gcode': config.ps_disable_gcode
    })
    
    return {"status": "success"}

@router.get("/i18n-error")
async def test_i18n_error(lang: str = Depends(get_language)):
    """Example route returning a localized error message"""
    errors = {
        "en": "An unexpected error occurred while processing your request.",
        "vi": "Đã xảy ra lỗi không mong muốn trong quá trình xử lý yêu cầu của bạn."
    }
    raise HTTPException(status_code=400, detail=errors.get(lang, errors["en"]))
