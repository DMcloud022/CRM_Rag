from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Header
from pydantic import BaseModel, EmailStr
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
    linkedin_profile: Optional[str] = None

async def get_api_key(api_key: str = Header(...)):
    expected_api_key = "test"
    if api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

@router.post("/scan-business-card", response_model=BusinessCardScanResponse)
async def scan_business_card(
    image: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    try:
        transcription_result = await transcribe_business_card(image)
        cleaned_data = clean_and_validate_transcription(transcription_result)
        
        public_data = transcription_result.get('public_data', {})
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
        raise HTTPException(status_code=500, detail=f"Error processing business card: {str(e)}")

@router.post("/gather-public-data")
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
        raise HTTPException(status_code=500, detail=f"Error gathering and summarizing public data: {str(e)}")

def clean_and_validate_transcription(transcription: Dict[str, Any]) -> Dict[str, Any]:
    cleaned_data = {}
    
    # Handle 'name' field
    name = transcription.get("name", "").strip()
    if name:
        name_parts = name.split(maxsplit=1)
        cleaned_data["first_name"] = name_parts[0]
        cleaned_data["last_name"] = name_parts[1] if len(name_parts) > 1 else ""
    else:
        cleaned_data["first_name"] = "Unknown"
        cleaned_data["last_name"] = ""
    
    cleaned_data["name"] = f"{cleaned_data['first_name']} {cleaned_data['last_name']}".strip()
    
    # Handle 'email' field with validation
    email = transcription.get("email", "").strip()
    if email:
        try:
            cleaned_data["email"] = EmailStr.validate(email)
        except ValueError:
            cleaned_data["email"] = None
    else:
        cleaned_data["email"] = None

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
            website=cleaned_data.get("website"),
            address=cleaned_data.get("address"),
            linkedin_profile=cleaned_data.get("linkedin_profile"),
            public_data=public_data
        )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=f"Invalid lead data: {str(ve)}")
