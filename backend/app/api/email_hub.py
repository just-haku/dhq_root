from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.models.user import User
from app.models.email_message import EmailMessage
from app.models.collaboration import Collaboration, VideoUnit
from app.api.auth import get_current_user
from app.services.email_service import email_service
from app.services.ai_pipeline_service import ai_pipeline
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class DraftRequest(BaseModel):
    prompt_id: str

async def process_new_emails(user: User, emails: List[EmailMessage]):
    """Background task to run AI processing on new emails"""
    for email in emails:
        await ai_pipeline.process_email(user, email)

@router.get("/")
async def get_emails(
    status: Optional[str] = None,
    is_collaboration: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    """List processed emails for the current user"""
    query = {"user": current_user}
    if status:
        query["status"] = status
    if is_collaboration is not None:
        query["is_collaboration"] = is_collaboration
        
    emails = EmailMessage.objects(**query).order_by('-urgency', '-processed_at')
    return {"emails": [json.loads(e.to_json()) for e in emails]}

@router.post("/sync")
async def sync_emails(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Trigger IMAP fetch and background AI processing"""
    new_emails = email_service.fetch_emails(current_user, limit=20)
    
    if new_emails:
        # Run AI pipeline in background to avoid blocking the API
        background_tasks.add_task(process_new_emails, current_user, new_emails)
        
    return {"message": f"Sync started. Found {len(new_emails)} new emails.", "count": len(new_emails)}

@router.post("/{email_id}/convert")
async def convert_to_collaboration(
    email_id: str,
    current_user: User = Depends(get_current_user)
):
    """Manually convert an email into a Collaboration entry"""
    email_msg = EmailMessage.objects(id=email_id, user=current_user).first()
    if not email_msg:
        raise HTTPException(status_code=404, detail="Email not found")
        
    # Create Collaboration from AI extracted data
    data = email_msg.ai_data or {}
    
    collab = Collaboration(
        name=f"Collab: {data.get('scope', email_msg.subject)}",
        collaborator_name=data.get('collaborator_name', email_msg.sender_name or "Unknown"),
        collaborator_email=email_msg.sender_email,
        type="Paid" if data.get('price') != "###" else "Product",
        agreed_price=float(data.get('price')) if data.get('price', "###") != "###" else 0.0,
        platform=[data.get('platform', 'Not Specified')],
        scope=data.get('scope', 'Not Specified'),
        other_notes=f"Created from email: {email_msg.subject}\n\n{email_msg.body[:500]}...",
        status="On Going"
    )
    collab.save()
    
    email_msg.status = 'Collaboration'
    email_msg.save()
    
    return {"message": "Collaboration created", "collaboration_id": str(collab.id)}

@router.post("/{email_id}/draft")
async def generate_email_draft(
    email_id: str,
    request: DraftRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate an AI draft response for an email"""
    email_msg = EmailMessage.objects(id=email_id, user=current_user).first()
    if not email_msg:
        raise HTTPException(status_code=404, detail="Email not found")
        
    prompt_template = PromptTemplate.objects(id=request.prompt_id, user=current_user).first()
    if not prompt_template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
        
    draft = await ai_pipeline.generate_draft(current_user, email_msg, prompt_template)
    return {"draft": draft}

import json
