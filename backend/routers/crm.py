import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
from fastapi.responses import JSONResponse, RedirectResponse
from services.crm_integration import send_lead_to_crm, initiate_oauth, exchange_code_for_token
from services.crm_integration.zoho import send_to_zoho
from models.lead import Lead, Company, Note, CustomObject
from models.oauth import OAuthCredentials
from utils.oauth import get_oauth_credentials, store_oauth_credentials
from utils.rate_limiter import rate_limit
from config import SUPPORTED_CRMS, MAX_REQUESTS_PER_MINUTE
from starlette.background import BackgroundTask
import httpx
import aiohttp

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
        
        # Create a background task to automatically handle the callback
        background_task = BackgroundTask(handle_oauth_callback, crm_name=crm_name, auth_url=auth_url)
        
        return RedirectResponse(url=auth_url, background=background_task)
    except Exception as e:
        logger.error(f"Error initiating OAuth for {crm_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error initiating OAuth: {str(e)}")

async def handle_oauth_callback(crm_name: str, auth_url: str):
    try:
        async with httpx.AsyncClient() as client:
            # Simulate a user following the auth_url and granting permission
            response = await client.get(auth_url, follow_redirects=True)
            
            # Extract the code from the final URL
            final_url = str(response.url)
            code = final_url.split('code=')[1].split('&')[0] if 'code=' in final_url else None

            if not code:
                logger.error(f"Failed to obtain authorization code for {crm_name}")
                return

            # Exchange the code for a token
            credentials = await exchange_code_for_token(crm_name, code)
            
            # Store the credentials
            await store_oauth_credentials(crm_name, credentials)
            
            logger.info(f"Successfully completed OAuth flow for {crm_name}")
    except Exception as e:
        logger.error(f"Error in automatic OAuth callback handling for {crm_name}: {str(e)}")


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
    
HUBSPOT_API_BASE_URL = "https://api.hubapi.com"

async def create_lead_in_hubspot(lead: Lead, access_token: str) -> dict:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    properties = {
        "firstname": lead.name.split()[0] if lead.name else "",
        "lastname": lead.name.split()[-1] if lead.name and len(lead.name.split()) > 1 else "",
        "email": lead.email,
        "phone": lead.phone,
        "company": lead.company,
        "jobtitle": lead.position,
    }
    data = {"properties": properties}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 201:
                return await response.json()
            else:
                error_detail = await response.text()
                logger.error(f"HubSpot API error: {response.status} - {error_detail}")
                raise HTTPException(status_code=response.status, detail=f"HubSpot API error: {error_detail}")

@router.post("/create-hubspot-lead")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def create_hubspot_lead(
    lead: Lead = Body(..., description="The lead to send to HubSpot"),
    access_token: str = Query(..., description="OAuth access token for HubSpot authentication")
):
    try:
        if not lead.email:
            raise ValueError("Email is required for the lead")

        logger.info(f"Attempting to create lead in HubSpot: {lead.email}")
        result = await create_lead_in_hubspot(lead, access_token)
        
        logger.info(f"Successfully created lead in HubSpot: {result.get('id', 'N/A')}")
        return JSONResponse(
            content={
                "message": "Successfully created lead in HubSpot",
                "hubspot_response": result,
                "lead_details": lead.dict()
            },
            status_code=201
        )

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error creating lead in HubSpot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    
@router.post("/create-zoho-lead")
async def create_zoho_lead(
    lead: Lead = Body(..., description="The lead to send to Zoho CRM"),
    access_token: str = Query(..., description="OAuth access token for Zoho CRM authentication")
):
    try:
        if not lead.email:
            raise ValueError("Email is required for the lead")

        logger.info(f"Attempting to create lead in Zoho CRM: {lead.email}")
        
        credentials = OAuthCredentials(access_token=access_token)
        result = await send_to_zoho(lead, credentials)
        
        logger.info(f"Successfully created lead in Zoho CRM: {result}")
        return {
            "message": "Successfully created lead in Zoho CRM",
            "zoho_response": result,
            "lead_details": lead.dict()
        }

    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error creating lead in Zoho CRM: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    

@router.post("/create-hubspot-company")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def create_hubspot_company(
    company: Company = Body(..., description="The company to create in HubSpot"),
    access_token: str = Query(..., description="OAuth access token for HubSpot authentication")
):
    try:
        logger.info(f"Attempting to create company in HubSpot: {company.name}")
        result = await create_company_in_hubspot(company, access_token)
        
        logger.info(f"Successfully created company in HubSpot: {result.get('id', 'N/A')}")
        return JSONResponse(
            content={
                "message": "Successfully created company in HubSpot",
                "hubspot_response": result,
                "company_details": company.dict()
            },
            status_code=201
        )
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error creating company in HubSpot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/create-hubspot-note")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def create_hubspot_note(
    note: Note = Body(..., description="The note to create in HubSpot"),
    access_token: str = Query(..., description="OAuth access token for HubSpot authentication")
):
    try:
        logger.info(f"Attempting to create note in HubSpot")
        result = await create_note_in_hubspot(note, access_token)
        
        logger.info(f"Successfully created note in HubSpot: {result.get('id', 'N/A')}")
        return JSONResponse(
            content={
                "message": "Successfully created note in HubSpot",
                "hubspot_response": result,
                "note_details": note.dict()
            },
            status_code=201
        )
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error creating note in HubSpot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/create-hubspot-custom-object")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def create_hubspot_custom_object(
    custom_object: CustomObject = Body(..., description="The custom object to create in HubSpot"),
    object_type: str = Query(..., description="The type of custom object to create"),
    access_token: str = Query(..., description="OAuth access token for HubSpot authentication")
):
    try:
        logger.info(f"Attempting to create custom object in HubSpot: {object_type}")
        result = await create_custom_object_in_hubspot(custom_object, object_type, access_token)
        
        logger.info(f"Successfully created custom object in HubSpot: {result.get('id', 'N/A')}")
        return JSONResponse(
            content={
                "message": f"Successfully created custom object '{object_type}' in HubSpot",
                "hubspot_response": result,
                "custom_object_details": custom_object.dict()
            },
            status_code=201
        )
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error creating custom object in HubSpot: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Helper functions for creating objects in HubSpot

async def create_company_in_hubspot(company: Company, access_token: str) -> dict:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/companies"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    properties = {
        "name": company.name,
        "domain": company.domain,
        "industry": company.industry,
        # Add more properties as needed
    }
    data = {"properties": properties}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 201:
                return await response.json()
            else:
                error_detail = await response.text()
                logger.error(f"HubSpot API error: {response.status} - {error_detail}")
                raise HTTPException(status_code=response.status, detail=f"HubSpot API error: {error_detail}")

async def create_note_in_hubspot(note: Note, access_token: str) -> dict:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/notes"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    properties = {
        "hs_note_body": note.content,
        "hs_timestamp": note.timestamp.isoformat(),
        # Add more properties as needed
    }
    data = {
        "properties": properties,
        "associations": [
            {
                "to": {"id": note.associated_object_id},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": note.association_type}]
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 201:
                return await response.json()
            else:
                error_detail = await response.text()
                logger.error(f"HubSpot API error: {response.status} - {error_detail}")
                raise HTTPException(status_code=response.status, detail=f"HubSpot API error: {error_detail}")

async def create_custom_object_in_hubspot(custom_object: CustomObject, object_type: str, access_token: str) -> dict:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/{object_type}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = {"properties": custom_object.properties}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 201:
                return await response.json()
            else:
                error_detail = await response.text()
                logger.error(f"HubSpot API error: {response.status} - {error_detail}")
                raise HTTPException(status_code=response.status, detail=f"HubSpot API error: {error_detail}")