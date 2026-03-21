from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.models.prompt_library import PromptTemplate
from app.api.auth import get_current_user
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class PromptCreateRequest(BaseModel):
    name: str
    content: str
    description: Optional[str] = None
    category: Optional[str] = 'Collaboration'
    variables: Optional[List[str]] = []

class PromptUpdateRequest(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    variables: Optional[List[str]] = None

@router.get("/")
async def get_prompts(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """List all prompt templates for the current user"""
    query = {"user": current_user}
    if category:
        query["category"] = category
        
    prompts = PromptTemplate.objects(**query).order_by('name')
    return {"prompts": [p.to_dict() for p in prompts if hasattr(p, 'to_dict')] or [p.to_json() for p in prompts]}

@router.post("/")
async def create_prompt_template(
    request: PromptCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new prompt template"""
    prompt = PromptTemplate(
        user=current_user,
        name=request.name,
        content=request.content,
        description=request.description,
        category=request.category,
        variables=request.variables
    )
    prompt.save()
    return {"message": "Prompt template created", "prompt_id": str(prompt.id)}

@router.patch("/{prompt_id}")
async def update_prompt_template(
    prompt_id: str,
    request: PromptUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update an existing prompt template"""
    prompt = PromptTemplate.objects(id=prompt_id, user=current_user).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt template not found")
        
    if request.name: prompt.name = request.name
    if request.content: prompt.content = request.content
    if request.description: prompt.description = request.description
    if request.category: prompt.category = request.category
    if request.variables is not None: prompt.variables = request.variables
    
    prompt.updated_at = datetime.utcnow()
    prompt.save()
    return {"message": "Prompt template updated"}

@router.delete("/{prompt_id}")
async def delete_prompt_template(
    prompt_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a prompt template"""
    prompt = PromptTemplate.objects(id=prompt_id, user=current_user).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt template not found")
        
    prompt.delete()
    return {"message": "Prompt template deleted"}
