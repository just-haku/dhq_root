from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, BooleanField, IntField, EmbeddedDocumentField, BinaryField
from datetime import datetime
from .user import User

class ChatRoom(Document):
    """Chat room model for group conversations"""
    
    name = StringField(required=True, max_length=100)
    description = StringField(max_length=500)
    room_type = StringField(choices=['GENERAL', 'PROJECT', 'PRIVATE', 'ANNOUNCEMENT'], default='GENERAL')
    
    # Room members and permissions
    members = ListField(ReferenceField(User))
    admins = ListField(ReferenceField(User))
    is_private = BooleanField(default=False)
    invite_code = StringField(max_length=20)  # For private rooms
    
    # Metadata
    created_by = ReferenceField(User, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    last_activity = DateTimeField(default=datetime.utcnow)
    is_active = BooleanField(default=True)
    
    # Message count
    message_count = IntField(default=0)
    
    meta = {
        'collection': 'chat_rooms',
        'indexes': [
            'members',
            'room_type',
            'created_at',
            'last_activity'
        ]
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'room_type': self.room_type,
            'is_private': self.is_private,
            'member_count': len(self.members),
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'message_count': self.message_count
        }

class ChatMessage(Document):
    """Chat message model"""
    
    # Message content
    content = StringField(required=True)
    message_type = StringField(choices=['TEXT', 'FILE', 'IMAGE', 'SYSTEM'], default='TEXT')
    
    # Relationships
    room = ReferenceField(ChatRoom, required=True)
    sender = ReferenceField(User, required=True)
    
    # Message metadata
    timestamp = DateTimeField(default=datetime.utcnow)
    edited_at = DateTimeField()
    is_edited = BooleanField(default=False)
    is_deleted = BooleanField(default=False)
    
    # File attachments
    file_attachments = ListField(StringField())  # File IDs from Vault
    
    # Reactions and replies
    reactions = ListField(StringField())  # Simple emoji reactions
    reply_to = ReferenceField('self')  # For threaded conversations
    
    # Read receipts
    read_by = ListField(ReferenceField(User))
    
    meta = {
        'collection': 'chat_messages',
        'indexes': [
            'room',
            'sender',
            'timestamp',
            ('room', 'timestamp')
        ]
    }
    
    def to_dict(self, include_sender_info=False):
        result = {
            'id': str(self.id),
            'content': self.content,
            'message_type': self.message_type,
            'room_id': str(self.room.id),
            'sender_id': str(self.sender.id),
            'timestamp': self.timestamp.isoformat(),
            'is_edited': self.is_edited,
            'is_deleted': self.is_deleted,
            'file_attachments': self.file_attachments,
            'reactions': self.reactions,
            'read_by_count': len(self.read_by)
        }
        
        if include_sender_info:
            result['sender'] = {
                'username': self.sender.username,
                'display_name': self.sender.display_name,
                'role': self.sender.role
            }
            
        if self.edited_at:
            result['edited_at'] = self.edited_at.isoformat()
            
        return result

class PrivateMessage(Document):
    """Private message between two users"""
    
    # Message content
    content = StringField(required=True)
    message_type = StringField(choices=['TEXT', 'FILE', 'IMAGE'], default='TEXT')
    
    # Participants
    sender = ReferenceField(User, required=True)
    recipient = ReferenceField(User, required=True)
    
    # Metadata
    timestamp = DateTimeField(default=datetime.utcnow)
    is_edited = BooleanField(default=False)
    is_deleted = BooleanField(default=False)
    is_read = BooleanField(default=False)
    read_at = DateTimeField()
    
    # File attachments
    file_attachments = ListField(StringField())
    
    meta = {
        'collection': 'private_messages',
        'indexes': [
            ('sender', 'recipient'),
            ('recipient', 'timestamp'),
            'timestamp'
        ]
    }
    
    def to_dict(self, include_sender_info=True):
        result = {
            'id': str(self.id),
            'content': self.content,
            'message_type': self.message_type,
            'sender_id': str(self.sender.id),
            'recipient_id': str(self.recipient.id),
            'timestamp': self.timestamp.isoformat(),
            'is_edited': self.is_edited,
            'is_deleted': self.is_deleted,
            'is_read': self.is_read,
            'file_attachments': self.file_attachments
        }
        
        if include_sender_info:
            result['sender'] = {
                'username': self.sender.username,
                'display_name': self.sender.display_name,
                'role': self.sender.role
            }
            
        if self.read_at:
            result['read_at'] = self.read_at.isoformat()
            
        return result

class AIChatSession(Document):
    user = ReferenceField(User, required=True)
    title = StringField(max_length=255, required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'ai_chat_sessions',
        'indexes': ['user']
    }

class AIChatMessage(Document):
    session = ReferenceField(AIChatSession, required=True, reverse_delete_rule=2)
    role = StringField(choices=('user', 'assistant', 'system', 'tool'), required=True)
    content = StringField(required=True)
    timestamp = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'ai_chat_messages',
        'indexes': ['session']
    }

class UserAPIKey(Document):
    user = ReferenceField(User, required=True)
    provider_name = StringField(required=True) # e.g. openai, anthropic, deepseek, civitai
    encrypted_key = BinaryField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'user_api_keys',
        'indexes': [
            {'fields': ['user', 'provider_name'], 'unique': True}
        ]
    }
