#!/usr/bin/env python3

import sys
sys.path.append('/home/haku/projects/DHQ_Root/backend')

from app.core.database import connect_db
from app.models.user import User

def approve_op_user():
    """Approve OP user"""
    connect_db()
    
    # Find OP user
    op_user = User.objects(username='kuro', role='OP').first()
    if not op_user:
        print("No OP user found")
        return
    
    # Approve the user
    op_user.status = 'ACTIVE'
    op_user.save()
    
    print(f"OP user approved successfully!")
    print(f"Username: {op_user.username}")
    print(f"Status: {op_user.status}")

if __name__ == "__main__":
    approve_op_user()
