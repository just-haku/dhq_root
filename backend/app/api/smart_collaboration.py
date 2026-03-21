from fastapi import APIRouter, HTTPException, Depends
from app.models.user import User
from app.models.collaboration import Collaboration, VideoUnit
from app.api.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class VideoUnitRequest(BaseModel):
    title: str
    caption: str
    script: Optional[str] = None
    subtitles_text: Optional[str] = None
    invitation: bool = False
    post_links: dict = {}
    tags: List[str] = []
    subtitles_needed: bool = False
    media_path: Optional[str] = None
    paid: bool = False
    done: bool = False

class CollaborationRequest(BaseModel):
    name: str
    service_name: str = "Default Service"
    collaborator_name: str = "Unknown"
    collaborator_email: Optional[str] = None
    type: str  # Paid, Product, Paid Product
    agreed_price: Optional[float] = None
    tracking_number: Optional[str] = None
    term: str = "Short"  # Long, Short
    duration: str = "TBD"
    contract_link: Optional[str] = None
    posting_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    other_notes: Optional[str] = None
    scope: str = "Product"  # App/Product
    channel: str
    platforms: List[str] = []
    videos: List[VideoUnitRequest] = []

class VideoUpdateRequest(BaseModel):
    video_index: int
    completed: Optional[bool] = None
    media_path: Optional[str] = None
    subtitles_needed: Optional[bool] = None
    subtitles: Optional[List[dict]] = None
    edits_needed: Optional[bool] = None
    edits_notes: Optional[str] = None
    video_updated: Optional[bool] = None
    approved: Optional[bool] = None
    platform_link: Optional[str] = None
    proof_link: Optional[str] = None

@router.post("/collaborations")
async def create_collaboration(
    request: CollaborationRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new collaboration for content creator channel"""
    
    try:
        # Validate required fields
        if request.type == "Paid" and not request.agreed_price:
            raise HTTPException(status_code=400, detail="Agreed price is required for paid collaborations")
        
        # We removed the hard deadline requirement to tolerate simpler payloads
        
        # Create video units
        video_units = []
        for video_req in request.videos:
            video_unit = VideoUnit(
                title=video_req.title,
                caption=video_req.caption,
                script=video_req.script,
                subtitles_text=video_req.subtitles_text,
                invitation=video_req.invitation,
                post_links=video_req.post_links,
                tags=video_req.tags,
                subtitles_needed=video_req.subtitles_needed,
                media_path=video_req.media_path,
                paid=video_req.paid,
                done=video_req.done
            )
            video_units.append(video_unit)
        
        # Create collaboration
        collaboration = Collaboration(
            name=request.name,
            collaborator_name=request.collaborator_name,
            collaborator_email=request.collaborator_email,
            type=request.type,
            agreed_price=request.agreed_price,
            tracking_number=request.tracking_number,
            term=request.term,
            duration=request.duration,
            contract_link=request.contract_link,
            posting_date=request.posting_date,
            deadline=request.deadline,
            other_notes=request.other_notes,
            scope=request.scope,
            channel=request.channel,
            platform=request.platforms if request.platforms else ["Unknown"],
            videos=video_units
        )
        
        collaboration.save()
        
        return {
            "message": "Collaboration created successfully!",
            "collaboration_id": str(collaboration.id),
            "name": request.name,
            "collaborator": request.collaborator_name,
            "type": request.type,
            "deadline": request.deadline.isoformat() if request.deadline else None,
            "total_videos": len(video_units)
        }
        
    except Exception as e:
        logger.error(f"Error creating collaboration: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/collaborations/{collab_id}")
async def update_collaboration(
    collab_id: str,
    request: CollaborationRequest,
    current_user: User = Depends(get_current_user)
):
    """Update a full collaboration element via standard mapped attributes"""
    try:
        collab = Collaboration.objects(id=collab_id).first()
        if not collab:
            raise HTTPException(status_code=404, detail="Collaboration not found")
        
        # update fields
        collab.name = request.name
        collab.collaborator_name = request.collaborator_name
        collab.collaborator_email = request.collaborator_email
        collab.type = request.type
        collab.agreed_price = request.agreed_price
        collab.tracking_number = request.tracking_number
        collab.term = request.term
        collab.duration = request.duration
        collab.contract_link = request.contract_link
        collab.posting_date = request.posting_date
        collab.deadline = request.deadline
        collab.other_notes = request.other_notes
        collab.scope = request.scope
        collab.channel = request.channel
        collab.platform = request.platforms if request.platforms else ["Unknown"]
        
        # recreate video units
        video_units = []
        for video_req in request.videos:
            video_unit = VideoUnit(
                title=video_req.title,
                caption=video_req.caption,
                script=video_req.script,
                subtitles_text=video_req.subtitles_text,
                invitation=video_req.invitation,
                post_links=video_req.post_links,
                tags=video_req.tags,
                subtitles_needed=video_req.subtitles_needed,
                media_path=video_req.media_path,
                paid=video_req.paid,
                done=video_req.done
            )
            video_units.append(video_unit)
        collab.videos = video_units
        
        collab.save()
        return {"message": "Collaboration updated successfully"}
    except Exception as e:
        logger.error(f"Error updating collaboration: {e}")
        raise HTTPException(status_code=500, detail="Failed to update collaboration")

@router.get("/collaborations")
async def get_collaborations(
    status_filter: Optional[str] = None,
    platform_filter: Optional[str] = None,
    upcoming_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Get collaborations with smart filtering"""
    
    query = {}
    
    # Apply filters
    if platform_filter:
        query["platform"] = platform_filter
    
    if upcoming_only:
        query["deadline"] = {"$gte": datetime.utcnow()}
    
    collaborations = Collaboration.objects(**query).order_by('deadline')
    
    result = []
    for collab in collaborations:
        # Calculate progress and status
        total_videos = len(collab.videos)
        completed_videos = sum(1 for video in collab.videos if video.completed)
        approved_videos = sum(1 for video in collab.videos if video.approved)
        
        # Determine status
        now = datetime.utcnow()
        if collab.status in ["Halted", "Declined"]:
            status = collab.status
        else:
            all_paid_and_done = True
            for video in collab.videos:
                price_required = collab.agreed_price and collab.agreed_price > 0
                if not video.done or (price_required and not video.paid):
                    all_paid_and_done = False
                    break
            
            if total_videos > 0 and all_paid_and_done:
                status = "Done"
            else:
                status = "On Going"
        
        # Apply status filter if provided
        if status_filter and status != status_filter:
            continue
        
        # Check package status for product collaborations
        package_status = "not_received"
        if collab.type in ["Product", "Paid Product"]:
            if collab.package_received:
                package_status = "received"
            elif collab.tracking_number:
                package_status = "shipped"
        
        result.append({
            "id": str(collab.id),
            "name": collab.name,
            "collaborator": collab.collaborator_name,
            "collaborator_email": collab.collaborator_email,
            "type": collab.type,
            "platform": collab.platform,
            "channel": collab.channel,
            "scope": collab.scope,
            "deadline": collab.deadline.isoformat() if collab.deadline else None,
            "posting_date": collab.posting_date.isoformat() if collab.posting_date else None,
            "status": status,
            "package_status": package_status,
            "tracking_number": collab.tracking_number,
            "agreed_price": collab.agreed_price,
            "total_videos": total_videos,
            "completed_videos": completed_videos,
            "approved_videos": approved_videos,
            "progress_percentage": (completed_videos / total_videos * 100) if total_videos > 0 else 0,
            "created_at": collab.created_at.isoformat()
        })
    
    return {
        "collaborations": result,
        "total": len(result)
    }

@router.get("/collaborations/{collaboration_id}")
async def get_collaboration_details(
    collaboration_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed collaboration information"""
    
    collaboration = Collaboration.objects(id=collaboration_id).first()
    if not collaboration:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    
    # Process videos with detailed status
    videos = []
    for i, video in enumerate(collaboration.videos):
        video_status = "pending"
        if video.approved:
            video_status = "approved"
        elif video.completed:
            video_status = "completed"
        elif video.video_updated:
            video_status = "review_needed"
        elif video.edits_needed:
            video_status = "edits_needed"
        
        videos.append({
            "index": i,
            "title": video.title,
            "caption": video.caption,
            "tags": video.tags,
            "status": video_status,
            "media_path": video.media_path,
            "subtitles_needed": video.subtitles_needed,
            "subtitles": video.subtitles,
            "edits_needed": video.edits_needed,
            "edits_notes": video.edits_notes,
            "video_updated": video.video_updated,
            "approved": video.approved,
            "platform_link": video.platform_link,
            "proof_link": video.proof_link
        })
    
    # Calculate overall statistics
    total_videos = len(collaboration.videos)
    completed_videos = sum(1 for video in collaboration.videos if video.completed)
    approved_videos = sum(1 for video in collaboration.videos if video.approved)
    
    # Check deadline urgency
    urgency = "normal"
    if collaboration.deadline:
        days_until_deadline = (collaboration.deadline - datetime.utcnow()).days
        if days_until_deadline < 0:
            urgency = "overdue"
        elif days_until_deadline <= 3:
            urgency = "urgent"
        elif days_until_deadline <= 7:
            urgency = "soon"
    
    return {
        "collaboration": {
            "id": str(collaboration.id),
            "name": collaboration.name,
            "collaborator_name": collaboration.collaborator_name,
            "collaborator_email": collaboration.collaborator_email,
            "type": collaboration.type,
            "agreed_price": collaboration.agreed_price,
            "tracking_number": collaboration.tracking_number,
            "package_received": collaboration.package_received,
            "term": collaboration.term,
            "duration": collaboration.duration,
            "contract_link": collaboration.contract_link,
            "posting_date": collaboration.posting_date.isoformat() if collaboration.posting_date else None,
            "deadline": collaboration.deadline.isoformat() if collaboration.deadline else None,
            "other_notes": collaboration.other_notes,
            "scope": collaboration.scope,
            "channel": collaboration.channel,
            "platform": collaboration.platform,
            "urgency": urgency,
            "created_at": collaboration.created_at.isoformat(),
            "statistics": {
                "total_videos": total_videos,
                "completed_videos": completed_videos,
                "approved_videos": approved_videos,
                "completion_rate": (completed_videos / total_videos * 100) if total_videos > 0 else 0,
                "approval_rate": (approved_videos / total_videos * 100) if total_videos > 0 else 0
            },
            "videos": videos
        }
    }

@router.put("/collaborations/{collaboration_id}/videos")
async def update_video_status(
    collaboration_id: str,
    request: VideoUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update video status in collaboration"""
    
    collaboration = Collaboration.objects(id=collaboration_id).first()
    if not collaboration:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    
    # Validate video index
    if request.video_index >= len(collaboration.videos):
        raise HTTPException(status_code=400, detail="Invalid video index")
    
    video = collaboration.videos[request.video_index]
    
    # Update video fields
    if request.completed is not None:
        video.completed = request.completed
    if request.media_path is not None:
        video.media_path = request.media_path
    if request.subtitles_needed is not None:
        video.subtitles_needed = request.subtitles_needed
    if request.subtitles is not None:
        video.subtitles = request.subtitles
    if request.edits_needed is not None:
        video.edits_needed = request.edits_needed
    if request.edits_notes is not None:
        video.edits_notes = request.edits_notes
    if request.video_updated is not None:
        video.video_updated = request.video_updated
    if request.approved is not None:
        video.approved = request.approved
    if request.platform_link is not None:
        video.platform_link = request.platform_link
    if request.proof_link is not None:
        video.proof_link = request.proof_link
    
    collaboration.save()
    
    return {
        "message": "Video status updated successfully",
        "collaboration_id": collaboration_id,
        "video_index": request.video_index,
        "video_title": video.title,
        "updated_fields": [k for k, v in request.dict().items() if v is not None and k != "video_index"]
    }

@router.put("/collaborations/{collaboration_id}/package")
async def update_package_status(
    collaboration_id: str,
    received: bool,
    tracking_number: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Update package status for collaboration"""
    
    collaboration = Collaboration.objects(id=collaboration_id).first()
    if not collaboration:
        raise HTTPException(status_code=404, detail="Collaboration not found")
    
    if collaboration.type not in ["Product", "Paid Product"]:
        raise HTTPException(status_code=400, detail="Package tracking only available for product collaborations")
    
    collaboration.package_received = received
    if tracking_number:
        collaboration.tracking_number = tracking_number
    
    collaboration.save()
    
    return {
        "message": "Package status updated successfully",
        "collaboration_id": collaboration_id,
        "package_received": received,
        "tracking_number": collaboration.tracking_number
    }

@router.delete("/collaborations/{collab_id}/delete")
async def delete_collaboration(
    collab_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a collaboration"""
    try:
        collaboration = Collaboration.objects(id=collab_id).first()
        if not collaboration:
            raise HTTPException(status_code=404, detail="Collaboration not found")
        
        collaboration.delete()
        return {"message": "Collaboration deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting collaboration: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete collaboration")

@router.get("/collaborations/dashboard/stats")
async def get_collaboration_dashboard_stats(
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics for collaborations"""
    
    collaborations = Collaboration.objects()
    
    # Calculate statistics
    total_collaborations = collaborations.count()
    
    # Status breakdown
    pending_count = 0
    in_progress_count = 0
    completed_count = 0
    overdue_count = 0
    
    # Platform breakdown
    platform_stats = {}
    
    # Type breakdown
    type_stats = {"Paid": 0, "Product": 0, "Paid Product": 0}
    
    # Urgent deadlines
    urgent_deadlines = []
    
    now = datetime.utcnow()
    
    for collab in collaborations:
        # Status calculation
        total_videos = len(collab.videos)
        completed_videos = sum(1 for video in collab.videos if video.completed)
        approved_videos = sum(1 for video in collab.videos if video.approved)
        
        if collab.deadline and collab.deadline < now:
            overdue_count += 1
        elif completed_videos == total_videos and approved_videos == total_videos:
            completed_count += 1
        elif completed_videos > 0:
            in_progress_count += 1
        else:
            pending_count += 1
        
        # Platform stats
        for p in collab.platform:
            platform_stats[p] = platform_stats.get(p, 0) + 1
        
        # Type stats
        type_stats[collab.type] = type_stats.get(collab.type, 0) + 1
        
        # Urgent deadlines (within 7 days)
        if collab.deadline:
            days_until = (collab.deadline - now).days
            if 0 <= days_until <= 7:
                urgent_deadlines.append({
                    "collaboration_id": str(collab.id),
                    "name": collab.name,
                    "collaborator": collab.collaborator_name,
                    "deadline": collab.deadline.isoformat(),
                    "days_remaining": days_until
                })
    
    # Sort urgent deadlines by days remaining
    urgent_deadlines.sort(key=lambda x: x["days_remaining"])
    
    return {
        "overview": {
            "total_collaborations": total_collaborations,
            "pending": pending_count,
            "in_progress": in_progress_count,
            "completed": completed_count,
            "overdue": overdue_count
        },
        "platform_breakdown": platform_stats,
        "type_breakdown": type_stats,
        "urgent_deadlines": urgent_deadlines[:5],  # Top 5 most urgent
        "completion_rate": (completed_count / total_collaborations * 100) if total_collaborations > 0 else 0
    }

@router.post("/collaborations/{collab_id}/halt")
async def halt_collaboration(
    collab_id: str,
    current_user: User = Depends(get_current_user)
):
    """Halt a collaboration"""
    try:
        collaboration = Collaboration.objects(id=collab_id).first()
        if not collaboration:
            raise HTTPException(status_code=404, detail="Collaboration not found")
        
        collaboration.status = "Halted"
        collaboration.save()
        return {"message": "Collaboration halted successfully"}
    except Exception as e:
        logger.error(f"Error halting collaboration: {e}")
        raise HTTPException(status_code=500, detail="Failed to halt collaboration")

@router.post("/collaborations/{collab_id}/decline")
async def decline_collaboration(
    collab_id: str,
    current_user: User = Depends(get_current_user)
):
    """Decline a collaboration"""
    try:
        collaboration = Collaboration.objects(id=collab_id).first()
        if not collaboration:
            raise HTTPException(status_code=404, detail="Collaboration not found")
        
        collaboration.status = "Declined"
        collaboration.save()
        return {"message": "Collaboration declined successfully"}
    except Exception as e:
        logger.error(f"Error declining collaboration: {e}")
        raise HTTPException(status_code=500, detail="Failed to decline collaboration")

@router.post("/collaborations/{collab_id}/resume")
async def resume_collaboration(
    collab_id: str,
    current_user: User = Depends(get_current_user)
):
    """Resume a halted collaboration"""
    try:
        collaboration = Collaboration.objects(id=collab_id).first()
        if not collaboration:
            raise HTTPException(status_code=404, detail="Collaboration not found")
        
        collaboration.status = "On Going"
        collaboration.save()
        return {"message": "Collaboration resumed successfully"}
    except Exception as e:
        logger.error(f"Error resuming collaboration: {e}")
        raise HTTPException(status_code=500, detail="Failed to resume collaboration")
