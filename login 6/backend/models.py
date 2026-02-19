from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

# Auth / User models
class UserCreate(BaseModel):
    name: str
    user_id: str
    password: str
    role: str = "student"  # student | teacher | admin

class UserOut(BaseModel):
    id: str
    name: str
    user_id: str
    role: str

class LoginRequest(BaseModel):
    user_id: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str

# Student-face models
class FaceRegister(BaseModel):
    user_id: str
    face_images: Optional[List[str]] = None   # data URLs (optional)
    face_encodings: Optional[List[List[float]]] = None

# Attendance models
class AttendanceMark(BaseModel):
    user_id: Optional[str]
    student_user_id: Optional[str]
    status: str = "present"  # present | absent
    marked_by: Optional[str]
    face_encoding: Optional[List[float]]
    timestamp: Optional[datetime]

class AttendanceResponse(BaseModel):
    student_user_id: str
    date: str
    status: str
    marked_by: Optional[str]
    score: Optional[float]

# Generic list responses
class StudentsList(BaseModel):
    students: List[Any]

class TeachersList(BaseModel):
    teachers: List[Any]
