from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from database import get_collection
from auth import require_roles, get_current_user
from datetime import datetime, date
import math

router = APIRouter(prefix="/attendance", tags=["attendance"])

users_col = get_collection("users")
att_col = get_collection("attendance")

# utility: euclidean distance between two vectors
def euclidean(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

@router.post("/auto")
async def auto_attendance(payload: dict, current_user: dict = Depends(require_roles("teacher", "admin"))):
    """
    Payload example: { "face_encoding": [0.12, 0.32, ...] }
    Matches against stored `face_encodings` in student documents and marks attendance for the matched student
    """
    enc = payload.get("face_encoding")
    if not enc or not isinstance(enc, list):
        raise HTTPException(status_code=400, detail="face_encoding required")

    # brute-force search across students
    best = {"user_id": None, "score": 1e9}
    for s in users_col.find({"role": "student", "face_encodings": {"$exists": True, "$ne": []}}, {"user_id": 1, "face_encodings": 1}):
        for stored in s.get("face_encodings", []):
            try:
                d = euclidean(enc, stored)
            except Exception:
                continue
            if d < best["score"]:
                best = {"user_id": s["user_id"], "score": d}

    # threshold for face-api descriptors (typical ~0.6) - configurable
    THRESHOLD = 0.62
    if best["user_id"] is None or best["score"] > THRESHOLD:
        return {"matched": False, "reason": "no match", "best_score": best["score"]}

    # mark attendance for today for matched student
    today = date.today().isoformat()
    existing = att_col.find_one({"student_user_id": best["user_id"], "date": today})
    if existing:
        return {"ok": True, "already_marked": True, "student_user_id": best["user_id"], "score": best["score"]}

    att_col.insert_one({
        "student_user_id": best["user_id"],
        "date": today,
        "status": "present",
        "marked_by": current_user["user_id"],
        "timestamp": datetime.utcnow(),
        "score": float(best["score"])
    })
    return {"ok": True, "student_user_id": best["user_id"], "score": best["score"]}

@router.post("/manual")
async def manual_attendance(payload: dict, current_user: dict = Depends(require_roles("teacher", "admin"))):
    # payload: { student_user_id: str, status: 'present'|'absent', date?: 'YYYY-MM-DD' }
    student_user_id = payload.get("student_user_id")
    status = payload.get("status", "present")
    if not student_user_id:
        raise HTTPException(status_code=400, detail="student_user_id required")
    d = payload.get("date", date.today().isoformat())
    att_col.update_one({"student_user_id": student_user_id, "date": d}, {"$set": {"status": status, "marked_by": current_user["user_id"], "timestamp": datetime.utcnow()}}, upsert=True)
    return {"ok": True}

@router.get("/student/{user_id}")
async def get_student_attendance(user_id: str, current_user: dict = Depends(get_current_user)):
    # students can view only their own attendance
    if current_user["role"] == "student" and current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    docs = list(att_col.find({"student_user_id": user_id}).sort([("date", -1)]))
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return {"attendance": docs}

@router.get("/date/{d}")
async def attendance_by_date(d: str, current_user: dict = Depends(require_roles("teacher", "admin"))):
    docs = list(att_col.find({"date": d}))
    for doc in docs:
        doc["id"] = str(doc.pop("_id"))
    return {"date": d, "records": docs}
