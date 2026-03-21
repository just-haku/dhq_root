import os, sys
sys.path.append("/home/haku/projects/DHQ_Root/backend")
from mongoengine import connect
from app.models.user import User
from app.models.drive import DriveQuota
from app.api.drive import get_user_quota, update_quota_usage

connect("dhq_main", host="mongodb://localhost:27017/dhq_main")

user = User.objects(username="kuro").first()
print("Found user:", user.username)

print("Calling get_user_quota...")
try:
    quota = get_user_quota(user)
    print("Quota obtained:", quota.id, quota.used_space)
except Exception as e:
    print("Crash in get_user_quota:", e)

print("Calling update_quota_usage with -1024...")
try:
    update_quota_usage(user, -1024)
    print("Update successful!")
except Exception as e:
    import traceback
    traceback.print_exc()
