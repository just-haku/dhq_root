from fastapi import APIRouter, HTTPException, Depends, status, Header, Request, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import timedelta, datetime
from typing import Optional
from app.core.database import redis_client
from app.models.user import User
from app.services.email_service import email_service
from app.core.security import generate_otp, verify_password, create_access_token, verify_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
import json

router = APIRouter()
security = HTTPBearer(auto_error=False)

class LoginRequest(BaseModel):
    username: str
    password: str

class OTPRequest(BaseModel):
    username: str
    otp: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str

@router.post("/register")
async def register(request: RegisterRequest):
    """Register a new user (PENDING status)"""
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Check if user exists
    if User.objects(username=request.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create user with PENDING status
    user = User(
        username=request.username,
        password_hash=get_password_hash(request.password),
        status="PENDING",
        role="USER"  # Default role
    )
    user.save()
    
    return {"message": "Registration successful. Awaiting admin approval."}

@router.post("/login")
async def login(request: LoginRequest):
    """Login user and issue JWT"""
    
    # Find user
    user = User.objects(username=request.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if user is approved
    if user.status != "ACTIVE":
        if user.status == "PENDING":
            raise HTTPException(status_code=403, detail="Account pending approval")
        elif user.status == "DECLINED":
            raise HTTPException(status_code=403, detail="Account declined")
    
    # Simple JWT issuance for all users (No OTP for now as email is gone)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    # Update last login
    user.last_login = datetime.utcnow()
    user.save()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user.username,
            "role": user.role
        }
    }

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token: Optional[str] = Query(None)
):
    """Get current user from JWT token (supports both Authorization header and 'token' query param)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Get token from header or query param
    auth_token = None
    if credentials:
        auth_token = credentials.credentials
    elif token:
        auth_token = token
        
    if not auth_token:
        raise credentials_exception
    
    try:
        payload = verify_token(auth_token)
        if not payload:
            raise credentials_exception
            
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        user = User.objects(username=username).first()
        if not user:
            raise credentials_exception
        
        return user
    except Exception as e:
        print(f"Auth Error: {e}")
        raise credentials_exception

async def get_op_user(current_user: User = Depends(get_current_user)):
    """Get current user and verify they are OP"""
    if current_user.role != 'OP':
        raise HTTPException(status_code=403, detail="OP access required")
    return current_user

async def get_current_user_optional(
    request: Request
) -> Optional[User]:
    """Get current user optionally (doesn't raise error if not authenticated)"""
    authorization = request.headers.get("authorization")
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            return None
        
        payload = verify_token(token)
        if not payload:
            return None
            
        username = payload.get('sub')
        if username is None:
            return None
        
        user = User.objects(username=username).first()
        return user
    except Exception:
        return None
