from mongoengine import Document, StringField, IntField, DateTimeField, ReferenceField, FloatField, ListField, DictField, BooleanField
from datetime import datetime
from .user import User

class APIEndpoint(Document):
    """API endpoint configuration for external services"""
    
    # Basic info
    name = StringField(required=True, max_length=100)
    description = StringField()
    endpoint_url = StringField(required=True, max_length=500)
    method = StringField(choices=['GET', 'POST', 'PUT', 'DELETE'], default='POST')
    
    # Authentication
    api_key = StringField(max_length=500)  # Encrypted API key
    auth_type = StringField(choices=['NONE', 'API_KEY', 'BEARER_TOKEN', 'BASIC_AUTH'], default='API_KEY')
    
    # Request configuration
    headers = DictField()  # Custom headers
    request_template = DictField()  # Template for request body
    
    # Response handling
    success_criteria = DictField()  # How to determine success
    response_mapping = DictField()  # How to map response fields
    
    # Cost and billing
    cost_kpi = IntField(default=0)  # KPI cost per request
    cost_currency = FloatField(default=0.0)  # Real currency cost
    
    # Status
    is_active = BooleanField(default=True)
    is_public = BooleanField(default=False)  # Available to all users
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    created_by = ReferenceField(User)
    
    meta = {
        'collection': 'api_endpoints',
        'indexes': [
            'name',
            'is_active',
            'is_public',
            'created_by'
        ]
    }
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'endpoint_url': self.endpoint_url,
            'method': self.method,
            'auth_type': self.auth_type,
            'headers': self.headers,
            'request_template': self.request_template,
            'success_criteria': self.success_criteria,
            'response_mapping': self.response_mapping,
            'cost_kpi': self.cost_kpi,
            'cost_currency': self.cost_currency,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': str(self.created_by.id) if self.created_by else None
        }

class Order(Document):
    """Order for external API services"""
    
    # Order details
    order_type = StringField(required=True, max_length=50)  # 'API_CALL', 'SERVICE', 'PRODUCT'
    service_name = StringField(required=True, max_length=100)
    
    # API endpoint reference (if applicable)
    api_endpoint = ReferenceField(APIEndpoint)
    
    # User and request
    user = ReferenceField(User, required=True)
    request_data = DictField()  # Data sent with the request
    
    # Status tracking
    status = StringField(choices=['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED'], default='PENDING')
    
    # Cost information
    cost_kpi = IntField(default=0)
    cost_currency = FloatField(default=0.0)
    paid_kpi = IntField(default=0)
    paid_currency = FloatField(default=0.0)
    
    # Response information
    response_data = DictField()  # Response from external service
    error_message = StringField()
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField()
    
    # Processing info
    processing_duration_seconds = FloatField(default=0.0)
    retry_count = IntField(default=0)
    
    meta = {
        'collection': 'orders',
        'indexes': [
            'user',
            'status',
            'order_type',
            'created_at',
            ('user', 'status'),
            ('user', 'created_at')
        ]
    }
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': str(self.id),
            'order_type': self.order_type,
            'service_name': self.service_name,
            'api_endpoint_id': str(self.api_endpoint.id) if self.api_endpoint else None,
            'user_id': str(self.user.id),
            'request_data': self.request_data,
            'status': self.status,
            'cost_kpi': self.cost_kpi,
            'cost_currency': self.cost_currency,
            'paid_kpi': self.paid_kpi,
            'paid_currency': self.paid_currency,
            'response_data': self.response_data,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'processing_duration_seconds': self.processing_duration_seconds,
            'retry_count': self.retry_count
        }
