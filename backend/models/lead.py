from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, Dict, Any

class Lead(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    linkedin_profile: Optional[HttpUrl] = None
    public_data: Optional[Dict[str, Any]] = {}