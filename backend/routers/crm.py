import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from services.crm_integration import send_lead_to_crm, initiate_oauth, exchange_code_for_token
from models.lead import Lead
from models.oauth import OAuthCredentials
from utils.oauth import get_oauth_credentials
from utils.rate_limiter import rate_limit
from utils.cache import cache
from typing import Dict, Any
from config import SUPPORTED_CRMS, MAX_REQUESTS_PER_MINUTE

router = APIRouter()
logger = logging.getLogger(__name__)

class CRMException(Exception):
    def __init__(self, crm_name: str, message: str):
        self.crm_name = crm_name
        self.message = message
        super().__init__(self.message)

@router.post("/send-to-crm/{crm_name}")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def send_to_crm(
    crm_name: str, 
    lead: Lead, 
    credentials: OAuthCredentials = Depends(get_oauth_credentials)
) -> JSONResponse:
    if crm_name not in SUPPORTED_CRMS:
        raise HTTPException(status_code=400, detail=f"Unsupported CRM: {crm_name}")
    
    try:
        result = await send_lead_to_crm(crm_name, lead, credentials)
        logger.info(f"Lead successfully sent to {crm_name} CRM")
        return JSONResponse(content={"message": f"Lead sent to {crm_name} CRM", "result": result}, status_code=200)
    except CRMException as ce:
        logger.error(f"CRM-specific error for {ce.crm_name}: {ce.message}")
        raise HTTPException(status_code=400, detail=str(ce))
    except Exception as e:
        logger.error(f"Error sending lead to {crm_name} CRM: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending lead to CRM: {str(e)}")

@router.get("/oauth/{crm_name}/initiate")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def oauth_initiate(crm_name: str) -> JSONResponse:
    if crm_name not in SUPPORTED_CRMS:
        raise HTTPException(status_code=400, detail=f"Unsupported CRM: {crm_name}")
    
    try:
        auth_url = await initiate_oauth(crm_name)
        logger.info(f"OAuth initiation successful for {crm_name}")
        return JSONResponse(content={"authUrl": auth_url}, status_code=200)
    except Exception as e:
        logger.error(f"Error initiating OAuth for {crm_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initiating OAuth: {str(e)}")

@router.get("/oauth/{crm_name}/callback")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
@cache(expire=3600)  # Cache for 1 hour
async def oauth_callback(
    crm_name: str, 
    code: str = Query(..., description="The authorization code returned by the OAuth provider")
) -> JSONResponse:
    if crm_name not in SUPPORTED_CRMS:
        raise HTTPException(status_code=400, detail=f"Unsupported CRM: {crm_name}")
    
    try:
        credentials = await exchange_code_for_token(crm_name, code)
        logger.info(f"Successfully exchanged code for token for {crm_name}")
        return JSONResponse(content={"access_token": credentials.access_token}, status_code=200)
    except Exception as e:
        logger.error(f"Error exchanging code for token for {crm_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error exchanging code for token: {str(e)}")