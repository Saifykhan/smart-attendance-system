from fastapi import APIRouter, Depends, HTTPException
from database import get_collection
from auth import hash_password, require_roles
from models import UserCreate

router = APIRouter(prefix="/admin", tags=["admin"])

users_col = get_collection("users")

@router.post("/add-user")
async def add_user(payload: UserCreate, current_user: dict = Depends(require_roles("admin"))):
    if users_col.find_one({"user_id": payload.user_id}):
        raise HTTPException(status_code=400, detail="user_id already exists")
    doc = {
        "name": payload.name,
        "user_id": payload.user_id,
        "password_hash": hash_password(payload.password),
        "role": payload.role,
        "created_at": None
    }
    users_col.insert_one(doc)
    return {"ok": True, "user_id": payload.user_id}

@router.get("/users")
async def list_users(current_user: dict = Depends(require_roles("admin"))):
    docs = list(users_col.find({}, {"password_hash": 0}))
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return {"users": docs}

@router.put("/users/{user_id}")
async def update_user(user_id: str, payload: dict, current_user: dict = Depends(require_roles("admin"))):
    res = users_col.update_one({"user_id": user_id}, {"$set": payload})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(require_roles("admin"))):
    res = users_col.delete_one({"user_id": user_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}
