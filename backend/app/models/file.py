from mongoengine import Document, StringField, DateTimeField, BinaryField, IntField, BooleanField, ReferenceField, ListField
from datetime import datetime
from .user import User

class EncryptedFile(Document):
    """Model for encrypted files stored in the Vault"""
    
    # File metadata
    filename = StringField(required=True, max_length=255)
    original_filename = StringField(required=True, max_length=255)
    file_path = StringField(required=True)  # Path to encrypted file on disk
    mime_type = StringField(required=True, max_length=100)
    file_size = IntField(required=True)  # Size in bytes
    
    # Encryption data
    nonce = BinaryField(required=True)  # 12-byte nonce for AES-GCM
    thumbnail_nonce = BinaryField()  # Nonce for encrypted thumbnail (if any)
    
    # Permissions
    owner = ReferenceField(User, required=True)
    permissions = StringField(choices=['ME_ONLY', 'SPECIFIC_USER', 'COMPANY', 'PUBLIC'], default='ME_ONLY')
    allowed_users = ListField(ReferenceField(User))  # For SPECIFIC_USER permission
    
    # Versioning
    is_version = BooleanField(default=False)  # True if this is a version of another file
    parent_file = ReferenceField('self')  # Original file if this is a version
    version_number = IntField(default=1)  # Version number
    
    # Metadata
    upload_date = DateTimeField(default=datetime.utcnow)
    last_modified = DateTimeField(default=datetime.utcnow)
    download_count = IntField(default=0)
    
    # Thumbnails
    has_thumbnail = BooleanField(default=False)
    thumbnail_path = StringField()  # Path to encrypted thumbnail
    
    # Security
    is_sensitive = BooleanField(default=False)  # For forensic watermarking
    
    meta = {
        'collection': 'encrypted_files',
        'indexes': [
            'owner',
            'upload_date',
            'original_filename',
            'permissions'
        ]
    }
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'filename': self.filename,
            'original_filename': self.original_filename,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'permissions': self.permissions,
            'upload_date': self.upload_date.isoformat(),
            'last_modified': self.last_modified.isoformat(),
            'download_count': self.download_count,
            'has_thumbnail': self.has_thumbnail,
            'is_sensitive': self.is_sensitive,
            'version_number': self.version_number,
            'is_version': self.is_version
        }
