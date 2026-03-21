from mongoengine import Document, EmbeddedDocument, StringField, IntField, ListField, ReferenceField, DictField, BooleanField, DateTimeField, BinaryField, FloatField
from datetime import datetime
from .shop import ShopItem

class User(Document):
    username = StringField(primary_key=True, max_length=50)
    password_hash = StringField(max_length=255, required=True)
    role = StringField(choices=('OP', 'AD', 'USER'), required=True)
    status = StringField(choices=('PENDING', 'ACTIVE', 'DECLINED'), default='PENDING')
    
    # Profile fields
    display_name = StringField(max_length=100)
    email = StringField(max_length=255)
    avatar_url = StringField(max_length=500)
    banner_url = StringField(max_length=500)
    
    # Extended Profile
    bio = StringField(max_length=1000)
    phone = StringField(max_length=20)
    location = StringField(max_length=100)
    website = StringField(max_length=255)
    
    # Currency and Gaming
    kpi_current = IntField(default=0)
    kpi_lifetime = IntField(default=0)
    inventory = ListField(DictField())
    equipped_items = DictField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField()
    # Credentials and API keys
    personal_api_key = StringField(max_length=255)
    api_dollar_balance = FloatField(default=0.0)
    
    # Email Credentials (IMAP)
    email_creds = DictField()  # { 'email': '...', 'password': '...' }
    
    # AI Providers
    ai_providers = ListField(DictField())  # [ { 'type': 'openai', 'api_key': '...' }, ... ]
    
    meta = {
        'collection': 'user',
        'strict': False,
        'auto_create_index': False,
        'indexes': [
            {'fields': ['username'], 'unique': True}
        ]
    }
