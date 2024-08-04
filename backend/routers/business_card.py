from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, Dict, Any
from services.image_processing import transcribe_business_card
from services.public_data import gather_public_data
from models.lead import Lead

router = APIRouter()

class BusinessCardScanResponse(BaseModel):
    lead: Lead
    message: str

@router.post("/scan-business-card", response_model=BusinessCardScanResponse)
async def scan_business_card(image: UploadFile = File(...)):
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File uploaded is not an image")

    try:
        transcription = await transcribe_business_card(image)
        
        # Validate and clean transcription data
        cleaned_data = clean_and_validate_transcription(transcription)
        
        # Gather public data
        public_data = await gather_public_data(cleaned_data.get("email"), cleaned_data.get("linkedin_profile"))
        
        try:
            lead = Lead(
                name=cleaned_data.get("name", "Unknown"),
                email=cleaned_data.get("email"),
                phone=cleaned_data.get("phone"),
                company=cleaned_data.get("company"),
                position=cleaned_data.get("job_title"),
                linkedin_profile=cleaned_data.get("linkedin_profile"),
                public_data=public_data
            )
        except ValueError as ve:
            raise HTTPException(status_code=422, detail=f"Invalid lead data: {str(ve)}")
        
        return BusinessCardScanResponse(
            lead=lead,
            message="Business card scanned and public data gathered successfully."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing business card: {str(e)}")

def clean_and_validate_transcription(transcription: Dict[str, Any]) -> Dict[str, Any]:
    cleaned_data = {}
    
    # Validate and clean each field
    if name := transcription.get("name"):
        cleaned_data["name"] = str(name).strip() or "Unknown"
    else:
        cleaned_data["name"] = "Unknown"
    
    if email := transcription.get("email"):
        try:
            cleaned_data["email"] = EmailStr.validate(email)
        except ValueError:
            cleaned_data["email"] = None
    
    if linkedin_profile := transcription.get("linkedin_profile"):
        try:
            cleaned_data["linkedin_profile"] = HttpUrl.validate(linkedin_profile)
        except ValueError:
            cleaned_data["linkedin_profile"] = None
    
    # Clean other fields
    for field in ["phone", "company", "job_title"]:
        if value := transcription.get(field):
            cleaned_data[field] = str(value).strip()
    
    return cleaned_data


