import os
import io
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Generator
import base64

CHUNK_SIZE = 64 * 1024  # 64KB chunks
NONCE_SIZE = 12
TAG_SIZE = 16

VLT2_MAGIC = b'VLT2'

class VaultCipher:
    def __init__(self, key: bytes):
        """
        Initialize with a 32-byte master key.
        """
        self.raw_key = key
        # V2 uses hashed key
        import hashlib
        self.v2_key = hashlib.sha256(self.raw_key).digest()
        
    def encrypt_file(self, source_path: str, dest_path: str):
        """Encrypt a file in chunks using V2 (Hardened)"""
        with open(source_path, 'rb') as f_in, open(dest_path, 'wb') as f_out:
            # Write V2 magic header
            f_out.write(VLT2_MAGIC)
            
            aesgcm_v2 = AESGCM(self.v2_key)
            
            while True:
                chunk = f_in.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                nonce = os.urandom(NONCE_SIZE)
                # encrypt returns ciphertext + tag
                encrypted_chunk = aesgcm_v2.encrypt(nonce, chunk, None)
                
                f_out.write(nonce)
                f_out.write(encrypted_chunk)

    def decrypt_stream(self, file_path: str, start: int = 0, end: int = None) -> Generator[bytes, None, None]:
        """Stream decrypt a file in chunks with range support and V1/V2 auto-detection"""
        full_chunk_size = NONCE_SIZE + CHUNK_SIZE + TAG_SIZE
        
        with open(file_path, 'rb') as f:
            # Detect version
            header = f.read(4)
            is_v2 = (header == VLT2_MAGIC)
            
            active_key = self.v2_key if is_v2 else self.raw_key
            header_offset = 4 if is_v2 else 0
            
            aesgcm = AESGCM(active_key)
            
            # Reposition to the start of the required decrypted chunk
            start_chunk_idx = start // CHUNK_SIZE
            bytes_to_skip_in_first_chunk = start % CHUNK_SIZE
            
            f.seek(header_offset + (start_chunk_idx * full_chunk_size))
            
            bytes_delivered = 0
            total_to_deliver = (end - start + 1) if end is not None else None
            
            curr_skip = bytes_to_skip_in_first_chunk
            
            while True:
                nonce = f.read(NONCE_SIZE)
                if not nonce:
                    break
                
                encrypted_data_with_tag = f.read(CHUNK_SIZE + TAG_SIZE)
                if not encrypted_data_with_tag:
                    break
                    
                try:
                    decrypted = aesgcm.decrypt(nonce, encrypted_data_with_tag, None)
                except Exception:
                    break
                
                # Slicing the decrypted chunk
                chunk_payload = decrypted[curr_skip:]
                curr_skip = 0 # Only skip for the first chunk
                
                if total_to_deliver is not None:
                    remaining = total_to_deliver - bytes_delivered
                    if len(chunk_payload) >= remaining:
                        yield chunk_payload[:remaining]
                        break
                    else:
                        yield chunk_payload
                        bytes_delivered += len(chunk_payload)
                else:
                    yield chunk_payload

    @staticmethod
    def generate_key() -> str:
        """Generate a random 32-byte key encoded in base64 for .env"""
        return base64.b64encode(os.urandom(32)).decode()

# Global utility
def get_vault_cipher():
    from app.core.config import settings
    # Use key from settings
    key = settings.vault_master_key
    # If base64, decode it
    try:
        if len(key) > 32:
            import base64
            decoded = base64.b64decode(key)
            if len(decoded) == 32:
                key = decoded
    except:
        pass
    return VaultCipher(key)
