from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["dhq"]

print("Finding file 69a673d24ca9eec5695ffec8...")
try:
    file = db.drive_file.find_one({"_id": ObjectId("69a673d24ca9eec5695ffec8")})
    print("Found file:")
    print(file)
except Exception as e:
    print("Error:", e)
