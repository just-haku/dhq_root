from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
import secrets
import string
import bcrypt

# Constants
# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365 * 100  # 100 years for persistent sessions

# Use bcrypt directly to avoid passlib 1.7.4 compatibility issues with bcrypt 4.0+
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (supports bcrypt and legacy SHA-256)"""
    import hashlib
    import bcrypt
    
    # 1. Try bcrypt directly
    try:
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            hashed_bytes = hashed_password
            
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_bytes)
    except Exception:
        # 2. Last resort: Check if it's a legacy SHA-256 hash
        try:
            return hashlib.sha256(plain_password.encode('utf-8')).hexdigest() == hashed_password
        except Exception:
            return False

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    import bcrypt
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def hash_password(password: str) -> str:
    """Alias for get_password_hash for compatibility"""
    return get_password_hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_otp() -> str:
    """Generate 6-digit OTP"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def encrypt_data(data: bytes) -> bytes:
    """Encrypt data using AES-256-GCM"""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import os
    
    # Use AES_KEY from settings (ensured 32 bytes)
    key = settings.AES_KEY.encode().ljust(32, b'\0')[:32]
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    # Return nonce + ciphertext
    return nonce + ciphertext

def decrypt_data(data: bytes) -> bytes:
    """Decrypt data using AES-256-GCM"""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    
    if len(data) < 12:
        return None
        
    key = settings.AES_KEY.encode().ljust(32, b'\0')[:32]
    aesgcm = AESGCM(key)
    nonce = data[:12]
    ciphertext = data[12:]
    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception:
        return None
