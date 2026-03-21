#!/usr/bin/env python3

import os
import sys
from pymongo import MongoClient
from mongoengine import connect, disconnect
from app.models.drive import DriveFile
from app.models.user import User

def nuke_drive():
    """Delete all drive data for testing purposes"""
    
    print("🔥 NUKING DRIVE DATA - TESTING ONLY 🔥")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        connect('dhq_database', host='localhost', port=27017)
        print("✅ Connected to MongoDB")
        
        # Get all users
        users = User.objects()
        print(f"📊 Found {len(users)} users")
        
        for user in users:
            print(f"\n🗑️  Cleaning data for user: {user.username}")
            
            # Delete all drive files for this user
            files = DriveFile.objects(owner=user)
            file_count = len(files)
            
            # Delete physical files
            for file in files:
                if file.file_path and os.path.exists(file.file_path):
                    try:
                        os.remove(file.file_path)
                        print(f"   📁 Deleted: {file.file_path}")
                    except Exception as e:
                        print(f"   ❌ Failed to delete {file.file_path}: {e}")
                
                # Delete thumbnail if exists
                if file.thumbnail_path and os.path.exists(file.thumbnail_path):
                    try:
                        os.remove(file.thumbnail_path)
                        print(f"   🖼️  Deleted thumbnail: {file.thumbnail_path}")
                    except Exception as e:
                        print(f"   ❌ Failed to delete thumbnail {file.thumbnail_path}: {e}")
            
            # Delete database records
            files.delete()
            print(f"   ✅ Deleted {file_count} database records")
            
            # Delete user's storage directory
            user_storage = f"/home/haku/storage/DHQ_Root/Drive/{user.username}"
            if os.path.exists(user_storage):
                try:
                    import shutil
                    shutil.rmtree(user_storage)
                    print(f"   📁 Deleted storage directory: {user_storage}")
                except Exception as e:
                    print(f"   ❌ Failed to delete storage directory: {e}")
        
        print("\n✅ Drive data nuked successfully!")
        print("🔄 Restarting services...")
        
        # Restart services
        os.system("./dhq_manager.sh restart all")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        disconnect()

if __name__ == "__main__":
    confirm = input("⚠️  This will delete ALL drive data. Are you sure? (type 'YES'): ")
    if confirm == "YES":
        nuke_drive()
    else:
        print("❌ Operation cancelled")
