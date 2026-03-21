from mongoengine import Document, StringField, IntField, BooleanField, ReferenceField, DateTimeField, ListField, DictField
from datetime import datetime
from .user import User

class UserMemoryAllocation(Document):
    """Model for user memory/storage allocations by OP"""
    
    # User reference
    user = ReferenceField(User, required=True, unique=True)
    
    # Memory allocation (in bytes)
    drive_quota = IntField(default=5 * 1024 * 1024 * 1024)  # 5GB default
    vault_quota = IntField(default=0)  # Unlimited for OP
    
    # Additional permissions
    can_upload_large_files = BooleanField(default=False)  # Files > 100MB
    max_file_size = IntField(default=100 * 1024 * 1024)  # 100MB default
    
    # Special privileges
    can_access_vault = BooleanField(default=False)
    can_manage_shop = BooleanField(default=False)
    can_view_all_drives = BooleanField(default=False)
    
    # Metadata
    allocated_by = ReferenceField(User, required=True)  # OP who allocated
    allocation_date = DateTimeField(default=datetime.utcnow)
    last_modified = DateTimeField(default=datetime.utcnow)
    notes = StringField(max_length=500)
    
    # Usage tracking
    current_drive_usage = IntField(default=0)
    current_vault_usage = IntField(default=0)
    
    meta = {
        'collection': 'user_memory_allocations',
        'indexes': [
            'user',
            'allocated_by',
            'allocation_date'
        ]
    }
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user': {
                'id': str(self.user.id),
                'username': self.user.username
            },
            'drive_quota': self.drive_quota,
            'vault_quota': self.vault_quota,
            'can_upload_large_files': self.can_upload_large_files,
            'max_file_size': self.max_file_size,
            'can_access_vault': self.can_access_vault,
            'can_manage_shop': self.can_manage_shop,
            'can_view_all_drives': self.can_view_all_drives,
            'allocated_by': {
                'id': str(self.allocated_by.id),
                'username': self.allocated_by.username
            },
            'allocation_date': self.allocation_date,
            'last_modified': self.last_modified,
            'notes': self.notes,
            'current_drive_usage': self.current_drive_usage,
            'current_vault_usage': self.current_vault_usage,
            'drive_usage_percentage': (self.current_drive_usage / self.drive_quota * 100) if self.drive_quota > 0 else 0
        }

class MemoryAllocationHistory(Document):
    """History of memory allocation changes"""
    
    user = ReferenceField(User, required=True)
    changed_by = ReferenceField(User, required=True)
    
    # Change details
    field_name = StringField(required=True)  # drive_quota, max_file_size, etc.
    old_value = IntField()
    new_value = IntField()
    
    # Metadata
    change_date = DateTimeField(default=datetime.utcnow)
    reason = StringField(max_length=500)
    
    meta = {
        'collection': 'memory_allocation_history',
        'indexes': [
            'user',
            'changed_by',
            'change_date'
        ]
    }
