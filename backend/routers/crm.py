# import logging
# from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
# from fastapi.responses import JSONResponse, RedirectResponse
# from services.crm_integration import send_lead_to_crm, initiate_oauth, exchange_code_for_token
# from services.crm_integration.zoho import send_to_zoho
# from models.lead import Lead
# from models.oauth import OAuthCredentials
# from utils.oauth import get_oauth_credentials, store_oauth_credentials, create_user_token
# from utils.rate_limiter import rate_limit
# from config import SUPPORTED_CRMS, MAX_REQUESTS_PER_MINUTE
# from starlette.background import BackgroundTask
# import httpx
# import aiohttp
# from services.crm_integration.hubspot import create_company, create_custom_object, create_note

# router = APIRouter()
# logger = logging.getLogger(__name__)

# def validate_crm(crm_name: str):
#     """Validate if the provided CRM name is supported."""
#     if crm_name not in SUPPORTED_CRMS:
#         raise HTTPException(status_code=400, detail=f"Unsupported CRM: {crm_name}")

# @router.post("/send-to-crm/{crm_name}")
# @rate_limit(MAX_REQUESTS_PER_MINUTE)
# async def send_to_crm(
#     crm_name: str,
#     lead: Lead,
#     credentials: OAuthCredentials = Depends(get_oauth_credentials)
# ) -> JSONResponse:
#     validate_crm(crm_name)

#     try:
#         result = await send_lead_to_crm(crm_name, lead, credentials)
#         logger.info(f"Lead successfully sent to {crm_name} CRM")
#         return JSONResponse(content={"message": f"Lead sent to {crm_name} CRM", "result": result}, status_code=200)
#     except (ValueError, ConnectionError) as e:
#         logger.error(f"Error sending lead to {crm_name} CRM: {str(e)}")
#         raise HTTPException(status_code=400 if isinstance(e, ValueError) else 503, detail=str(e))
#     except Exception as e:
#         logger.error(f"Unexpected error sending lead to {crm_name} CRM: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# @router.get("/oauth/{crm_name}/initiate")
# @rate_limit(MAX_REQUESTS_PER_MINUTE)
# async def oauth_initiate(crm_name: str, request: Request):
#     validate_crm(crm_name)

#     try:
#         auth_url = await initiate_oauth(crm_name)
#         logger.info(f"OAuth initiation successful for {crm_name}. Redirecting to: {auth_url}")
#         return RedirectResponse(url=auth_url)
#     except Exception as e:
#         logger.error(f"Error initiating OAuth for {crm_name}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error initiating OAuth: {str(e)}")

# async def handle_oauth_callback(crm_name: str, auth_url: str):
#     try:
#         async with httpx.AsyncClient() as client:
#             # Simulate a user following the auth_url and granting permission
#             response = await client.get(auth_url, follow_redirects=True)

#             # Extract the code from the final URL
#             final_url = str(response.url)
#             code = final_url.split('code=')[1].split('&')[0] if 'code=' in final_url else None

#             if not code:
#                 logger.error(f"Failed to obtain authorization code for {crm_name}")
#                 return

#             # Exchange the code for a token
#             credentials = await exchange_code_for_token(crm_name, code)

#             # Store the credentials
#             await store_oauth_credentials(crm_name, credentials)

#             logger.info(f"Successfully completed OAuth flow for {crm_name}")
#     except Exception as e:
#         logger.error(f"Error in automatic OAuth callback handling for {crm_name}: {str(e)}")


# @router.get("/oauth/{crm_name}/callback")
# @rate_limit(MAX_REQUESTS_PER_MINUTE)
# async def oauth_callback(
#     crm_name: str,
#     code: str = Query(..., description="The authorization code returned by the OAuth provider"),
#     error: str = Query(None, description="Error message if OAuth failed"),
#     error_description: str = Query(None, description="Detailed error description")
# ):
#     if error:
#         logger.error(f"OAuth error for {crm_name}: {error}. Description: {error_description}")
#         raise HTTPException(status_code=400, detail=f"OAuth error: {error}. {error_description}")

#     validate_crm(crm_name)

#     try:
#         # Exchange the code for a token
#         credentials = await exchange_code_for_token(crm_name, code)

#         logger.info(f"Successfully completed OAuth flow for {crm_name}")

#         # Redirect to the frontend with the access token
#         redirect_url = f"{FRONTEND_CALLBACK_URL}?access_token={credentials.access_token}&refresh_token={credentials.refresh_token}&expires_at={credentials.expires_at}"
#         return RedirectResponse(url=redirect_url)
#     except Exception as e:
#         logger.error(f"Error in OAuth callback for {crm_name}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error in OAuth callback: {str(e)}")

# HUBSPOT_API_BASE_URL = "https://api.hubapi.com"

# async def create_lead_in_hubspot(lead: Lead, access_token: str) -> dict:
#     url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/contacts"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/json",
#     }
#     properties = {
#         "firstname": lead.name.split()[0] if lead.name else "",
#         "lastname": lead.name.split()[-1] if lead.name and len(lead.name.split()) > 1 else "",
#         "email": lead.email,
#         "phone": lead.phone,
#         "company": lead.company,
#         "jobtitle": lead.position,
#     }
#     data = {"properties": properties}

#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, headers=headers, json=data) as response:
#             if response.status == 201:
#                 return await response.json()
#             else:
#                 error_detail = await response.text()
#                 logger.error(f"HubSpot API error: {response.status} - {error_detail}")
#                 raise HTTPException(status_code=response.status, detail=f"HubSpot API error: {error_detail}")

# @router.post("/create-hubspot-lead")
# @rate_limit(MAX_REQUESTS_PER_MINUTE)
# async def create_hubspot_lead(
#     lead: Lead = Body(..., description="The lead to send to HubSpot"),
#     access_token: str = Query(..., description="OAuth access token for HubSpot authentication")
# ):
#     try:
#         if not lead.email:
#             raise ValueError("Email is required for the lead")

#         logger.info(f"Attempting to create lead in HubSpot: {lead.email}")
#         result = await create_lead_in_hubspot(lead, access_token)

#         logger.info(f"Successfully created lead in HubSpot: {result.get('id', 'N/A')}")
#         return JSONResponse(
#             content={
#                 "message": "Successfully created lead in HubSpot",
#                 "hubspot_response": result,
#                 "lead_details": lead.dict()
#             },
#             status_code=201
#         )

#     except ValueError as ve:
#         logger.error(f"Validation error: {str(ve)}")
#         raise HTTPException(status_code=400, detail=str(ve))
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         logger.error(f"Unexpected error creating lead in HubSpot: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# @router.post("/create-zoho-lead")
# async def create_zoho_lead(
#     lead: Lead = Body(..., description="The lead to send to Zoho CRM"),
#     access_token: str = Query(..., description="OAuth access token for Zoho CRM authentication")
# ):
#     try:
#         if not lead.email:
#             raise ValueError("Email is required for the lead")

#         logger.info(f"Attempting to create lead in Zoho CRM: {lead.email}")

#         credentials = OAuthCredentials(access_token=access_token)
#         result = await send_to_zoho(lead, credentials)

#         logger.info(f"Successfully created lead in Zoho CRM: {result}")
#         return {
#             "message": "Successfully created lead in Zoho CRM",
#             "zoho_response": result,
#             "lead_details": lead.dict()
#         }

#     except ValueError as ve:
#         logger.error(f"Validation error: {str(ve)}")
#         raise HTTPException(status_code=400, detail=str(ve))
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         logger.error(f"Unexpected error creating lead in Zoho CRM: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# @router.post("/hubspot/companies")
# @rate_limit(MAX_REQUESTS_PER_MINUTE)
# async def create_hubspot_company(
#     company: dict = Body(..., description="The company data to send to HubSpot"),
#     credentials: OAuthCredentials = Depends(get_oauth_credentials)
# ):
#     try:
#         result = await create_company(company, credentials)
#         return JSONResponse(content=result, status_code=201)
#     except Exception as e:
#         logger.error(f"Error creating company in HubSpot: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/hubspot/notes")
# @rate_limit(MAX_REQUESTS_PER_MINUTE)
# async def create_hubspot_note(
#     note: dict = Body(..., description="The note data to send to HubSpot"),
#     credentials: OAuthCredentials = Depends(get_oauth_credentials)
# ):
#     try:
#         result = await create_note(note, credentials)
#         return JSONResponse(content=result, status_code=201)
#     except Exception as e:
#         logger.error(f"Error creating note in HubSpot: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/hubspot/custom/{object_type}")
# @rate_limit(MAX_REQUESTS_PER_MINUTE)
# async def create_hubspot_custom_object(
#     object_type: str,
#     custom_object: dict = Body(..., description="The custom object data to send to HubSpot"),
#     credentials: OAuthCredentials = Depends(get_oauth_credentials)
# ):
#     try:
#         result = await create_custom_object(object_type, custom_object, credentials)
#         return JSONResponse(content=result, status_code=201)
#     except Exception as e:
#         logger.error(f"Error creating custom object in HubSpot: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/oauth/{crm_name}")
# @rate_limit(MAX_REQUESTS_PER_MINUTE)
# async def oauth_flow(crm_name: str, request: Request):
#     validate_crm(crm_name)

#     try:
#         auth_url = await initiate_oauth(crm_name)

#         # Simulate user authorization and get the code
#         async with httpx.AsyncClient() as client:
#             response = await client.get(auth_url, follow_redirects=True)
#             final_url = str(response.url)
#             code = final_url.split('code=')[1].split('&')[0] if 'code=' in final_url else None

#         if not code:
#             raise HTTPException(status_code=400, detail="Failed to obtain authorization code")

#         # Exchange the code for a token
#         credentials = await exchange_code_for_token(crm_name, code)

#         # Store the credentials and create a user token
#         user_id = "example_user_id"  # Replace with actual user identification logic
#         await store_oauth_credentials(user_id, crm_name, credentials)
#         user_token = await create_user_token(user_id, crm_name)

#         return JSONResponse(content={
#             "message": "OAuth flow completed successfully",
#             "user_token": user_token
#         })
#     except Exception as e:
#         logger.error(f"Error in OAuth flow for {crm_name}: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error in OAuth flow: {str(e)}")

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
from fastapi.responses import JSONResponse, RedirectResponse
from services.crm_integration import send_lead_to_crm, initiate_oauth, exchange_code_for_token
from services.crm_integration.zoho import send_to_zoho
from models.lead import Lead
from models.oauth import OAuthCredentials
from utils.oauth import get_oauth_credentials, store_oauth_credentials, create_user_token
from utils.rate_limiter import rate_limit
from config import SUPPORTED_CRMS, MAX_REQUESTS_PER_MINUTE
from starlette.background import BackgroundTask
import httpx
import aiohttp
from services.crm_integration.hubspot import create_company, create_custom_object, create_note

router = APIRouter()
logger = logging.getLogger(__name__)


def validate_crm(crm_name: str):
    """Validate if the provided CRM name is supported."""
    if crm_name not in SUPPORTED_CRMS:
        raise HTTPException(
            status_code=400, detail=f"Unsupported CRM: {crm_name}")


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
        raise HTTPException(status_code=400 if isinstance(
            e, ValueError) else 503, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error sending lead to {crm_name} CRM: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/oauth/{crm_name}/initiate")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def oauth_initiate(crm_name: str, request: Request):
    validate_crm(crm_name)

    try:
        auth_url = await initiate_oauth(crm_name)
        logger.info(
            f"OAuth initiation successful for {crm_name}. Redirecting to: {auth_url}")
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Error initiating OAuth for {crm_name}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error initiating OAuth: {str(e)}")


async def handle_oauth_callback(crm_name: str, auth_url: str):
    try:
        async with httpx.AsyncClient() as client:
            # Simulate a user following the auth_url and granting permission
            response = await client.get(auth_url, follow_redirects=True)

            # Extract the code from the final URL
            final_url = str(response.url)
            code = final_url.split('code=')[1].split(
                '&')[0] if 'code=' in final_url else None

            if not code:
                logger.error(
                    f"Failed to obtain authorization code for {crm_name}")
                return

            # Exchange the code for a token
            credentials = await exchange_code_for_token(crm_name, code)

            # Store the credentials
            await store_oauth_credentials(crm_name, credentials)

            logger.info(f"Successfully completed OAuth flow for {crm_name}")
    except Exception as e:
        logger.error(
            f"Error in automatic OAuth callback handling for {crm_name}: {str(e)}")

FRONTEND_CALLBACK_URL = "https://192.168.1.13:8081/auth/callback"


@router.get("/oauth/{crm_name}/callback")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def oauth_callback(
    crm_name: str,
    code: str = Query(...,
                      description="The authorization code returned by the OAuth provider"),
    error: str = Query(None, description="Error message if OAuth failed"),
    error_description: str = Query(
        None, description="Detailed error description")
):
    if error:
        logger.error(
            f"OAuth error for {crm_name}: {error}. Description: {error_description}")
        raise HTTPException(
            status_code=400, detail=f"OAuth error: {error}. {error_description}")

    validate_crm(crm_name)

    try:
        # Exchange the code for a token
        credentials = await exchange_code_for_token(crm_name, code)

        logger.info(f"Successfully completed OAuth flow for {crm_name}")

        # Redirect to the frontend with the access token
        redirect_url = f"{FRONTEND_CALLBACK_URL}?access_token={credentials.access_token}&refresh_token={credentials.refresh_token}&expires_at={credentials.expires_at}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Error in OAuth callback for {crm_name}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error in OAuth callback: {str(e)}")

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
                logger.error(
                    f"HubSpot API error: {response.status} - {error_detail}")
                raise HTTPException(status_code=response.status,
                                    detail=f"HubSpot API error: {error_detail}")


@router.post("/create-hubspot-lead")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def create_hubspot_lead(
    lead: Lead = Body(..., description="The lead to send to HubSpot"),
    access_token: str = Query(...,
                              description="OAuth access token for HubSpot authentication")
):
    try:
        if not lead.email:
            raise ValueError("Email is required for the lead")

        logger.info(f"Attempting to create lead in HubSpot: {lead.email}")
        result = await create_lead_in_hubspot(lead, access_token)

        logger.info(
            f"Successfully created lead in HubSpot: {result.get('id', 'N/A')}")
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
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/create-zoho-lead")
async def create_zoho_lead(
    lead: Lead = Body(..., description="The lead to send to Zoho CRM"),
    access_token: str = Query(...,
                              description="OAuth access token for Zoho CRM authentication")
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
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/hubspot/companies")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def create_hubspot_company(
    company: dict = Body(...,
                         description="The company data to send to HubSpot"),
    credentials: OAuthCredentials = Depends(get_oauth_credentials)
):
    try:
        result = await create_company(company, credentials)
        return JSONResponse(content=result, status_code=201)
    except Exception as e:
        logger.error(f"Error creating company in HubSpot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hubspot/notes")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def create_hubspot_note(
    note: dict = Body(..., description="The note data to send to HubSpot"),
    credentials: OAuthCredentials = Depends(get_oauth_credentials)
):
    try:
        result = await create_note(note, credentials)
        return JSONResponse(content=result, status_code=201)
    except Exception as e:
        logger.error(f"Error creating note in HubSpot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hubspot/custom/{object_type}")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def create_hubspot_custom_object(
    object_type: str,
    custom_object: dict = Body(...,
                               description="The custom object data to send to HubSpot"),
    credentials: OAuthCredentials = Depends(get_oauth_credentials)
):
    try:
        result = await create_custom_object(object_type, custom_object, credentials)
        return JSONResponse(content=result, status_code=201)
    except Exception as e:
        logger.error(f"Error creating custom object in HubSpot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/oauth/{crm_name}")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def oauth_flow(crm_name: str, request: Request):
    validate_crm(crm_name)

    try:
        auth_url = await initiate_oauth(crm_name)

        # Simulate user authorization and get the code
        async with httpx.AsyncClient() as client:
            response = await client.get(auth_url, follow_redirects=True)
            final_url = str(response.url)
            code = final_url.split('code=')[1].split(
                '&')[0] if 'code=' in final_url else None

        if not code:
            raise HTTPException(
                status_code=400, detail="Failed to obtain authorization code")

        # Exchange the code for a token
        credentials = await exchange_code_for_token(crm_name, code)

        # Store the credentials and create a user token
        user_id = "example_user_id"  # Replace with actual user identification logic
        await store_oauth_credentials(user_id, crm_name, credentials)
        user_token = await create_user_token(user_id, crm_name)

        return JSONResponse(content={
            "message": "OAuth flow completed successfully",
            "user_token": user_token
        })
    except Exception as e:
        logger.error(f"Error in OAuth flow for {crm_name}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error in OAuth flow: {str(e)}")
