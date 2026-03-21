#!/usr/bin/env python3

import sys
import os
sys.path.append('/home/haku/projects/DHQ_Root/backend')

# Set environment variables
os.environ.setdefault('MONGODB_URI', 'mongodb://localhost:27017/dhq_db')
os.environ.setdefault('SECRET_KEY', 'dev-secret-key-for-testing-only')
os.environ.setdefault('AES_KEY', 'dev-aes-key-for-testing-only-32-chars')
os.environ.setdefault('REAL_LOGIN_ROUTE', '/hidden-login')
os.environ.setdefault('REAL_REGISTER_ROUTE', '/hidden-register')
os.environ.setdefault('SMTP_USER', 'test@example.com')
os.environ.setdefault('SMTP_PASS', 'test-password')
os.environ.setdefault('OP_INIT_USER', 'kuro')
os.environ.setdefault('OP_INIT_PASS', 'test-password')

from app.models.api_server import APIServer
from app.core.database import connect_db

def create_api_server():
    try:
        # Connect to database
        connect_db()
        
        # Check if server already exists
        existing = APIServer.objects(name='tangtuongtacre_api').first()
        if existing:
            print(f"API server '{existing.display_name}' already exists with ID: {existing.id}")
            return existing.id
        
        # Create the API server
        server = APIServer(
            name='tangtuongtacre_api',
            display_name='Tang Tuong Tac RE',
            base_url='https://tangtuongtacre.com/api/v2',
            api_version='v2',
            supports_services='views,likes,comments,followers,shares',
            description='Tang Tuong Tac RE SMM services provider',
            priority=1,
            is_active=True,
            is_default=True
        )
        
        server.save()
        print(f'✅ Created API server: {server.display_name}')
        print(f'📋 ID: {server.id}')
        print(f'🌐 URL: {server.base_url}')
        print(f'🔧 Services: {server.supports_services}')
        
        return server.id
        
    except Exception as e:
        print(f'❌ Error creating API server: {e}')
        return None

if __name__ == '__main__':
    create_api_server()
