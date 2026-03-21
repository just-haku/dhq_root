from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["dhq_main"]

print("Users in dhq_main:")
for u in db.user.find():
    print(u.get("_id"), u.get("role"), "Quota:", u.get("storage_used_gb"))

print("\nExecuting update_quota_usage logic manually...")
used_gb = 0.5
size_change = -1024 * 1024 # -1MB
# The actual python logic is: quota.used_space = max(0, quota.used_space + size_change)
# Wait, DriveQuota model:
for q in db.drive_quota.find():
    print("Quota doc:", q)

