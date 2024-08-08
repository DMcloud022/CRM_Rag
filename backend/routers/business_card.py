import logging
import re
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Header
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Dict, Any
from models.lead import Lead
from services.image_processing import transcribe_business_card
from services.public_data import gather_public_data, summarize_public_data

router = APIRouter()

class BusinessCardScanResponse(BaseModel):
    lead: Lead
    public_data_summary: str
    message: str

class PublicDataRequest(BaseModel):
    email: Optional[EmailStr] = None
    linkedin_profile: Optional[HttpUrl] = None

async def get_api_key(api_key: str = Header(..., description="API Key for authentication")):
    expected_api_key = "test"  # In production, use a secure method to store and retrieve API keys
    if api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

@router.post("/scan-business-card", response_model=BusinessCardScanResponse)
async def scan_business_card(
    image: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
) -> BusinessCardScanResponse:
    try:
        transcription_result = await transcribe_business_card(image)
        
        if "error" in transcription_result:
            raise HTTPException(status_code=500, detail=transcription_result["error"])
        
        cleaned_data = clean_and_validate_transcription(transcription_result)
        public_data = await gather_public_data(cleaned_data.get("email"), cleaned_data.get("linkedin_profile"))
        public_data_summary = await summarize_public_data(public_data)
        lead = create_lead(cleaned_data, public_data)
        
        return BusinessCardScanResponse(
            lead=lead,
            public_data_summary=public_data_summary,
            message="Business card scanned and public data gathered successfully."
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(f"Error in scan_business_card: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing business card: {str(e)}")

@router.post("/gather-public-data", response_model=Dict[str, Any])
async def gather_public_data_route(
    request: PublicDataRequest,
    api_key: str = Depends(get_api_key)
) -> Dict[str, Any]:
    try:
        public_data = await gather_public_data(request.email, request.linkedin_profile)
        summary = await summarize_public_data(public_data)
        
        return {
            "public_data": public_data,
            "summary": summary
        }
    except Exception as e:
        logging.error(f"Error in gather_public_data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error gathering and summarizing public data: {str(e)}")

def clean_and_validate_transcription(transcription: Dict[str, Any]) -> Dict[str, Any]:
    cleaned_data = {
        "first_name": "Unknown",
        "last_name": "",
        "email": None,
    }

    # Handle 'name' field
    name = transcription.get("name", "").strip()
    if name:
        name_parts = name.split(maxsplit=1)
        cleaned_data["first_name"] = name_parts[0]
        cleaned_data["last_name"] = name_parts[1] if len(name_parts) > 1 else ""

    cleaned_data["name"] = f"{cleaned_data['first_name']} {cleaned_data['last_name']}".strip()

    # Handle 'email' field with validation
    email = transcription.get("email", "").strip()
    if email and re.match(r"[^@]+@[^@]+\.[^@]+", email):
        cleaned_data["email"] = email

    # Handle other fields
    for field in ["phone", "company", "address", "job_title", "linkedin_profile", "website"]:
        value = transcription.get(field, "").strip()
        if value:
            cleaned_data[field] = value

    return cleaned_data

def create_lead(cleaned_data: Dict[str, Any], public_data: Dict[str, Any]) -> Lead:
    try:
        return Lead(
            name=cleaned_data.get("name", "Unknown"),
            email=cleaned_data.get("email"),
            phone=cleaned_data.get("phone"),
            company=cleaned_data.get("company"),
            position=cleaned_data.get("job_title"),
            linkedin_profile=cleaned_data.get("linkedin_profile"),
            public_data=public_data
        )
    except ValueError as ve:
        logging.error(f"Invalid lead data: {str(ve)}")
        raise HTTPException(status_code=422, detail=f"Invalid lead data: {str(ve)}")