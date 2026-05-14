from mongoengine import Document, StringField, ReferenceField, DateTimeField
from datetime import datetime
from .user import User

class Task(Document):
    title = StringField(max_length=200, required=True)
    description = StringField(max_length=2000)
    creator = ReferenceField(User, required=True)
    assignee = ReferenceField(User) # If None, it's a self-task or unassigned
    
    status = StringField(
        choices=('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'),
        default='PENDING'
    )
    priority = StringField(
        choices=('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'),
        default='MEDIUM'
    )
    
    due_date = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'tasks',
        'indexes': ['assignee', 'creator', 'status', 'priority']
    }
