from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
import secrets
import string
import bcrypt

# Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        # Try passlib first
        return pwd_context.verify(plain_password, hashed_password)
    except:
        # Fall back to bcrypt directly
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

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
    """Encrypt data using AES-256 (placeholder implementation)"""
    # This is a placeholder - implement proper AES encryption
    import base64
    return base64.b64encode(data)

def decrypt_data(encrypted_data: bytes) -> bytes:
    """Decrypt data using AES-256 (placeholder implementation)"""
    # This is a placeholder - implement proper AES decryption
    import base64
    return base64.b64decode(encrypted_data)
