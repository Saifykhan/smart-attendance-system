from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["smart_attendance"]   # 👈 Yaha change karna hai
    print("✅ MongoDB Connected Successfully!")
except Exception as e:
    print("❌ Connection Failed:", e)
