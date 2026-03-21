import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

# --- Helpers ---

def utc_now():
    """Helper to get timezone-aware UTC current time."""
    return datetime.datetime.now(datetime.timezone.utc)

# --- Role Based Access Control (RBAC) ---

class Permission(db.EmbeddedDocument):
    name = db.StringField(required=True)
    description = db.StringField()

class Role(db.Document):
    name = db.StringField(required=True, unique=True)
    permissions = db.ListField(db.StringField())  # List of permission keys
    meta = {'collection': 'roles'}

class Group(db.Document):
    name = db.StringField(required=True, unique=True)
    description = db.StringField()
    permissions = db.DictField(default={}) 
    meta = {'collection': 'groups'}

# --- Economy & Shop ---

class ShopItem(db.Document):
    name = db.StringField(required=True, max_length=100)
    type = db.StringField(default='namecard', max_length=50)
    description = db.StringField(max_length=200)
    price = db.IntField(default=0)
    discount = db.IntField(default=0)
    title_content = db.StringField(max_length=100)
    resource_url = db.StringField(max_length=200)
    is_active = db.BooleanField(default=True)
    created_at = db.DateTimeField(default=utc_now)
    meta = {'collection': 'shop_items'}

class UserInventory(db.Document):
    """
    Inventory items for users.
    Using a separate collection (Document) instead of EmbeddedDocument 
    allows for easier querying and scalability (e.g. searching all users who own item X).
    """
    user_id = db.ReferenceField('User', required=True) # Matches shop.py usage of user_id=...
    item_id = db.ReferenceField('ShopItem', required=True) # Matches shop.py usage of item_id=...
    acquired_at = db.DateTimeField(default=utc_now)
    meta = {'collection': 'user_inventory'}

# --- User ---

class User(db.Document, UserMixin):
    # Auth
    username = db.StringField(required=True, unique=True, max_length=150)
    email = db.StringField(unique=True)
    password_hash = db.StringField(required=True)
    
    # Registration Status
    status = db.StringField(default='active', max_length=20, choices=('active', 'pending', 'denied'))
    denial_reason = db.StringField(default='')

    # Profile
    display_name = db.StringField(max_length=150)
    bio = db.StringField(max_length=500, default='')
    avatar = db.StringField(default="placeholder.png", max_length=200)
    created_at = db.DateTimeField(default=utc_now)
    last_seen = db.DateTimeField(default=utc_now)
    
    # Roles & Groups
    role = db.ReferenceField(Role)
    groups = db.ListField(db.ReferenceField(Group))
    
    # Economy
    balance = db.FloatField(default=0.0)
    kpi = db.IntField(default=0)
    
    # Cosmetics
    namecard_url = db.StringField(max_length=200)
    active_title = db.StringField(max_length=100)
    active_title_bg = db.StringField(max_length=200)
    active_background = db.StringField(max_length=200)
    active_avatar_frame = db.StringField(max_length=200)
    active_banner_frame = db.StringField(max_length=200)
    
    # System
    api_key = db.StringField(max_length=150)
    is_banned = db.BooleanField(default=False)
    permissions = db.DictField(default={})
    
    # NOTE: inventory list is removed in favor of UserInventory collection queries
    # to avoid data synchronization issues.
    
    meta = {'collection': 'users'}

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        return self.role and self.role.name in ['admin', 'operator']

    @property
    def name(self):
        return self.display_name if self.display_name else self.username

    def has_perm(self, perm_key):
        """Checks permissions across Role, Groups, and User-specific overrides."""
        if self.role and self.role.name in ['operator', 'admin']: 
            return True
        
        # Check User specific permissions (Dict lookup)
        if self.permissions and perm_key in self.permissions:
            return self.permissions[perm_key]
        
        # Check Group permissions (Dict lookup)
        for group in self.groups:
            if group.permissions and perm_key in group.permissions:
                return group.permissions[perm_key]
        
        # Check Role permissions (List lookup)
        if self.role and self.role.permissions:
            if 'all' in self.role.permissions: 
                return True
            if perm_key in self.role.permissions: 
                return True
                
        return False
    
    def get_id(self):
        return str(self.id)

# --- Collaboration & Orders ---

class Collaboration(db.Document):
    name = db.StringField(required=True, max_length=100)
    user = db.ReferenceField(User, required=True)
    service_id = db.StringField(max_length=50)
    service_name = db.StringField(max_length=100)
    link = db.StringField(max_length=500)
    total_days = db.FloatField()
    step_hours = db.FloatField()
    tolerance_pct = db.FloatField()
    total_quantity = db.IntField()
    auto_check = db.BooleanField(default=True)
    is_deleted = db.BooleanField(default=False)
    created_at = db.DateTimeField(default=utc_now)
    meta = {'collection': 'collaborations'}

class Order(db.Document):
    collaboration = db.ReferenceField(Collaboration, required=True)
    quantity = db.IntField(required=True)
    scheduled_time = db.DateTimeField(required=True)
    status = db.StringField(default='Pending', max_length=50)
    api_order_id = db.StringField(max_length=100)
    api_response = db.StringField()
    executed_at = db.DateTimeField()
    meta = {'collection': 'orders'}

# --- Tasks ---

class Task(db.Document):
    title = db.StringField(required=True)
    description = db.StringField()
    assigned_to = db.ReferenceField(User)
    assigned_by = db.ReferenceField(User)
    status = db.StringField(default='pending', choices=('pending', 'in_progress', 'completed'))
    due_date = db.DateTimeField()
    created_at = db.DateTimeField(default=utc_now)
    kpi_awarded = db.BooleanField(default=False)
    meta = {'collection': 'tasks'}

# --- Chat & Notifications ---

class ChatMessage(db.Document):
    user = db.ReferenceField(User)
    username_snapshot = db.StringField()
    message = db.StringField()
    is_sticker = db.BooleanField(default=False)
    timestamp = db.DateTimeField(default=utc_now)
    meta = {'collection': 'chat_messages'}

class Notification(db.Document):
    user = db.ReferenceField(User, required=True) # Changed back to 'user' for dashboard.py compatibility
    type = db.StringField(default='info', max_length=50)
    category = db.StringField(default='system', max_length=50)
    title = db.StringField(max_length=100)
    content = db.StringField()
    is_read = db.BooleanField(default=False)
    timestamp = db.DateTimeField(default=utc_now)
    group_key = db.StringField(max_length=100)
    meta = {'collection': 'notifications'}
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'type': self.type,
            'category': self.category,
            'title': self.title,
            'content': self.content,
            'is_read': self.is_read,
            'time': self.timestamp.strftime('%Y-%m-%d %H:%M')
        }

# --- Media ---

class MediaComment(db.EmbeddedDocument):
    user = db.ReferenceField(User)
    username_snapshot = db.StringField()
    content = db.StringField()
    timestamp = db.DateTimeField(default=utc_now)

class MediaReaction(db.EmbeddedDocument):
    user = db.ReferenceField(User)
    username_snapshot = db.StringField()
    reaction_type = db.StringField(max_length=100)

class MediaGroup(db.Document):
    name = db.StringField(required=True, max_length=100)
    description = db.StringField(max_length=255)
    creator = db.ReferenceField(User) # Optional creator
    allowed_users = db.ListField(db.ReferenceField(User))
    avatar = db.StringField(max_length=200)
    created_at = db.DateTimeField(default=utc_now)
    meta = {'collection': 'media_groups'}

class Media(db.Document):
    filename = db.StringField(required=True)
    original_filename = db.StringField(required=True)
    file_type = db.StringField(required=True) 
    filepath = db.StringField() 
    mimetype = db.StringField(max_length=50)
    
    # References
    user = db.ReferenceField(User, required=True)
    group = db.ReferenceField(MediaGroup)
    
    caption = db.StringField(max_length=500)
    is_public = db.BooleanField(default=True)
    allowed_users = db.ListField(db.ReferenceField(User))
    is_hidden = db.BooleanField(default=False)
    reports = db.IntField(default=0)
    is_temp = db.BooleanField(default=False)
    uploaded_at = db.DateTimeField(default=utc_now)

    comments = db.ListField(db.EmbeddedDocumentField(MediaComment))
    reactions = db.ListField(db.EmbeddedDocumentField(MediaReaction))
    
    meta = {'collection': 'media'}

class CustomReaction(db.Document):
    name = db.StringField(max_length=50)
    image_url = db.StringField(max_length=200)
    created_by = db.ReferenceField(User)
    meta = {'collection': 'custom_reactions'}

class SavedCollection(db.Document):
    user = db.ReferenceField(User, required=True)
    name = db.StringField(default='Saved Posts', max_length=100)
    items = db.ListField(db.ReferenceField(Media))
    meta = {'collection': 'saved_collections'}

# --- Security & VirusTotal ---

class ScanResult(db.Document):
    resource_type = db.StringField(required=True, choices=('file', 'url'))
    resource_key = db.StringField(required=True)  # file hash or url
    status = db.StringField()
    malicious_count = db.IntField(default=0)
    total_engines = db.IntField(default=0)
    permalink = db.StringField()
    scanned_at = db.DateTimeField(default=utc_now)
    requested_by = db.ReferenceField(User)
    meta = {'collection': 'scan_results'}