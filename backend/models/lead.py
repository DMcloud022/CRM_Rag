from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, Dict, Any

class Lead(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    linkedin_profile: Optional[HttpUrl] = None
    public_data: Optional[Dict[str, Any]] = {}