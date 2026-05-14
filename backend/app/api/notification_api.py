from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.notification import Notification
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/notifications")
async def get_notifications(current_user: User = Depends(get_current_user)):
    """Retrieve recent notifications for the user"""
    notifications = Notification.objects(user_id=current_user.username).order_by('-created_at').limit(50)
    return [
        {
            "id": str(n.id),
            "message": n.message,
            "type": n.type,
            "link": n.link,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat()
        }
        for n in notifications
    ]

@router.put("/notifications/{notif_id}/read")
async def mark_as_read(notif_id: str, current_user: User = Depends(get_current_user)):
    """Mark a notification as read"""
    notif = Notification.objects(id=notif_id, user_id=current_user.username).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    notif.save()
    return {"message": "Marked as read"}

@router.delete("/notifications/{notif_id}")
async def delete_notification(notif_id: str, current_user: User = Depends(get_current_user)):
    """Delete a notification"""
    notif = Notification.objects(id=notif_id, user_id=current_user.username).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.delete()
    return {"message": "Deleted"}

@router.get("/notifications/unread/count")
async def get_unread_count(current_user: User = Depends(get_current_user)):
    """Get the count of unread notifications"""
    count = Notification.objects(user_id=current_user.username, is_read=False).count()
    return {"count": count}
