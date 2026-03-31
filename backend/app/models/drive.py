from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField, DateTimeField, IntField, LongField, BooleanField,
    ListField, EmbeddedDocumentField, ReferenceField, FloatField
)
from app.models.user import User
from datetime import datetime
import os

class DriveFileShare(EmbeddedDocument):
    """Share information for a Drive file"""
    shared_with = ReferenceField(User)  # User who received access
    shared_by = ReferenceField(User)    # User who shared
    share_type = StringField(choices=['read', 'write'], default='read')
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()  # Optional expiration
    share_link = StringField()     # Encrypted share link
    is_public = BooleanField(default=False)
    access_level = StringField(choices=['only_me', 'specific_users', 'internal', 'public'], default='only_me')
    permission_level = StringField(choices=['visitor', 'viewer', 'commenter', 'editor'], default='viewer')
    allowed_users = ListField(ReferenceField(User))  # List of specific users allowed

class DriveFile(Document):
    """Drive file model"""
    
    # File information
    filename = StringField(required=True)           # Original filename
    stored_filename = StringField(required=True)    # Stored filename (UUID)
    file_path = StringField(required=True)          # Full file path
    mime_type = StringField(required=True)           # MIME type
    file_size = LongField(required=True)             # File size in bytes
    
    # User and folder information
    owner = ReferenceField(User, required=True)     # File owner
    folder_path = StringField(default="/")           # Folder path
    parent_folder = StringField()                     # Parent folder ID (for nested folders)
    is_folder = BooleanField(default=False)         # Whether this is a folder
    
    # Sharing information
    shares = ListField(EmbeddedDocumentField(DriveFileShare))
    access_level = StringField(choices=['only_me', 'specific_users', 'internal', 'public'], default='only_me')
    permission_level = StringField(choices=['visitor', 'viewer', 'commenter', 'editor'], default='viewer')
    allowed_users = ListField(ReferenceField(User))  # List of specific users allowed
    public_share_link = StringField()                   # Full frontend route
    share_link_id = StringField(max_length=6, unique=True, sparse=True) # The 6-character encrypted link ID
    public_share_expires = DateTimeField()
    
    # Share metadata
    share_token = StringField()                         # Unique token for share links
    share_password = StringField()                      # Optional password protection
    
    # Legacy field for backward compatibility
    is_public = BooleanField(default=False)
    
    # Metadata
    description = StringField()
    tags = ListField(StringField())
    
    # User organization
    is_starred = BooleanField(default=False)
    labels = ListField(StringField())
    
    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    modified_at = DateTimeField(default=datetime.utcnow)
    last_accessed = DateTimeField(default=datetime.utcnow)
    download_count = IntField(default=0)
    
    # File versioning
    version = IntField(default=1)
    is_deleted = BooleanField(default=False)
    deleted_at = DateTimeField()
    
    # Thumbnail information
    has_thumbnail = BooleanField(default=False)
    thumbnail_path = StringField()
    
    meta = {'collection': 'drive_files'}
    
    def save(self, *args, **kwargs):
        self.modified_at = datetime.utcnow()
        return super(DriveFile, self).save(*args, **kwargs)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'filename': self.filename,
            'name': self.filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'size': self.file_size,
            'owner': {
                'id': str(self.owner.id),
                'username': self.owner.username,
                'display_name': self.owner.display_name
            },
            'folder_path': self.folder_path,
            'parent_folder': self.parent_folder,
            'is_folder': self.is_folder,
            'shares': [
                {
                    'shared_with': {
                        'id': str(share.shared_with.id),
                        'username': share.shared_with.username,
                        'display_name': share.shared_with.display_name
                    } if share.shared_with else None,
                    'shared_by': {
                        'id': str(share.shared_by.id),
                        'username': share.shared_by.username,
                        'display_name': share.shared_by.display_name
                    },
                    'share_type': share.share_type,
                    'created_at': share.created_at.isoformat(),
                    'expires_at': share.expires_at.isoformat() if share.expires_at else None,
                    'share_link': share.share_link,
                    'is_public': share.is_public,
                    'access_level': share.access_level,
                    'allowed_users': [
                        {
                            'id': str(user.id),
                            'username': user.username,
                            'display_name': user.display_name
                        } for user in (share.allowed_users or [])
                    ]
                } for share in self.shares
            ],
            'access_level': self.access_level,
            'permission_level': getattr(self, 'permission_level', 'viewer'),
            'allowed_users': [
                {
                    'id': str(user.id),
                    'username': user.username,
                    'display_name': user.display_name
                } for user in (self.allowed_users or [])
            ],
            'public_share_link': self.public_share_link,
            'share_link_id': self.share_link_id,
            'public_share_expires': self.public_share_expires.isoformat() if self.public_share_expires else None,
            'share_token': self.share_token,
            'has_password': bool(self.share_password),
            'description': self.description,
            'tags': self.tags,
            'is_starred': getattr(self, 'is_starred', False),
            'labels': getattr(self, 'labels', []),
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'download_count': self.download_count,
            'version': self.version,
            'has_thumbnail': self.has_thumbnail,
            'thumbnail_path': self.thumbnail_path
        }

class DriveQuota(Document):
    """User drive quota management"""
    
    user = ReferenceField(User, required=True, unique=True)
    used_space = LongField(default=0)          # Used space in bytes
    total_quota = LongField(default=30*1024*1024*1024)  # 30GB default
    additional_quota = LongField(default=0)    # Additional quota allocated by OP
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'drive_quotas'}
    
    @property
    def available_space(self):
        return self.total_quota + self.additional_quota - self.used_space
    
    @property
    def usage_percentage(self):
        total = self.total_quota + self.additional_quota
        return (self.used_space / total * 100) if total > 0 else 0
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(DriveQuota, self).save(*args, **kwargs)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'user': {
                'id': str(self.user.id),
                'username': self.user.username,
                'display_name': self.user.display_name
            },
            'used_space': self.used_space,
            'total_quota': self.total_quota,
            'additional_quota': self.additional_quota,
            'available_space': self.available_space,
            'usage_percentage': round(self.usage_percentage, 2),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
