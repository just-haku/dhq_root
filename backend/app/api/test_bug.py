from fastapi import APIRouter
from app.models.user import User
from app.api.drive import get_user_quota, update_quota_usage

router = APIRouter()

@router.get("/test-quota-crash")
async def test_quota_crash():
    try:
        user = User.objects(username="kuro").first()
        if not user:
            return {"error": "User kuro not found"}
            
        print("Got user:", user.username)
        # Try to get quota
        try:
            q = get_user_quota(user)
            return {"success": True, "quota_used": q.used_space}
        except Exception as e:
            return {"error": f"Crash in get_user_quota: {str(e)}"}
            
    except Exception as e:
        return {"error": f"General crash: {str(e)}"}
