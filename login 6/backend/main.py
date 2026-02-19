from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from database import get_collection
from auth import create_access_token, hash_password
from datetime import timedelta
import uvicorn

# routers
from student import router as student_router
from teacher import router as teacher_router
from admin import router as admin_router
from attendance import router as attendance_router
from auth import pwd_context

app = FastAPI(title="Smart Attendance - Backend")

# CORS - allow everything for local development (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router)
app.include_router(teacher_router)
app.include_router(admin_router)
app.include_router(attendance_router)

# Simple login endpoint (keeps frontend compatibility with /login)
@app.post("/login")
async def login(payload: dict):
    user_id = payload.get("user_id")
    password = payload.get("password")
    if not user_id or not password:
        return {"error": "user_id and password required"}
    users = get_collection("users")
    user = users.find_one({"user_id": user_id})
    if not user:
        return {"error": "invalid credentials"}
    if not pwd_context.verify(password, user["password_hash"]):
        return {"error": "invalid credentials"}
    token = create_access_token({"user_id": user_id, "role": user["role"]})
    return {"token": token, "role": user["role"], "user_id": user_id}

# Startup: ensure indexes and seed admin/teacher/student for quick testing
@app.on_event("startup")
async def startup_event():
    users = get_collection("users")
    users.create_index("user_id", unique=True, name="idx_user_id")

    att = get_collection("attendance")
    att.create_index([("student_user_id", 1), ("date", 1)], unique=False)

    # seed default accounts if not present
    def _ensure(user_id, name, password, role):
        if not users.find_one({"user_id": user_id}):
            users.insert_one({
                "name": name,
                "user_id": user_id,
                "password_hash": hash_password(password),
                "role": role,
                "face_encodings": []
            })
    _ensure("admin", "Administrator", "admin123", "admin")
    _ensure("teacher", "Teacher One", "teacher123", "teacher")
    _ensure("student", "Student One", "student123", "student")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
@app.get("/")
def home():
    return {"message": "Smart Attendance Backend Running"}
