import os
import httpx
import base64
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.api.auth import get_current_user
from app.models.user import User
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# VirusTotal Configuration
VT_API_KEY = os.getenv("TOTAL_V_KEY")
VT_BASE_URL = "https://www.virustotal.com/api/v3"

def get_headers():
    if not VT_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="VirusTotal API key is not configured in .env (TOTAL_V_KEY)"
        )
    return {"x-apikey": VT_API_KEY}

@router.post("/url")
async def scan_url(
    url: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a URL for scanning to VirusTotal v3
    Returns an analysis ID used for polling results
    """
    headers = get_headers()
    data = {"url": url}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{VT_BASE_URL}/urls", headers=headers, data=data)
            if response.status_code != 200:
                error_data = response.json().get("error", {})
                logger.error(f"VT URL Scan Error: {error_data}")
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=error_data.get("message", "VirusTotal submission failed")
                )
            
            return response.json()
        except Exception as e:
            logger.error(f"VT API Exception: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/file")
async def scan_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a file for scanning to VirusTotal v3
    """
    headers = get_headers()
    
    # Read file content
    file_content = await file.read()
    files = {"file": (file.filename, file_content, file.content_type)}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Note: For files > 32MB, VT requires a special upload URL via /files/upload_url
            # For now, we handle small files directly
            response = await client.post(f"{VT_BASE_URL}/files", headers=headers, files=files)
            
            if response.status_code != 200:
                error_data = response.json().get("error", {})
                logger.error(f"VT File Scan Error: {error_data}")
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=error_data.get("message", "VirusTotal submission failed")
                )
            
            return response.json()
        except Exception as e:
            logger.error(f"VT API Exception: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{analysis_id}")
async def get_report(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get scan analysis report for a given analysis ID
    """
    headers = get_headers()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{VT_BASE_URL}/analyses/{analysis_id}", headers=headers)
            
            if response.status_code != 200:
                error_data = response.json().get("error", {})
                logger.error(f"VT Report Error: {error_data}")
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=error_data.get("message", "Failed to get scan report")
                )
            
            return response.json()
        except Exception as e:
            logger.error(f"VT API Exception: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/url-report/{url_base64}")
async def get_url_report(
    url_base64: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get existing report for a URL directly (using its URL ID)
    URL ID is base64 (without padding) of the URL
    """
    headers = get_headers()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{VT_BASE_URL}/urls/{url_base64}", headers=headers)
            
            if response.status_code != 200:
                error_data = response.json().get("error", {})
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=error_data.get("message", "Failed to get URL report")
                )
            
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
