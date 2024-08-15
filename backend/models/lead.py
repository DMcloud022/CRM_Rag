from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class SocialProfile(BaseModel):
    type: str
    url: HttpUrl

class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class WorkExperience(BaseModel):
    company: str
    position: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class Education(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None

class PublicData(BaseModel):
    bio: Optional[str] = None
    skills: List[str] = []
    languages: List[str] = []
    interests: List[str] = []
    publications: List[str] = []
    awards: List[str] = []
    work_experience: List[WorkExperience] = []
    education: List[Education] = []

class Lead(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)
    website: Optional[HttpUrl] = None
    twitter_handle: Optional[str] = Field(None, max_length=50)
    address: Optional[Address] = None
    social_profiles: List[SocialProfile] = []
    public_data: Optional[PublicData] = None
    source: Optional[str] = "Business Card Scan"
    lifecycle_stage: Optional[str] = "lead"

class Company(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    domain: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    number_of_employees: Optional[int] = None
    annual_revenue: Optional[float] = None
    founded_year: Optional[int] = None
    address: Optional[Address] = None
    phone: Optional[str] = Field(None, max_length=20)
    linkedin_company_page: Optional[HttpUrl] = None
    facebook_company_page: Optional[HttpUrl] = None
    twitter_handle: Optional[str] = Field(None, max_length=50)

class Note(BaseModel):
    content: str
    timestamp: datetime
    associated_object_id: str
    association_type: int
    owner_id: Optional[str] = None
    note_type: Optional[str] = None

class CustomObject(BaseModel):
    properties: Dict[str, Any]