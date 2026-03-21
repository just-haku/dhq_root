from mongoengine import Document, StringField, ListField, ReferenceField, DateTimeField
from datetime import datetime
from .user import User

class PromptTemplate(Document):
    """Model for managing AI response prompts"""
    user = ReferenceField(User, required=True)
    name = StringField(max_length=100, required=True)
    description = StringField(max_length=500)
    category = StringField(choices=('General', 'Collaboration', 'Product', 'Refusal', 'Negotiation'), default='Collaboration')
    
    content = StringField(max_length=5000, required=True)
    variables = ListField(StringField()) # List of prompt variables like {{collaborator_name}}
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'prompt_templates',
        'indexes': [
            'user',
            'category',
            'name'
        ]
    }
