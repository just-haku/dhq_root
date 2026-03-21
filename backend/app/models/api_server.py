from mongoengine import Document, StringField, URLField, BooleanField, IntField, DateTimeField, FloatField
from datetime import datetime

class APIServer(Document):
    """Model for API servers that OP can configure"""
    
    meta = {'collection': 'api_servers'}
    
    # Basic info
    name = StringField(required=True, max_length=100, unique=True)
    display_name = StringField(required=True, max_length=200)
    base_url = URLField(required=True)
    
    # Configuration
    is_active = BooleanField(default=True)
    is_default = BooleanField(default=False)
    is_external = BooleanField(default=True)
    rate_per_1000 = FloatField(default=0.0)
    priority = IntField(default=1)  # Lower number = higher priority
    
    # API details
    api_key = StringField(max_length=255) # System default key for this server
    api_version = StringField(default="v2")
    supports_services = StringField(default="views,likes,comments")  # Comma-separated
    
    # Metadata
    description = StringField(max_length=500)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"{self.display_name} ({self.base_url})"

class UserAPIKey(Document):
    """Model for storing user API keys for different servers"""
    
    meta = {'collection': 'user_api_keys'}
    
    # Relations
    user_id = StringField(required=True)
    api_server_id = StringField(required=True)  # Reference to APIServer
    
    # API Key
    api_key = StringField(required=True, max_length=255)
    key_name = StringField(max_length=100)  # User-friendly name for the key
    
    # Status
    is_active = BooleanField(default=True)
    last_used = DateTimeField()
    usage_count = IntField(default=0)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f"API Key for user {self.user_id} on server {self.api_server_id}"
