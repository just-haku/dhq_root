from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.models.task import Task
from app.models.user import User
from app.api.auth import get_current_user
from app.core.notifications import send_notification
from datetime import datetime

router = APIRouter()

@router.get("/tasks", response_model=List[dict])
async def get_tasks(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Retrieve tasks for the current user or all tasks if Admin/OP"""
    query = {}
    if current_user.role not in ['AD', 'OP']:
        # Users see tasks they created or are assigned to
        from mongoengine import Q
        query = Q(creator=current_user) | Q(assignee=current_user)
    
    if status:
        if isinstance(query, dict):
            query['status'] = status
        else:
            query = query & Q(status=status)
            
    tasks = Task.objects(query).order_by('-created_at')
    return [
        {
            "id": str(t.id),
            "title": t.title,
            "description": t.description,
            "creator": t.creator.username,
            "assignee": t.assignee.username if t.assignee else None,
            "status": t.status,
            "priority": t.priority,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "created_at": t.created_at.isoformat()
        }
        for t in tasks
    ]

@router.post("/tasks")
async def create_task(
    title: str,
    description: Optional[str] = None,
    assignee_username: Optional[str] = None,
    priority: str = "MEDIUM",
    due_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user)
):
    """Create a new task"""
    assignee = None
    if assignee_username:
        assignee = User.objects(username=assignee_username).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")
            
    task = Task(
        title=title,
        description=description,
        creator=current_user,
        assignee=assignee,
        priority=priority,
        due_date=due_date
    )
    task.save()
    
    # Notify assignee if it's not the creator
    if assignee and assignee != current_user:
        import asyncio
        asyncio.create_task(send_notification(
            user_id=assignee.username,
            message=f"New task assigned: {title}",
            n_type="TASK",
            link="/tasks"
        ))
        
    return {"message": "Task created", "id": str(task.id)}

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: str,
    status: Optional[str] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Update task status or details"""
    task = Task.objects(id=task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Only creator, assignee, or Admin/OP can update
    if current_user.role not in ['AD', 'OP'] and \
       task.creator != current_user and \
       task.assignee != current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if status: task.status = status
    if description: task.description = description
    task.updated_at = datetime.utcnow()
    task.save()
    return {"message": "Task updated"}
