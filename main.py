import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from database import db, create_document, get_documents
from schemas import Appointment, BlogPost, DoctorSettings

app = FastAPI(title="Doctor Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Doctor Portfolio API is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response

# -------- Appointment Endpoints --------

@app.post("/api/appointments")
def create_appointment(payload: Appointment):
    try:
        inserted_id = create_document("appointment", payload)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AppointmentQuery(BaseModel):
    email: Optional[EmailStr] = None
    date: Optional[str] = None

@app.get("/api/appointments")
def list_appointments(email: Optional[str] = None, date: Optional[str] = None):
    try:
        filt = {}
        if email:
            filt["email"] = email
        if date:
            filt["date"] = date
        docs = get_documents("appointment", filt)
        # Convert ObjectId to str
        for d in docs:
            d["_id"] = str(d["_id"]) if "_id" in d else None
            # Convert dates to ISO strings
            if isinstance(d.get("created_at"), datetime):
                d["created_at"] = d["created_at"].isoformat()
            if isinstance(d.get("updated_at"), datetime):
                d["updated_at"] = d["updated_at"].isoformat()
        return {"ok": True, "items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- Blog Endpoints --------

@app.post("/api/blogs")
def create_blog(payload: BlogPost):
    try:
        inserted_id = create_document("blogpost", payload)
        return {"ok": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/blogs")
def list_blogs(published: Optional[bool] = None):
    try:
        filt = {}
        if published is not None:
            filt["published"] = published
        docs = get_documents("blogpost", filt)
        for d in docs:
            d["_id"] = str(d["_id"]) if "_id" in d else None
            if isinstance(d.get("created_at"), datetime):
                d["created_at"] = d["created_at"].isoformat()
            if isinstance(d.get("updated_at"), datetime):
                d["updated_at"] = d["updated_at"].isoformat()
        return {"ok": True, "items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- Settings Endpoints --------

@app.get("/api/settings")
def get_settings():
    try:
        docs = get_documents("doctorsettings", {})
        if docs:
            d = docs[0]
            d["_id"] = str(d["_id"]) if "_id" in d else None
            return {"ok": True, "settings": d}
        # default fallback
        return {"ok": True, "settings": {"notification_email": os.getenv("DEFAULT_EMAIL", "doctor@example.com"), "available_slots": ["09:00", "10:00", "11:00", "14:00", "15:00"]}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/settings")
def update_settings(payload: DoctorSettings):
    try:
        # Simple upsert: if exists, replace first; else insert
        existing = get_documents("doctorsettings", {})
        from database import db
        data = payload.model_dump()
        data["updated_at"] = datetime.utcnow()
        if existing:
            _id = existing[0]["_id"]
            db["doctorsettings"].update_one({"_id": _id}, {"$set": data})
            return {"ok": True, "updated": True}
        else:
            create_document("doctorsettings", payload)
            return {"ok": True, "created": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
