"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Appointment -> "appointment" collection
- BlogPost -> "blogpost" collection
- DoctorSettings -> "doctorsettings" collection
"""

import datetime as _dt
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class Appointment(BaseModel):
    """
    Appointments booked by patients
    Collection: "appointment"
    """
    name: str = Field(..., description="Patient full name")
    email: EmailStr = Field(..., description="Patient email")
    phone: Optional[str] = Field(None, description="Contact number")
    date: _dt.date = Field(..., description="Appointment date (YYYY-MM-DD)")
    time: str = Field(..., description="Time slot (e.g., 10:30 AM)")
    note: Optional[str] = Field(None, description="Short note or reason")
    status: str = Field("pending", description="Status: pending|confirmed|cancelled")

class BlogPost(BaseModel):
    """
    Blog posts authored by the doctor/developer
    Collection: "blogpost"
    """
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Rich text/markdown content")
    cover_image: Optional[str] = Field(None, description="Optional cover image URL")
    tags: List[str] = Field(default_factory=list, description="Tags for the post")
    published: bool = Field(False, description="Whether the post is visible publicly")

class DoctorSettings(BaseModel):
    """
    Admin-editable settings
    Collection: "doctorsettings"
    """
    notification_email: EmailStr = Field(..., description="Email to receive appointment notifications")
    available_slots: Optional[List[str]] = Field(default_factory=list, description="List of allowed slot strings like '09:00', '10:30'")
