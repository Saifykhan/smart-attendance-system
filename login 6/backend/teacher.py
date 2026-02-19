from fastapi import APIRouter, Depends, HTTPException
from typing import List
from database import get_collection
from auth import require_roles, get_current_user

router = APIRouter(prefix="/teachers", tags=["teachers"])

users_col = get_collection("users")

@router.get("/", dependencies=[Depends(require_roles("admin"))])
async def list_teachers():
    docs = list(users_col.find({"role": "teacher"}, {"password_hash": 0}))
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return {"teachers": docs}

@router.get("/me")
async def get_me(current_user: dict = Depends(require_roles("teacher", "admin", "student"))):
    # simple profile endpoint
    return {"user_id": current_user["user_id"], "name": current_user["name"], "role": current_user["role"]}
