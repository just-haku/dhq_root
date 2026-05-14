from mongoengine import Document, StringField, DateTimeField, BooleanField
from datetime import datetime

class Notification(Document):
    user_id = StringField(required=True) # Target username
    message = StringField(max_length=500, required=True)
    type = StringField(max_length=50, default='SYSTEM') # TASK, ORDER, COLLAB, SYSTEM
    link = StringField(max_length=500) # Optional link to related item
    
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'notifications',
        'indexes': ['user_id', 'is_read', 'created_at']
    }
