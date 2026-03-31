import os
import io
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from PIL import Image
import ffmpeg
from typing import Tuple, Optional, Union
import uuid

class EncryptionService:
    def __init__(self, aes_key: str):
        """Initialize with 32-byte hex AES key"""
        self.key = bytes.fromhex(aes_key)
        if len(self.key) != 32:
            raise ValueError("AES key must be 32 bytes (64 hex chars)")
    
    def encrypt_file(self, file_data: bytes) -> Tuple[bytes, bytes]:
        """Encrypt file data using AES-256-GCM
        Returns: (encrypted_data, nonce)
        """
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        encrypted_data = aesgcm.encrypt(nonce, file_data, None)
        return encrypted_data, nonce
    
    def decrypt_file(self, encrypted_data: bytes, nonce: bytes) -> bytes:
        """Decrypt file data using AES-256-GCM"""
        aesgcm = AESGCM(self.key)
        return aesgcm.decrypt(nonce, encrypted_data, None)
    
    def encrypt_and_save(self, file_data: bytes, file_path: str) -> Tuple[str, bytes]:
        """Encrypt file data and save to disk
        Returns: (saved_file_path, nonce)
        """
        encrypted_data, nonce = self.encrypt_file(file_data)
        
        # Save encrypted file
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        
        return file_path, nonce
    
    def load_and_decrypt(self, file_path: str, nonce: bytes) -> bytes:
        """Load encrypted file from disk and decrypt"""
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        return self.decrypt_file(encrypted_data, nonce)
    
    def generate_thumbnail_from_encrypted(self, encrypted_data: bytes, nonce: bytes, 
                                       output_size: tuple = (200, 200)) -> Optional[bytes]:
        """Generate thumbnail from encrypted image data"""
        try:
            # Decrypt the image data
            image_data = self.decrypt_file(encrypted_data, nonce)
            
            # Create PIL Image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Create thumbnail
            image.thumbnail(output_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            thumb_bytes = io.BytesIO()
            image.save(thumb_bytes, format='JPEG', quality=85)
            thumb_bytes.seek(0)
            
            return thumb_bytes.getvalue()
        except Exception as e:
            print(f"Thumbnail generation error: {e}")
            return None
    
    def generate_video_thumbnail_from_encrypted(self, encrypted_data: bytes, nonce: bytes,
                                             output_size: tuple = (200, 200)) -> Optional[bytes]:
        """Generate thumbnail from encrypted video data"""
        try:
            # Decrypt video data
            video_data = self.decrypt_file(encrypted_data, nonce)
            
            # Create temporary file for ffmpeg
            temp_id = str(uuid.uuid4())
            temp_input = f"/tmp/{temp_id}_input.mp4"
            temp_output = f"/tmp/{temp_id}_output.jpg"
            
            # Write decrypted video to temp file
            with open(temp_input, 'wb') as f:
                f.write(video_data)
            
            try:
                # Use ffmpeg to extract thumbnail from first frame
                (
                    ffmpeg
                    .input(temp_input, hwaccel='none')
                    .output(temp_output, vframes=1, threads=1, format='image2', vcodec='mjpeg')
                    .overwrite_output()
                    .run(input=video_data, capture_stdout=True, capture_stderr=True)
                )
                
                # Read the thumbnail
                with open(temp_output, 'rb') as f:
                    thumbnail_data = f.read()
                
                return thumbnail_data
            finally:
                # Clean up temp files
                if os.path.exists(temp_input):
                    os.remove(temp_input)
                if os.path.exists(temp_output):
                    os.remove(temp_output)
                    
        except Exception as e:
            print(f"Video thumbnail generation error: {e}")
            return None

# Global encryption service instance
encryption_service = None

def get_encryption_service() -> EncryptionService:
    """Get or create encryption service instance"""
    global encryption_service
    if encryption_service is None:
        from app.core.config import settings
        encryption_service = EncryptionService(settings.AES_KEY)
    return encryption_service
