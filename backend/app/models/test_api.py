from mongoengine import Document, StringField, BooleanField, DictField, DateTimeField, ReferenceField, IntField, FloatField
from datetime import datetime
from .user import User

class TestAPIConfig(Document):
    """Configuration for test API endpoints"""
    
    # Basic configuration
    name = StringField(required=True, max_length=100)
    description = StringField()
    
    # Test endpoint settings
    is_enabled = BooleanField(default=False)
    mock_responses = BooleanField(default=True)  # Use mock responses instead of real API
    intercept_growth_orders = BooleanField(default=False)  # Intercept growth order API calls
    
    # Real API configuration (when mock_responses is False)
    real_api_url = StringField(max_length=500)
    real_api_key = StringField(max_length=500)
    
    # Test response templates
    success_response = DictField(default=lambda: {"order": 99999})
    error_response = DictField(default=lambda: {"error": "Test error message"})
    
    # API command templates based on the images you provided
    add_order_template = DictField(
        default=lambda: {
            "key": "{api_key}",
            "action": "add",
            "service": "{service_id}",
            "link": "{link}",
            "quantity": "{quantity}"
        }
    )
    
    status_template = DictField(
        default=lambda: {
            "key": "{api_key}",
            "action": "status",
            "order": "{order_id}"
        }
    )
    
    balance_template = DictField(
        default=lambda: {
            "key": "{api_key}",
            "action": "balance"
        }
    )
    
    # Test behavior settings
    response_delay_ms = IntField(default=1000)  # Simulate API delay
    failure_rate_percent = IntField(default=0, min_value=0, max_value=100)  # Simulate failures
    
    # Logging
    log_requests = BooleanField(default=True)
    log_responses = BooleanField(default=True)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    created_by = ReferenceField(User)
    
    meta = {
        'collection': 'test_api_configs',
        'indexes': [
            'name',
            'is_enabled',
            'created_by'
        ]
    }
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'mock_responses': self.mock_responses,
            'intercept_growth_orders': self.intercept_growth_orders,
            'real_api_url': self.real_api_url,
            'real_api_key': '***' if self.real_api_key else None,  # Hide key in responses
            'success_response': self.success_response,
            'error_response': self.error_response,
            'add_order_template': self.add_order_template,
            'status_template': self.status_template,
            'balance_template': self.balance_template,
            'response_delay_ms': self.response_delay_ms,
            'failure_rate_percent': self.failure_rate_percent,
            'log_requests': self.log_requests,
            'log_responses': self.log_responses,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': str(self.created_by.id) if self.created_by else None
        }

class APILog(Document):
    """Log of API requests and responses"""
    
    # Request info
    endpoint_name = StringField(required=True, max_length=100)
    method = StringField(required=True, max_length=10)
    url = StringField(max_length=500)
    request_headers = DictField()
    request_body = DictField()
    
    # Response info
    response_status = IntField()
    response_headers = DictField()
    response_body = DictField()
    
    # Timing
    request_timestamp = DateTimeField(default=datetime.utcnow)
    response_timestamp = DateTimeField()
    duration_ms = FloatField()
    
    # User and context
    user = ReferenceField(User)
    order_id = StringField(max_length=100)
    
    # Test mode info
    is_test_mode = BooleanField(default=True)
    mock_response_used = BooleanField(default=False)
    
    meta = {
        'collection': 'api_logs',
        'indexes': [
            'endpoint_name',
            'request_timestamp',
            'user',
            'order_id',
            'is_test_mode'
        ]
    }
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': str(self.id),
            'endpoint_name': self.endpoint_name,
            'method': self.method,
            'url': self.url,
            'request_headers': self.request_headers,
            'request_body': self.request_body,
            'response_status': self.response_status,
            'response_headers': self.response_headers,
            'response_body': self.response_body,
            'request_timestamp': self.request_timestamp.isoformat(),
            'response_timestamp': self.response_timestamp.isoformat() if self.response_timestamp else None,
            'duration_ms': self.duration_ms,
            'user_id': str(self.user.id) if self.user else None,
            'order_id': self.order_id,
            'is_test_mode': self.is_test_mode,
            'mock_response_used': self.mock_response_used
        }
