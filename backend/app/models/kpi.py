from mongoengine import Document, StringField, IntField, DateTimeField, ReferenceField, FloatField
from datetime import datetime
from .user import User

class KPIHistory(Document):
    """Track KPI point changes and history"""
    
    # User reference
    user = ReferenceField(User, required=True)
    
    # Transaction details
    amount = IntField(required=True)  # Positive for gains, negative for losses
    balance_after = IntField(required=True)  # Balance after this transaction
    
    # Source and reason
    source = StringField(required=True, max_length=100)  # 'daily_bonus', 'game_win', 'game_cost', 'admin_adjustment', etc.
    reason = StringField(max_length=500)  # Detailed description
    
    # Related entity (optional)
    related_entity_type = StringField(max_length=50)  # 'game', 'task', 'project', etc.
    related_entity_id = StringField(max_length=100)  # ID of related entity
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    created_by = ReferenceField(User)  # Who initiated this change (for admin adjustments)
    
    meta = {
        'collection': 'kpi_history',
        'indexes': [
            'user',
            'source',
            'created_at',
            ('user', 'created_at')
        ]
    }
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': str(self.id),
            'user_id': str(self.user.id),
            'amount': self.amount,
            'balance_after': self.balance_after,
            'source': self.source,
            'reason': self.reason,
            'related_entity_type': self.related_entity_type,
            'related_entity_id': self.related_entity_id,
            'created_at': self.created_at.isoformat(),
            'created_by': str(self.created_by.id) if self.created_by else None
        }
