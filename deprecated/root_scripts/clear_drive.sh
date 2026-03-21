#!/bin/bash

echo "🔥 NUKING DRIVE DATA - TESTING ONLY 🔥"
echo "======================================"

# Stop services
echo "🛑 Stopping services..."
./dhq_manager.sh stop

# Clear MongoDB collections
echo "🗑️  Clearing MongoDB collections..."
docker exec dhq_mongo mongosh dhq_database --eval "db.drive_files.deleteMany({})"
docker exec dhq_mongo mongosh dhq_database --eval "db.drive_folders.deleteMany({})"

# Delete storage directories
echo "📁 Deleting storage directories..."
rm -rf /home/haku/storage/DHQ_Root/Drive/*

# Recreate base directories
echo "📁 Recreating base directories..."
mkdir -p /home/haku/storage/DHQ_Root/Drive
mkdir -p /home/haku/storage/thumbnails

# Set permissions
echo "🔐 Setting permissions..."
chmod -R 755 /home/haku/storage/DHQ_Root/Drive
chmod -R 755 /home/haku/storage/thumbnails

echo "✅ Drive data nuked successfully!"
echo "🔄 Restarting services..."

# Restart services
./dhq_manager.sh start

echo "🎉 Ready for fresh testing!"
