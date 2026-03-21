#!/bin/bash

echo "🔥 FORCE NUKING DRIVE DATA - TESTING ONLY 🔥"
echo "=========================================="

# Stop all services
echo "🛑 Stopping all services..."
./dhq_manager.sh stop

# Kill any remaining processes
echo "💀 Killing remaining processes..."
pkill -f "python.*app"
pkill -f "node.*frontend"
pkill -f "uvicorn"
pkill -f "npm.*dev"

# Clear MongoDB completely
echo "🗑️  Clearing MongoDB completely..."
# Connect to MongoDB and drop collections
mongosh dhq_database --eval "
db.drive_files.deleteMany({});
db.drive_folders.deleteMany({});
db.users.deleteMany({});
exit;
"

# Delete all storage directories
echo "📁 Deleting all storage directories..."
rm -rf /home/haku/storage/DHQ_Root/Drive/*
rm -rf /home/haku/storage/thumbnails/*
rm -rf /home/haku/storage/DHQ_Root/Uploads/*

# Recreate base directories
echo "📁 Recreating base directories..."
mkdir -p /home/haku/storage/DHQ_Root/Drive
mkdir -p /home/haku/storage/thumbnails
mkdir -p /home/haku/storage/DHQ_Root/Uploads

# Set permissions
echo "🔐 Setting permissions..."
chmod -R 777 /home/haku/storage/DHQ_Root/Drive
chmod -R 777 /home/haku/storage/thumbnails
chmod -R 777 /home/haku/storage/DHQ_Root/Uploads

# Clear any cache
echo "🧹 Clearing cache..."
rm -rf /home/haku/projects/DHQ_Root/frontend/node_modules/.vite
rm -rf /home/haku/projects/DHQ_Root/frontend/dist

# Restart services
echo "🔄 Restarting services..."
./dhq_manager.sh start

echo "✅ Drive data completely nuked!"
echo "🎉 Ready for fresh testing!"
