import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from services.crm_integration import send_lead_to_crm, initiate_oauth, exchange_code_for_token
from models.lead import Lead
from models.oauth import OAuthCredentials
from utils.oauth import get_oauth_credentials
from utils.rate_limiter import rate_limit
from config import SUPPORTED_CRMS, MAX_REQUESTS_PER_MINUTE

router = APIRouter()
logger = logging.getLogger(__name__)

def validate_crm(crm_name: str):
    """Validate if the provided CRM name is supported."""
    if crm_name not in SUPPORTED_CRMS:
        raise HTTPException(status_code=400, detail=f"Unsupported CRM: {crm_name}")

@router.post("/send-to-crm/{crm_name}")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def send_to_crm(
    crm_name: str, 
    lead: Lead, 
    credentials: OAuthCredentials = Depends(get_oauth_credentials)
) -> JSONResponse:
    validate_crm(crm_name)

    try:
        result = await send_lead_to_crm(crm_name, lead, credentials)
        logger.info(f"Lead successfully sent to {crm_name} CRM")
        return JSONResponse(content={"message": f"Lead sent to {crm_name} CRM", "result": result}, status_code=200)
    except (ValueError, ConnectionError) as e:
        logger.error(f"Error sending lead to {crm_name} CRM: {str(e)}")
        raise HTTPException(status_code=400 if isinstance(e, ValueError) else 503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error sending lead to {crm_name} CRM: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/oauth/{crm_name}/initiate")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def oauth_initiate(crm_name: str, request: Request) -> RedirectResponse:
    validate_crm(crm_name)

    try:
        auth_url = await initiate_oauth(crm_name)
        logger.info(f"OAuth initiation successful for {crm_name}. Redirecting to: {auth_url}")
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Error initiating OAuth for {crm_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initiating OAuth: {str(e)}")

@router.get("/oauth/{crm_name}/callback")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def oauth_callback(
    crm_name: str,
    code: str = Query(None, description="The authorization code returned by the OAuth provider"),
    error: str = Query(None, description="Error message if OAuth failed"),
    error_description: str = Query(None, description="Detailed error description")
) -> JSONResponse:
    if error:
        logger.error(f"OAuth error for {crm_name}: {error}. Description: {error_description}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}. {error_description}")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")

    validate_crm(crm_name)

    try:
        credentials = await exchange_code_for_token(crm_name, code)
        logger.info(f"Successfully exchanged code for token for {crm_name}")
        return JSONResponse(content={"message": "OAuth successful", "access_token": credentials.access_token})
    except (ValueError, ConnectionError) as e:
        logger.error(f"Error during OAuth for {crm_name}: {str(e)}")
        raise HTTPException(status_code=400 if isinstance(e, ValueError) else 503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error exchanging code for token for {crm_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")