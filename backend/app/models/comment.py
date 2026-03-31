from mongoengine import Document, StringField, DateTimeField, ReferenceField
from app.models.user import User
from datetime import datetime

class Comment(Document):
    """Comment model for shared folders and files"""
    
    # Target can be a DriveFile ID or VaultFile ID (stored as string for flexibility)
    target_id = StringField(required=True)
    target_type = StringField(choices=['drive', 'vault'], required=True)
    
    # Author information
    user = ReferenceField(User)  # Optional (None for guest editors)
    guest_name = StringField()   # For non-authenticated comments if allowed
    
    # Content
    content = StringField(required=True)
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    modified_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'comments',
        'indexes': [
            'target_id',
            'created_at'
        ]
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user': {
                'id': str(self.user.id),
                'username': self.user.username,
                'display_name': self.user.display_name
            } if self.user else None,
            'guest_name': self.guest_name,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }
