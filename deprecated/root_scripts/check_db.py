from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["dhq"]

kuro = db.user.find_one({"username": "kuro"})
print(f"Kuro ID: {kuro['_id']}")

print("All trash files for kuro:")
for f in db.drive_file.find({"owner": kuro["_id"], "is_deleted": True}):
    print(f["_id"], f["filename"], f["is_deleted"], f.get("file_path"))
