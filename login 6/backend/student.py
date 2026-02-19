from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models import UserCreate, UserOut, FaceRegister
from database import get_collection
from auth import hash_password, require_roles, get_current_user
from bson import ObjectId

router = APIRouter(prefix="/students", tags=["students"])

users_col = get_collection("users")

@router.post("/register", status_code=201)
async def register_student(payload: UserCreate):
    # Only allow creation of student role through admin or self-registration
    if users_col.find_one({"user_id": payload.user_id}):
        raise HTTPException(status_code=400, detail="user_id already exists")
    doc = {
        "name": payload.name,
        "user_id": payload.user_id,
        "password_hash": hash_password(payload.password),
        "role": payload.role,
        "created_at": None,
        "face_encodings": [],
        "face_images": []
    }
    users_col.insert_one(doc)
    return {"ok": True, "user_id": payload.user_id}

@router.get("/", response_model=List[UserOut])
async def list_students(current_user: dict = Depends(require_roles("teacher", "admin"))):
    docs = list(users_col.find({"role": "student"}, {"password_hash": 0}))
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs

@router.get("/{user_id}", response_model=UserOut)
async def get_student(user_id: str, current_user: dict = Depends(get_current_user)):
    # students can access only their own record
    doc = users_col.find_one({"user_id": user_id}, {"password_hash": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Student not found")
    # allow student to view own profile, teacher/admin to view any
    if current_user["role"] == "student" and current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    doc["id"] = str(doc.pop("_id"))
    return doc

@router.put("/{user_id}")
async def update_student(user_id: str, payload: dict, current_user: dict = Depends(require_roles("teacher", "admin"))):
    # allow teacher/admin to update student details
    res = users_col.update_one({"user_id": user_id, "role": "student"}, {"$set": payload})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"ok": True}

@router.delete("/{user_id}")
async def delete_student(user_id: str, current_user: dict = Depends(require_roles("teacher", "admin"))):
    res = users_col.delete_one({"user_id": user_id, "role": "student"})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"ok": True}

@router.post("/{user_id}/face")
async def add_face_data(user_id: str, data: FaceRegister, current_user: dict = Depends(get_current_user)):
    # Accept face images (base64) and/or face_encodings (list of floats)
    user = users_col.find_one({"user_id": user_id, "role": "student"})
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    # only student themselves or teacher/admin can upload
    if current_user["role"] == "student" and current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    ops = {}
    if data.face_images:
        ops.setdefault("$push", {})["face_images"] = {"$each": data.face_images}
    if data.face_encodings:
        ops.setdefault("$push", {})["face_encodings"] = {"$each": data.face_encodings}
    if ops:
        users_col.update_one({"user_id": user_id}, ops)
    return {"ok": True}
