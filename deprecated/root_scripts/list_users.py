from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["dhq"]

print("Users:")
for u in db.user.find():
    print(u.get("username"), u.get("_id"), u.get("role"))
