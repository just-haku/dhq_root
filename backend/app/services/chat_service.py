from app.models.chat import ChatRoom, ChatMessage, PrivateMessage
from app.models.user import User
from app.core.database import redis_client
from app.services.encryption_service import get_encryption_service
from datetime import datetime, timedelta
import json
import secrets
from typing import List, Optional, Dict, Any

class ChatService:
    """Service for managing real-time chat functionality"""
    
    # Socket.IO connection management
    def __init__(self):
        self.connected_users = {}  # user_id -> socket_id
        self.user_sockets = {}    # socket_id -> user_id
        self.user_rooms = {}      # user_id -> list of room_ids
    
    def user_connected(self, user_id: str, socket_id: str):
        """Register user connection"""
        self.connected_users[user_id] = socket_id
        self.user_sockets[socket_id] = user_id
        
        # Set online status in Redis
        redis_client.set(f"user:{user_id}:online", "1", ex=300)  # 5 min timeout
        
        # Load user's rooms
        user = User.objects(id=user_id).first()
        if user:
            rooms = ChatRoom.objects(members=user)
            self.user_rooms[user_id] = [str(room.id) for room in rooms]
    
    def user_disconnected(self, socket_id: str):
        """Handle user disconnection"""
        if socket_id in self.user_sockets:
            user_id = self.user_sockets[socket_id]
            
            # Remove from tracking
            del self.connected_users[user_id]
            del self.user_sockets[socket_id]
            
            # Remove from Redis (go offline)
            redis_client.delete(f"user:{user_id}:online")
            
            # Clear room subscriptions
            if user_id in self.user_rooms:
                del self.user_rooms[user_id]
    
    def is_user_online(self, user_id: str) -> bool:
        """Check if user is online"""
        return redis_client.exists(f"user:{user_id}:online")
    
    def get_online_users(self) -> List[str]:
        """Get list of online user IDs"""
        pattern = "user:*:online"
        keys = redis_client.keys(pattern)
        return [key.decode().split(':')[1] for key in keys]
    
    # Room management
    def create_room(self, name: str, creator: User, room_type: str = 'GENERAL', 
                   description: str = "", members: List[User] = None) -> ChatRoom:
        """Create a new chat room"""
        
        if members is None:
            members = []
        
        # Add creator as member and admin
        if creator not in members:
            members.append(creator)
        
        room = ChatRoom(
            name=name,
            description=description,
            room_type=room_type,
            members=members,
            admins=[creator],
            created_by=creator,
            is_private=(room_type == 'PRIVATE')
        )
        
        # Generate invite code for private rooms
        if room_type == 'PRIVATE':
            room.invite_code = self._generate_invite_code()
        
        room.save()
        
        # Update user room subscriptions
        for member in members:
            user_id = str(member.id)
            if user_id not in self.user_rooms:
                self.user_rooms[user_id] = []
            self.user_rooms[user_id].append(str(room.id))
        
        return room
    
    def join_room(self, user: User, room: ChatRoom) -> bool:
        """Add user to room"""
        if user not in room.members:
            room.members.append(user)
            room.save()
            
            # Update user room subscriptions
            user_id = str(user.id)
            if user_id not in self.user_rooms:
                self.user_rooms[user_id] = []
            self.user_rooms[user_id].append(str(room.id))
            
            return True
        return False
    
    def leave_room(self, user: User, room: ChatRoom) -> bool:
        """Remove user from room"""
        if user in room.members:
            room.members.remove(user)
            
            # Remove from admins if applicable
            if user in room.admins:
                room.admins.remove(user)
            
            room.save()
            
            # Update user room subscriptions
            user_id = str(user.id)
            if user_id in self.user_rooms:
                room_id = str(room.id)
                if room_id in self.user_rooms[user_id]:
                    self.user_rooms[user_id].remove(room_id)
            
            return True
        return False
    
    def get_user_rooms(self, user: User) -> List[ChatRoom]:
        """Get all rooms user is member of. Creates General Chat if none found."""
        rooms = ChatRoom.objects(members=user).order_by('-last_activity')
        
        # Check if user has a General Chat
        has_general = any(r.name == "General Chat" for r in rooms)
        if not has_general:
            # Create individual General Chat
            general_room = self.create_room(
                name="General Chat",
                creator=user,
                room_type='GENERAL',
                description=f"Initial private workspace for {user.username}",
                members=[user]
            )
            # Re-fetch or add to list
            rooms = ChatRoom.objects(members=user).order_by('-last_activity')
            
        return rooms
    
    def invite_to_room(self, user_to_invite: User, room: ChatRoom) -> bool:
        """Invite a user to a room"""
        return self.join_room(user_to_invite, room)
    
    # Message management
    def send_room_message(self, room: ChatRoom, sender: User, content: str, 
                         message_type: str = 'TEXT', file_attachments: List[str] = None) -> ChatMessage:
        """Send message to room"""
        
        message = ChatMessage(
            content=content,
            message_type=message_type,
            room=room,
            sender=sender,
            file_attachments=file_attachments or []
        )
        
        message.save()
        
        # Update room activity
        room.last_activity = datetime.utcnow()
        room.message_count += 1
        room.save()
        
        return message
    
    def send_private_message(self, sender: User, recipient: User, content: str,
                           message_type: str = 'TEXT', file_attachments: List[str] = None) -> PrivateMessage:
        """Send private message"""
        
        message = PrivateMessage(
            content=content,
            message_type=message_type,
            sender=sender,
            recipient=recipient,
            file_attachments=file_attachments or []
        )
        
        message.save()
        
        return message
    
    def get_room_messages(self, room: ChatRoom, limit: int = 50, before: datetime = None) -> List[ChatMessage]:
        """Get messages from room with pagination"""
        query = ChatMessage.objects(room=room, is_deleted=False)
        
        if before:
            query = query.filter(timestamp__lt=before)
        
        return query.order_by('-timestamp').limit(limit)
    
    def get_private_conversation(self, user1: User, user2: User, limit: int = 50) -> List[PrivateMessage]:
        """Get private conversation between two users"""
        messages = PrivateMessage.objects(
            __raw__={
                '$or': [
                    {'sender': user1.id, 'recipient': user2.id},
                    {'sender': user2.id, 'recipient': user1.id}
                ],
                'is_deleted': False
            }
        ).order_by('-timestamp').limit(limit)
        
        return messages
    
    # Typing indicators
    def set_typing(self, user_id: str, room_id: str, is_typing: bool):
        """Set user typing status in room"""
        key = f"typing:{room_id}:{user_id}"
        
        if is_typing:
            redis_client.setex(key, 5, "1")  # 5 second timeout
        else:
            redis_client.delete(key)
    
    def get_typing_users(self, room_id: str) -> List[str]:
        """Get list of users currently typing in room"""
        pattern = f"typing:{room_id}:*"
        keys = redis_client.keys(pattern)
        return [key.decode().split(':')[2] for key in keys]
    
    # Search functionality
    def search_messages(self, user: User, query: str, room_id: str = None) -> List[Dict]:
        """Search messages user has access to"""
        results = []
        
        if room_id:
            # Search in specific room
            room = ChatRoom.objects(id=room_id).first()
            if room and user in room.members:
                messages = ChatMessage.objects(
                    room=room,
                    content__icontains=query,
                    is_deleted=False
                ).limit(50)
                
                for msg in messages:
                    results.append(msg.to_dict(include_sender_info=True))
        else:
            # Search in all user's rooms
            rooms = ChatRoom.objects(members=user)
            for room in rooms:
                messages = ChatMessage.objects(
                    room=room,
                    content__icontains=query,
                    is_deleted=False
                ).limit(20)
                
                for msg in messages:
                    results.append(msg.to_dict(include_sender_info=True))
        
        # Also search private messages
        private_messages = PrivateMessage.objects(
            __raw__={
                '$or': [
                    {'sender': user.id},
                    {'recipient': user.id}
                ],
                'content__icontains': query,
                'is_deleted': False
            }
        ).limit(20)
        
        for msg in private_messages:
            results.append(msg.to_dict(include_sender_info=True))
        
        # Sort by timestamp
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return results[:100]  # Limit to 100 results
    
    def _generate_invite_code(self) -> str:
        """Generate unique room invite code"""
        while True:
            code = secrets.token_urlsafe(8)[:12].upper()
            if not ChatRoom.objects(invite_code=code).first():
                return code

# Global chat service instance
chat_service = ChatService()

def get_chat_service() -> ChatService:
    """Get chat service instance"""
    return chat_service
