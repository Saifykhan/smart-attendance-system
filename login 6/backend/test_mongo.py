from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/")
    
    DB_NAME = "smart_attendance"


    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print("❌ Connection Failed:", e)
