#!/usr/bin/env python3

import os
import sys
sys.path.append('/home/haku/projects/DHQ_Root/backend')

from app.core.config import settings
from app.core.database import connect_db
from app.models.user import User
import bcrypt

def update_op_user():
    """Update OP user to new credentials"""
    connect_db()
    
    # Find existing OP user
    op_user = User.objects(role='OP').first()
    if not op_user:
        print("No OP user found")
        return
    
    # Update username and password
    op_user.username = 'kuro'
    op_user.password_hash = bcrypt.hashpw(settings.OP_INIT_PASS.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    op_user.save()
    
    print(f"OP user updated successfully!")
    print(f"Username: {op_user.username}")
    print(f"Display Name: {op_user.display_name}")

if __name__ == "__main__":
    update_op_user()
