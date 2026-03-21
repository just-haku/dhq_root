from mongoengine import Document, StringField, DateTimeField, ReferenceField, BooleanField, DictField
from datetime import datetime
from .user import User

class EmailMessage(Document):
    """Model to track fetched emails and avoid duplicates"""
    user = ReferenceField(User, required=True)
    message_id = StringField(required=True)  # IMAP Message-ID header
    uid = StringField() # IMAP Unique ID
    
    sender_name = StringField()
    sender_email = StringField()
    subject = StringField()
    body = StringField()
    
    is_collaboration = BooleanField(default=False)
    urgency = StringField(choices=('High', 'Medium', 'Normal'), default='Normal')
    
    # Extracted data from AI
    ai_data = DictField() # { scope, platform, price, etc. }
    
    status = StringField(choices=('Unprocessed', 'Collaboration', 'Skim', 'Junk'), default='Unprocessed')
    processed_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'email_messages',
        'indexes': [
            'user',
            'message_id',
            'status',
            'is_collaboration',
            '-processed_at'
        ]
    }
