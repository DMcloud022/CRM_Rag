from fastapi import APIRouter, Depends, HTTPException, Query
from services.crm_integration import send_lead_to_crm, initiate_oauth, exchange_code_for_token
from models.lead import Lead
from models.oauth import OAuthCredentials
from utils.oauth import get_oauth_credentials
from typing import Dict, Any

router = APIRouter()

@router.post("/send-to-crm/{crm_name}")
async def send_to_crm(
    crm_name: str, 
    lead: Lead, 
    credentials: OAuthCredentials = Depends(get_oauth_credentials)
) -> Dict[str, Any]:
    try:
        result = await send_lead_to_crm(crm_name, lead, credentials)
        return {"message": f"Lead sent to {crm_name} CRM", "result": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending lead to CRM: {str(e)}")

@router.get("/oauth/{crm_name}/initiate")
async def oauth_initiate(crm_name: str) -> Dict[str, str]:
    try:
        auth_url = await initiate_oauth(crm_name)
        return {"authUrl": auth_url}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating OAuth: {str(e)}")

@router.get("/oauth/{crm_name}/callback")
async def oauth_callback(
    crm_name: str, 
    code: str = Query(..., description="The authorization code returned by the OAuth provider")
) -> Dict[str, str]:
    try:
        credentials = await exchange_code_for_token(crm_name, code)
        return {"access_token": credentials.access_token}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exchanging code for token: {str(e)}")