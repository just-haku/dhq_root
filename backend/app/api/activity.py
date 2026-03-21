from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.models.file import EncryptedFile
from app.models.arcade import UserArcadeProfile, GameSession
from app.models.collaboration import Collaboration
from app.api.auth import get_current_user
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class ActivityItem(BaseModel):
    id: str
    type: str
    title: str
    description: str
    user: dict
    timestamp: datetime
    metadata: dict

@router.get("/feed")
async def get_activity_feed(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get real-time activity feed"""
    
    activities = []
    
    # Recent collaboration activities
    recent_collaborations = Collaboration.objects().order_by('-created_at').limit(20)
    for collab in recent_collaborations:
        activities.append(ActivityItem(
            id=str(collab.id),
            type="collaboration",
            title=f"Collaboration {collab.type}",
            description=collab.name,
            user={
                "id": str(collab.id),
                "username": collab.collaborator_name,
                "display_name": collab.collaborator_name
            },
            timestamp=collab.created_at,
            metadata={
                "platform": collab.platform,
                "type": collab.type,
                "deadline": collab.deadline.isoformat() if collab.deadline else None
            }
        ))
    
    # Recent file uploads
    try:
        recent_files = EncryptedFile.objects().order_by('-created_at').limit(15)
        for file in recent_files:
            activities.append(ActivityItem(
                id=str(file.id),
                type="file",
                title="File uploaded",
                description=file.filename,
                user={
                    "id": str(file.owner.id),
                    "username": file.owner.username,
                    "display_name": file.owner.display_name
                },
                timestamp=file.created_at,
                metadata={
                    "file_size": file.file_size,
                    "mime_type": file.mime_type
                }
            ))
    except Exception as e:
        print(f"Error loading EncryptedFile activities: {e}")
    
    # Recent game sessions
    try:
        recent_games = GameSession.objects().order_by('-completed_at').limit(10)
        for game in recent_games:
            activities.append(ActivityItem(
                id=str(game.id),
                type="game",
                title=f"Played {game.game_type}",
                description=f"Score: {game.score} | KPI: {game.kpi_earned}",
                user={
                    "id": str(game.user.id),
                    "username": game.user.username,
                    "display_name": game.user.display_name
                },
                timestamp=game.completed_at,
                metadata={
                    "game_type": game.game_type,
                    "difficulty": game.difficulty,
                    "duration": game.duration_seconds
                }
            ))
    except Exception as e:
        print(f"Error loading GameSession activities: {e}")
    
    # Sort by timestamp
    activities.sort(key=lambda x: x.timestamp, reverse=True)
    
    return activities[:limit]

@router.get("/analytics/overview")
async def get_analytics_overview(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive analytics overview"""
    
    # Time ranges
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)
    
    # User metrics
    total_users = User.objects.count()
    active_users_24h = User.objects(last_login__gte=last_24h).count()
    active_users_7d = User.objects(last_login__gte=last_7d).count()
    
    # Collaboration metrics
    total_collaborations = Collaboration.objects.count()
    active_collaborations = Collaboration.objects().count()  # All are considered active
    completed_collaborations = Collaboration.objects().count()  # Simplified for now
    
    # File metrics
    total_files = EncryptedFile.objects.count()
    uploaded_24h = EncryptedFile.objects(upload_date__gte=last_24h).count()
    uploaded_7d = EncryptedFile.objects(upload_date__gte=last_7d).count()
    
    # Arcade metrics
    total_kpi_earned = UserArcadeProfile.objects().sum('total_kpi_earned') or 0
    games_played_24h = GameSession.objects(completed_at__gte=last_24h).count()
    games_played_7d = GameSession.objects(completed_at__gte=last_7d).count()
    
    # Growth metrics
    new_users_24h = User.objects(created_at__gte=last_24h).count()
    new_users_7d = User.objects(created_at__gte=last_7d).count()
    
    return {
        "users": {
            "total": total_users,
            "active_24h": active_users_24h,
            "active_7d": active_users_7d,
            "new_24h": new_users_24h,
            "new_7d": new_users_7d,
            "growth_rate_7d": round((new_users_7d / max(total_users - new_users_7d, 1)) * 100, 2)
        },
        "collaborations": {
            "total": total_collaborations,
            "active": active_collaborations,
            "completed": completed_collaborations,
            "completion_rate": round((completed_collaborations / max(total_collaborations, 1)) * 100, 2)
        },
        "files": {
            "total": total_files,
            "uploaded_24h": uploaded_24h,
            "uploaded_7d": uploaded_7d,
            "total_size_gb": round(EncryptedFile.objects().sum('file_size') / (1024**3), 2)
        },
        "arcade": {
            "total_kpi_earned": total_kpi_earned,
            "games_played_24h": games_played_24h,
            "games_played_7d": games_played_7d,
            "active_players": UserArcadeProfile.objects(games_played__gt=0).count()
        },
        "engagement": {
            "daily_active_rate": round((active_users_24h / max(total_users, 1)) * 100, 2),
            "weekly_active_rate": round((active_users_7d / max(total_users, 1)) * 100, 2),
            "avg_collaborations_per_user": round(total_collaborations / max(total_users, 1), 2),
            "avg_files_per_user": round(total_files / max(total_users, 1), 2)
        }
    }

@router.get("/analytics/trends")
async def get_analytics_trends(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get analytics trends over time"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    trends = []
    
    # Generate daily data points
    for i in range(days):
        date = start_date + timedelta(days=i)
        next_date = date + timedelta(days=1)
        
        # Count activities for this day
        new_users = User.objects(created_at__gte=date, created_at__lt=next_date).count()
        new_collaborations = Collaboration.objects(created_at__gte=date, created_at__lt=next_date).count()
        new_files = EncryptedFile.objects(upload_date__gte=date, upload_date__lt=next_date).count()
        games_played = GameSession.objects(completed_at__gte=date, completed_at__lt=next_date).count()
        
        trends.append({
            "date": date.isoformat(),
            "new_users": new_users,
            "new_collaborations": new_collaborations,
            "new_files": new_files,
            "games_played": games_played
        })
    
    return trends

@router.get("/analytics/top-performers")
async def get_top_performers(
    metric: str = "kpi",
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get top performers by different metrics"""
    
    performers = []
    
    if metric == "kpi":
        profiles = UserArcadeProfile.objects().order_by('-kpi_balance').limit(limit)
        for profile in profiles:
            performers.append({
                "user": {
                    "id": str(profile.user.id),
                    "username": profile.user.username,
                    "display_name": profile.user.display_name
                },
                "value": profile.kpi_balance,
                "metadata": {
                    "total_earned": profile.total_kpi_earned,
                    "level": profile.level,
                    "games_played": profile.games_played
                }
            })
    
    elif metric == "collaborations":
        # Get users with most collaborations
        pipeline = [
            {"$group": {"_id": "$collaborator_name", "collaboration_count": {"$sum": 1}}},
            {"$sort": {"collaboration_count": -1}},
            {"$limit": limit}
        ]
        
        results = Collaboration.objects.aggregate(pipeline)
        for result in results:
            if result["_id"]:
                performers.append({
                    "id": result["_id"],
                    "username": result["_id"],
                    "display_name": result["_id"],
                    "value": result["collaboration_count"],
                    "metric": "collaborations"
                })
    
    elif metric == "files":
        # Get users with most uploaded files
        pipeline = [
            {"$group": {"_id": "$owner", "file_count": {"$sum": 1}}},
            {"$sort": {"file_count": -1}},
            {"$limit": limit}
        ]
        
        results = EncryptedFile.objects.aggregate(pipeline)
        for result in results:
            if result["_id"]:
                user = result["_id"]
                performers.append({
                    "user": {
                        "id": str(user.id),
                        "username": user.username,
                        "display_name": user.display_name
                    },
                    "value": result["file_count"],
                    "metadata": {
                        "role": user.role,
                        "status": user.status
                    }
                })
    
    return performers
