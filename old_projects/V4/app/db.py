from pymongo import MongoClient
import os

# You can set your MongoDB URI via an environment variable, or use a default value.
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

# Create a MongoClient instance
client = MongoClient(MONGO_URI)

# Choose a database name (change "my_database" as needed)
db = client["my_database"]

# Optionally, you can create and export collections here.
global_settings_collection = db["global_settings"]
plots_collection = db["plots"]
users_collection = db["users"]
# Add more collections as needed.
