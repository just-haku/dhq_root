from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["dhq"]

print("Collections in dhq:")
print(db.list_collection_names())
