from pymongo import MongoClient

MONGO_URI = "mongodb+srv://aishwaryasingh2410_db_user:OcS6Wltiz3jNcA1g@cluster0.sdicuyj.mongodb.net/cursor_database"

client = MongoClient(MONGO_URI)

db = client["cursor_database"]

options_collection = db["options_chain"]