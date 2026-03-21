from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class EncryptionService:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        from app.core.storage import storage_service
        
        # Check all storages for existing key
        for storage_path in storage_service.get_all_storage_paths():
            key_file = os.path.join(storage_path, ".encryption_key")
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()

        # Generate new key in the highest priority storage
        primary_storage = storage_service.get_all_storage_paths()[0]
        key_file = os.path.join(primary_storage, ".encryption_key")
        
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(key_file), exist_ok=True)
        with open(key_file, 'wb') as f:
            f.write(key)
        return key
    
    def encrypt(self, data: bytes) -> tuple[bytes, bytes]:
        """Encrypt data and return (encrypted_data, nonce)"""
        encrypted_data = self.cipher.encrypt(data)
        # For Fernet, the nonce is part of the encrypted data, but we'll extract it for consistency
        nonce = encrypted_data[:12]  # First 12 bytes as nonce
        return encrypted_data, nonce
    
    def decrypt(self, encrypted_data: bytes, nonce: bytes = None) -> bytes:
        """Decrypt data"""
        return self.cipher.decrypt(encrypted_data)

# Global instance
_encryption_service = None

def get_encryption_service() -> EncryptionService:
    """Get global encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
