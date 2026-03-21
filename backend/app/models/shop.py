from mongoengine import Document, StringField, IntField, DateTimeField, BooleanField, ListField, DictField
from datetime import datetime

class ShopItem(Document):
    name = StringField(max_length=100, required=True)
    type = StringField(choices=(
        'Avatar Frame', 
        'Banner Frame', 
        'Animated Avatar', 
        'Animated Banner', 
        'Role', 
        'Profile Decoration',
        'Chat Badge',
        'Title',
        'Effect'
    ), required=True)
    rarity = StringField(choices=('COMMON', 'RARE', 'EPIC', 'LEGENDARY'), default='COMMON')
    price = IntField(required=True, min_value=0)
    asset_url = StringField(max_length=500)
    sale_price = IntField(min_value=0)
    sale_start = DateTimeField()
    sale_end = DateTimeField()
    available_start = DateTimeField()
    available_end = DateTimeField()
    description = StringField(max_length=500)
    is_active = BooleanField(default=True)
    is_limited = BooleanField(default=False)
    stock_quantity = IntField(min_value=0, default=0)
    requirements = DictField()  # e.g., {"level": 5, "kpi_required": 100}
    metadata = DictField()  # Additional item-specific data
    tags = ListField(StringField(max_length=50))
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'shop_items', 'indexes': ['type', 'price', 'is_active']}

class UserPurchase(Document):
    user_id = StringField(required=True)
    item_id = StringField(required=True)
    item_name = StringField(required=True)
    item_type = StringField(required=True)
    price_paid = IntField(required=True)
    purchased_at = DateTimeField(default=datetime.utcnow)
    is_active = BooleanField(default=True)  # For consumable/limited items
    metadata = DictField()
    
    meta = {'collection': 'user_purchases', 'indexes': ['user_id', 'item_id', 'purchased_at']}
