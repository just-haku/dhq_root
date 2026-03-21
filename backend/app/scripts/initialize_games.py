#!/usr/bin/env python3
"""
Initialize DHQ System with sample data
"""

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.models.user import User
from app.models.shop import ShopItem
from app.models.arcade import UserArcadeProfile, LeaderboardEntry
from app.models.kpi import KPIHistory
from app.core.database import connect_db
from datetime import datetime, timedelta
import random

def initialize_shop_items():
    """Initialize shop with sample items"""
    print("Initializing shop items...")
    
    sample_items = [
        {
            "name": "Golden Avatar Frame",
            "type": "Avatar Frame",
            "rarity": "LEGENDARY",
            "price": 500,
            "description": "A stunning golden frame for your avatar",
            "asset_url": "/assets/shop/golden_avatar_frame.png",
            "is_limited": True,
            "stock_quantity": 10,
            "requirements": {"level": 5, "kpi_required": 200},
            "tags": ["avatar", "premium", "golden"]
        },
        {
            "name": "Diamond Banner",
            "type": "Banner Frame",
            "rarity": "EPIC",
            "price": 300,
            "description": "Sparkling diamond banner frame",
            "asset_url": "/assets/shop/diamond_banner.png",
            "is_limited": True,
            "stock_quantity": 25,
            "requirements": {"level": 3, "kpi_required": 100},
            "tags": ["banner", "diamond", "premium"]
        },
        {
            "name": "Fire Avatar",
            "type": "Animated Avatar",
            "rarity": "EPIC",
            "price": 400,
            "description": "Animated fire effect for your avatar",
            "asset_url": "/assets/shop/fire_avatar.gif",
            "is_limited": False,
            "stock_quantity": 0,
            "requirements": {"level": 4, "kpi_required": 150},
            "tags": ["avatar", "animated", "fire"]
        },
        {
            "name": "Elite Role",
            "type": "Role",
            "rarity": "RARE",
            "price": 200,
            "description": "Elite user role with special permissions",
            "asset_url": "/assets/shop/elite_role.png",
            "is_limited": False,
            "stock_quantity": 0,
            "requirements": {"level": 2, "kpi_required": 50},
            "tags": ["role", "elite", "permission"]
        },
        {
            "name": "Chat Badge Pro",
            "type": "Chat Badge",
            "rarity": "COMMON",
            "price": 50,
            "description": "Professional chat badge",
            "asset_url": "/assets/shop/chat_badge_pro.png",
            "is_limited": False,
            "stock_quantity": 0,
            "requirements": {"level": 1, "kpi_required": 10},
            "tags": ["chat", "badge", "common"]
        },
        {
            "name": "Speed Boost",
            "type": "Effect",
            "rarity": "RARE",
            "price": 150,
            "description": "2x KPI earning speed for 1 hour",
            "asset_url": "/assets/shop/speed_boost.png",
            "is_limited": False,
            "stock_quantity": 0,
            "requirements": {"level": 2, "kpi_required": 30},
            "tags": ["effect", "boost", "speed"]
        }
    ]
    
    for item_data in sample_items:
        # Check if item already exists
        existing = ShopItem.objects(name=item_data["name"]).first()
        if not existing:
            item = ShopItem(**item_data)
            item.save()
            print(f"Created shop item: {item_data['name']}")
        else:
            print(f"Shop item already exists: {item_data['name']}")

def initialize_leaderboard():
    """Initialize leaderboard with sample data"""
    print("Initializing leaderboard...")
    
    # Get some users for leaderboard
    users = User.objects()[:10]
    
    game_types = ["WORDLE", "FAST_TYPING", "MEMORY_CARDS"]
    period_types = ["DAILY", "WEEKLY", "MONTHLY", "ALL_TIME"]
    
    for user in users:
        for game_type in game_types:
            for period_type in period_types:
                # Check if entry already exists
                existing = LeaderboardEntry.objects(
                    user=user,
                    game_type=game_type,
                    period_type=period_type
                ).first()
                
                if not existing:
                    # Generate random score
                    base_score = random.randint(100, 10000)
                    kpi_earned = base_score // 10
                    
                    entry = LeaderboardEntry(
                        user=user,
                        game_type=game_type,
                        period_type=period_type,
                        score=base_score,
                        kpi_earned=kpi_earned,
                        timestamp=datetime.utcnow()
                    )
                    entry.save()
                    print(f"Created leaderboard entry for {user.username} - {game_type} - {period_type}")

def initialize_arcade_profiles():
    """Initialize arcade profiles for existing users"""
    print("Initializing arcade profiles...")
    
    users = User.objects()
    
    for user in users:
        # Check if profile already exists
        existing = UserArcadeProfile.objects(user=user).first()
        if not existing:
            profile = UserArcadeProfile(
                user=user,
                kpi_balance=random.randint(50, 500),
                total_kpi_earned=random.randint(100, 1000),
                kpi_spent=random.randint(0, 200),
                level=random.randint(1, 5),
                experience_points=random.randint(0, 1000),
                games_played=random.randint(0, 50),
                achievements_unlocked=random.randint(0, 10),
                login_streak=random.randint(0, 7),
                last_login=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
            )
            profile.save()
            print(f"Created arcade profile for {user.username}")
        else:
            print(f"Arcade profile already exists for {user.username}")

def main():
    """Main initialization function"""
    print("🚀 Initializing DHQ System Data...")
    
    try:
        # Connect to database
        connect_db()
        print("✅ Connected to database")
        
        # Initialize data
        initialize_shop_items()
        initialize_arcade_profiles()
        initialize_leaderboard()
        
        print("\n🎉 DHQ System initialization completed successfully!")
        print("📊 Shop items, arcade profiles, and leaderboards are ready!")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
