from mongoengine import Document, DateTimeField, StringField, IntField, LongField, BooleanField, ReferenceField, ListField
from app.models.user import User
from datetime import datetime

class VaultFile(Document):
    """Secure, encrypted Vault file model (OP Only, No Sharing)"""
    
    filename = StringField(required=True)           # Original filename
    stored_filename = StringField(required=True)    # Stored filename (UUID)
    file_path = StringField(required=True)          # Full file path on disk
    mime_type = StringField(required=True)           # Original MIME type
    file_size = LongField(required=True)             # Original (unencrypted) size
    encrypted_size = LongField()                     # Size on disk (encrypted)
    
    owner = ReferenceField(User, required=True)     # Must be an OP
    folder_path = StringField(default="/")           # Virtual folder path
    is_folder = BooleanField(default=False)
    
    # Encryption Metadata
    encryption_v = IntField(default=1)              # Version of encryption used
    nonce = StringField()                           # Nonce/IV used (base64) (If not using standard chunked format)
    
    # Sharing information
    access_level = StringField(choices=['private', 'internal', 'public'], default='private')
    permission_level = StringField(choices=['visitor', 'viewer', 'commenter', 'editor'], default='viewer')
    allowed_users = ListField(ReferenceField(User))  # List of specific users allowed
    
    share_link_id = StringField(unique=True, sparse=True) # Non-human-readable hashed ID (long)
    public_share_expires = DateTimeField()
    share_password = StringField()                      # Optional password protection (hashed)
    download_count = IntField(default=0)
    
    # Metadata
    is_starred = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    modified_at = DateTimeField(default=datetime.utcnow)
    last_accessed = DateTimeField(default=datetime.utcnow)
    
    is_deleted = BooleanField(default=False)
    deleted_at = DateTimeField()

    meta = {'collection': 'vault_files'}

    def save(self, *args, **kwargs):
        self.modified_at = datetime.utcnow()
        return super(VaultFile, self).save(*args, **kwargs)

    def to_dict(self):
        return {
            'id': str(self.id),
            'filename': self.filename,
            'name': self.filename,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'size': self.file_size,
            'folder_path': self.folder_path,
            'is_folder': self.is_folder,
            'is_starred': self.is_starred,
            'access_level': self.access_level,
            'permission_level': getattr(self, 'permission_level', 'viewer'),
            'share_link_id': self.share_link_id,
            'public_share_link': self.public_share_link,
            'public_share_expires': self.public_share_expires.isoformat() if self.public_share_expires else None,
            'has_password': bool(self.share_password),
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat()
        }

    @property
    def public_share_link(self):
        if self.share_link_id:
            return f"https://haku.io.vn/s/{self.share_link_id}"
        return None
