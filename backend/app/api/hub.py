from fastapi import APIRouter, HTTPException, Depends
from app.models.chat import ChatRoom, ChatMessage, PrivateMessage
from app.models.user import User
from app.services.chat_service import get_chat_service
from app.api.auth import get_current_user
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

# Pydantic models for requests
class CreateRoomRequest(BaseModel):
    name: str
    description: str = ""
    room_type: str = "GENERAL"
    members: List[str] = []

class SendMessageRequest(BaseModel):
    content: str
    message_type: str = "TEXT"
    file_attachments: List[str] = []

class InviteUserRequest(BaseModel):
    username: str

class PrivateMessageRequest(BaseModel):
    recipient_id: str
    content: str
    message_type: str = "TEXT"
    file_attachments: List[str] = []

# REST API endpoints for chat
@router.post("/rooms")
async def create_room(
    request: CreateRoomRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new chat room"""
    
    chat_service = get_chat_service()
    
    # Validate room type
    valid_types = ['GENERAL', 'PROJECT', 'PRIVATE', 'ANNOUNCEMENT']
    if request.room_type not in valid_types:
        raise HTTPException(status_code=400, detail="Invalid room type")
    
    # Get members if provided
    members = []
    if request.members:
        members = User.objects(id__in=request.members)
    
    room = chat_service.create_room(
        name=request.name,
        creator=current_user,
        room_type=request.room_type,
        description=request.description,
        members=members
    )
    
    return room.to_dict()

@router.get("/rooms")
async def get_user_rooms(
    current_user: User = Depends(get_current_user)
):
    """Get all rooms for current user"""
    
    chat_service = get_chat_service()
    rooms = chat_service.get_user_rooms(current_user)
    
    return [room.to_dict() for room in rooms]

@router.get("/rooms/{room_id}")
async def get_room_details(
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get room details"""
    
    room = ChatRoom.objects(id=room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if user is member
    if current_user not in room.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return room.to_dict()

@router.post("/rooms/{room_id}/join")
async def join_room(
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    """Join a room"""
    
    room = ChatRoom.objects(id=room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    chat_service = get_chat_service()
    success = chat_service.join_room(current_user, room)
    
    if success:
        return {"message": "Joined room successfully"}
    else:
        return {"message": "Already a member"}

@router.post("/rooms/{room_id}/leave")
async def leave_room(
    room_id: str,
    current_user: User = Depends(get_current_user)
):
    """Leave a room"""
    
    room = ChatRoom.objects(id=room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    chat_service = get_chat_service()
    success = chat_service.leave_room(current_user, room)
    
    if success:
        return {"message": "Left room successfully"}
    else:
        return {"message": "Not a member"}

@router.post("/rooms/{room_id}/invite")
async def invite_to_room(
    room_id: str,
    request: InviteUserRequest,
    current_user: User = Depends(get_current_user)
):
    """Invite a user to a room"""
    room = ChatRoom.objects(id=room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    # Only admins can invite? Let's check permissions
    if current_user not in room.admins:
        raise HTTPException(status_code=403, detail="Only admins can invite members")
        
    user_to_invite = User.objects(username=request.username).first()
    if not user_to_invite:
        # Try display name search if username not found exactly
        user_to_invite = User.objects(display_name=request.username).first()
        
    if not user_to_invite:
        raise HTTPException(status_code=404, detail="User not found")
        
    chat_service = get_chat_service()
    success = chat_service.invite_to_room(user_to_invite, room)
    
    if success:
        return {"message": f"Invited {user_to_invite.username} successfully"}
    else:
        return {"message": "User already in room"}

@router.get("/rooms/{room_id}/messages")
async def get_room_messages(
    room_id: str,
    limit: int = 50,
    before: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get messages from room"""
    
    room = ChatRoom.objects(id=room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if user is member
    if current_user not in room.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    chat_service = get_chat_service()
    
    before_date = None
    if before:
        try:
            before_date = datetime.fromisoformat(before)
        except:
            pass
    
    messages = chat_service.get_room_messages(room, limit, before_date)
    
    return [msg.to_dict(include_sender_info=True) for msg in messages]

@router.post("/rooms/{room_id}/messages")
async def send_room_message(
    room_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """Send message to room"""
    
    room = ChatRoom.objects(id=room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if user is member
    if current_user not in room.members:
        raise HTTPException(status_code=403, detail="Access denied")
    
    chat_service = get_chat_service()
    message = chat_service.send_room_message(
        room=room,
        sender=current_user,
        content=request.content,
        message_type=request.message_type,
        file_attachments=request.file_attachments
    )
    
    return message.to_dict(include_sender_info=True)

@router.get("/conversations/{user_id}")
async def get_private_conversation(
    user_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get private conversation with another user"""
    
    other_user = User.objects(id=user_id).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    chat_service = get_chat_service()
    messages = chat_service.get_private_conversation(current_user, other_user, limit)
    
    return [msg.to_dict(include_sender_info=True) for msg in messages]

@router.post("/messages/private")
async def send_private_message(
    request: PrivateMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """Send private message"""
    
    recipient = User.objects(id=request.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    chat_service = get_chat_service()
    message = chat_service.send_private_message(
        sender=current_user,
        recipient=recipient,
        content=request.content,
        message_type=request.message_type,
        file_attachments=request.file_attachments
    )
    
    return message.to_dict(include_sender_info=True)

@router.get("/users/online")
async def get_online_users(
    current_user: User = Depends(get_current_user)
):
    """Get list of online users"""
    
    chat_service = get_chat_service()
    online_user_ids = chat_service.get_online_users()
    
    # Get user details
    online_users = User.objects(id__in=online_user_ids)
    
    return [{
        'id': str(user.id),
        'username': user.username,
        'display_name': user.display_name,
        'role': user.role
    } for user in online_users]

@router.get("/users/search")
async def search_users(
    q: str,
    current_user: User = Depends(get_current_user)
):
    """Search for users by username or display name"""
    if len(q) < 2:
        return []
        
    from mongoengine.queryset.visitor import Q
    users = User.objects(
        Q(username__icontains=q) | Q(display_name__icontains=q)
    ).limit(20)
    
    return [
        {
            "id": str(u.id),
            "username": u.username,
            "display_name": u.display_name or u.username,
            "avatar_url": u.avatar_url
        }
        for u in users
    ]

@router.get("/search")
async def search_messages(
    q: str,
    room_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Search messages"""
    
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
    
    chat_service = get_chat_service()
    results = chat_service.search_messages(current_user, q.strip(), room_id)
    
    return {
        'query': q.strip(),
        'results': results,
        'count': len(results)
    }
