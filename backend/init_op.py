#!/usr/bin/env python3
import sys
import os
sys.path.append('/home/haku/projects/DHQ_Root/backend')

import bcrypt
from app.core.config import settings
from app.core.database import connect_db
from app.models.user import User

def create_op_user():
    """Create the OP user if it doesn't exist"""
    # Connect to database first
    connect_db()
    
    existing_user = User.objects(username=settings.OP_INIT_USER).first()
    
    if existing_user:
        print(f"OP user '{settings.OP_INIT_USER}' already exists")
        return
    
    # Hash password using bcrypt directly
    password = settings.OP_INIT_PASS.encode('utf-8')
    password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
    
    op_user = User(
        username=settings.OP_INIT_USER,
        password_hash=password_hash,
        role="OP",
        status="ACTIVE",
        display_name="Operator",
        email="op@dhq.local"
    )
    op_user.save()
    print(f"Created OP user: {settings.OP_INIT_USER}")

if __name__ == "__main__":
    create_op_user()
