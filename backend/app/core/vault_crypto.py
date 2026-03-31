import os
import io
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from typing import Generator
import base64

CHUNK_SIZE = 64 * 1024  # 64KB chunks
NONCE_SIZE = 12
TAG_SIZE = 16

class VaultCipher:
    def __init__(self, key: str):
        """
        Initialize with a 32-byte (256-bit) master key.
        If the key is not 32 bytes, it will be padded or hashed (better to ensure it's 32 bytes).
        """
        if isinstance(key, str):
            # Ensure key is bytes and 32 bytes long
            self.key = key.encode().ljust(32, b'\0')[:32]
        else:
            self.key = key
        self.aesgcm = AESGCM(self.key)

    def encrypt_file(self, source_path: str, dest_path: str):
        """Encrypt a file in chunks"""
        with open(source_path, 'rb') as f_in, open(dest_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(CHUNK_SIZE)
                if not chunk:
                    break
                
                nonce = os.urandom(NONCE_SIZE)
                # encrypt returns ciphertext + tag
                encrypted_chunk = self.aesgcm.encrypt(nonce, chunk, None)
                
                f_out.write(nonce)
                f_out.write(encrypted_chunk)

    def decrypt_stream(self, file_path: str) -> Generator[bytes, None, None]:
        """Stream decrypt a file in chunks"""
        full_chunk_size = NONCE_SIZE + CHUNK_SIZE + TAG_SIZE
        
        with open(file_path, 'rb') as f:
            while True:
                # We need to be careful because the last chunk might be smaller
                # Reading fixed size: nonce + ciphertext + tag
                # But how do we know the ciphertext size of the last chunk?
                # Actually, AESGCM tag is always 16 bytes. Nonce is 12.
                # If f_in.read(CHUNK_SIZE) returned less, the encrypted chunk will be smaller.
                
                # Reading nonce first
                nonce = f.read(NONCE_SIZE)
                if not nonce:
                    break
                
                # Reading the rest of the chunk. 
                # We don't know the exact size if it was shorter than CHUNK_SIZE.
                # However, since we write [nonce][encrypted], the next nonce is 12 bytes away 
                # from the END of the current encrypted block.
                # A better approach: write the length of the encrypted block?
                # Or just assume CHUNK_SIZE unless it's the end of the file.
                
                # Let's read the maximum possible remaining for a chunk.
                # Wait, if we know CHUNK_SIZE is fixed for all but the last, 
                # we can calculate it from the file size.
                
                # Better: Read the remaining data for this chunk.
                # Since we know the original chunk was at most CHUNK_SIZE, 
                # the encrypted part is at most CHUNK_SIZE + TAG_SIZE.
                
                encrypted_data_with_tag = f.read(CHUNK_SIZE + TAG_SIZE)
                yield self.aesgcm.decrypt(nonce, encrypted_data_with_tag, None)

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
