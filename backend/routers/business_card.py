import logging
import re
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Header, Query
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Dict, Any
from models.lead import Lead
from services.image_processing import transcribe_business_card
from services.public_data import gather_public_data, enrich_lead_with_public_data
from services.crm_integration.hubspot import create_lead_in_hubspot

router = APIRouter()

class BusinessCardScanResponse(BaseModel):
    lead: Lead
    message: str

class PublicDataRequest(BaseModel):
    email: Optional[EmailStr] = None
    # linkedin_profile: Optional[HttpUrl] = None

async def get_api_key(api_key: str = Header(..., description="API Key for authentication")):
    expected_api_key = "test"  # In production, use a secure method to store and retrieve API keys
    if api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

@router.post("/scan-business-card", response_model=BusinessCardScanResponse)
async def scan_business_card(
    image: UploadFile = File(...),
    access_token: str = Query(..., description="OAuth access token for HubSpot authentication"),
    api_key: str = Depends(get_api_key)
) -> BusinessCardScanResponse:
    try:
        logging.info("Starting business card scan")
        transcription_result = await transcribe_business_card(image)
        
        if "error" in transcription_result:
            logging.error(f"Transcription error: {transcription_result['error']}")
            raise HTTPException(status_code=500, detail=transcription_result["error"])
        
        logging.info("Transcription successful, cleaning data")
        cleaned_data = clean_and_validate_transcription(transcription_result)
        
        logging.info("Gathering public data")
        public_data = await gather_public_data(
            cleaned_data.get("email"), 
            # cleaned_data.get("linkedin_profile")
        )
        
        logging.info("Creating lead")
        lead = create_lead(cleaned_data)
        
        logging.info("Enriching lead with public data")
        enriched_lead = await enrich_lead_with_public_data(lead, public_data)
        
        logging.info("Sending lead to HubSpot")
        hubspot_response = await create_lead_in_hubspot(enriched_lead, access_token)
        
        return BusinessCardScanResponse(
            lead=enriched_lead,
            message="Business card scanned, public data gathered, and lead created in HubSpot successfully."
        )

    except HTTPException as he:
        logging.error(f"HTTP Exception: {str(he)}")
        raise he
    except Exception as e:
        logging.error(f"Error in scan_business_card: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing business card: {str(e)}")

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

    # Handle 'email' field with validation
    email = transcription.get("email", "").strip()
    if email and re.match(r"[^@]+@[^@]+\.[^@]+", email):
        cleaned_data["email"] = email

    # Handle other fields
    for field in ["phone", "company", "job_title", "website", "twitter_handle"]:
        value = transcription.get(field, "").strip()
        if value:
            cleaned_data[field] = value

    return cleaned_data

def create_lead(cleaned_data: Dict[str, Any]) -> Lead:
    try:
        return Lead(
            first_name=cleaned_data.get("first_name", "Unknown"),
            last_name=cleaned_data.get("last_name", ""),
            email=cleaned_data.get("email"),
            phone=cleaned_data.get("phone"),
            company=cleaned_data.get("company"),
            job_title=cleaned_data.get("job_title"),
            # linkedin_profile=cleaned_data.get("linkedin_profile"),
            website=cleaned_data.get("website"),
            twitter_handle=cleaned_data.get("twitter_handle"),
        )
    except ValueError as ve:
        logging.error(f"Invalid lead data: {str(ve)}")
        raise HTTPException(status_code=422, detail=f"Invalid lead data: {str(ve)}")
