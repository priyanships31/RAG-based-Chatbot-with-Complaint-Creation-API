from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class ComplaintCreate(BaseModel):
    name: str = Field(..., min_length=2)
    phone_number: str = Field(..., min_length=10, max_length=15, pattern=r"^[0-9]+$")
    email: EmailStr
    complaint_details: str = Field(..., min_length=10)

class ComplaintResponse(BaseModel):
    complaint_id: str
    name: str
    phone_number: str
    email: str
    complaint_details: str
    created_at: datetime