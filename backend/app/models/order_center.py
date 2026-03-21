from mongoengine import Document, EmbeddedDocument, StringField, IntField, DateTimeField, ListField, BooleanField, EmbeddedDocumentField, FloatField, ReferenceField
from datetime import datetime
import uuid
from .user import User
from .api_server import APIServer

class OrderCenterSubOrder(EmbeddedDocument):
    """Individual sub-order within an Order Center order"""
    id = StringField(default=lambda: str(uuid.uuid4()))
    order_id = StringField()  # Parent order ID string for convenience
    ordinal_number = IntField()  # Sequence number
    qty = IntField()
    scheduled_time = DateTimeField()
    is_enabled = BooleanField(default=True)
    
    # States: Pending, Sent, Queued, Success, Tried but failed
    internal_status = StringField(choices=('Pending', 'Sent', 'Queued', 'Success', 'Tried but failed'), default='Pending')
    api_status = StringField()  # External status from provider
    api_order_ids = StringField()  # JSON string or comma-separated IDs
    cost = FloatField(default=0.0)
    
    retry_count = IntField(default=0)
    executed_at = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)

class OrderCenterOrder(Document):
    """Main Order Center order"""
    
    user = ReferenceField(User, required=True)
    name = StringField(required=True)
    unit_label = StringField()  # e.g., "Views", "Likes"
    target_link = StringField(required=True)
    total_qty = IntField(required=True)
    total_time = IntField()  # Total duration
    time_unit = StringField(choices=('Minutes', 'Hours', 'Days'), default='Minutes')
    step_mins = IntField(default=60)
    tolerance_pct = IntField(default=10)
    graph_type = StringField(choices=('Linear', 'Exponential', 'Viral Bell Curve', 'Random'), default='Linear')
    api_service_id = StringField(required=True)
    api_server = ReferenceField(APIServer)
    
    status = StringField(
        choices=('Active', 'Paused', 'Completed', 'Cancelled'), 
        default='Active'
    )
    paused_at = DateTimeField()
    est_cost = FloatField(default=0.0)
    
    # Data
    sub_orders = ListField(EmbeddedDocumentField(OrderCenterSubOrder))
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'order_center_orders',
        'indexes': [
            'user',
            'status',
            'created_at',
            ('status', 'sub_orders.internal_status', 'sub_orders.scheduled_time')
        ]
    }
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(OrderCenterOrder, self).save(*args, **kwargs)
