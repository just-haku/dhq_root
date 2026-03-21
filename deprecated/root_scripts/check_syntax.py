from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["dhq"]

print("Server API Drive File:")
with open("/home/haku/projects/DHQ_Root/backend/app/api/drive.py", "r") as f:
    content = f.read()
    print("Does update_quota_usage exist?", "update_quota_usage" in content)

print("Look at delete_trash_item block around 760:")
lines = content.split('\n')
for i, line in enumerate(lines):
    if "update_quota_usage(current_user" in line:
        for offset in range(-5, 5):
            print(lines[i + offset])
