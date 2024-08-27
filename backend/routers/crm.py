import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body, Header
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from backend.services.crm_integration import send_lead_to_crm, initiate_oauth, exchange_code_for_token
from backend.services.crm_integration.zoho import send_to_zoho
from backend.models.lead import Lead
from backend.models.oauth import OAuthCredentials
from backend.utils.oauth import get_oauth_credentials, store_oauth_credentials, refresh_hubspot_token
from backend.utils.rate_limiter import rate_limit
from backend.config import SUPPORTED_CRMS, MAX_REQUESTS_PER_MINUTE, HUBSPOT_CLIENT_ID, HUBSPOT_CLIENT_SECRET, HUBSPOT_REDIRECT_URI
from starlette.background import BackgroundTask
import httpx
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any
from urllib.parse import urlencode

router = APIRouter()
logger = logging.getLogger(__name__)

# async def get_valid_access_token(crm_name: str) -> str:
#     credentials = await get_oauth_credentials(crm_name)
#     if credentials.is_expired():
#         new_credentials = await refresh_hubspot_token(credentials.refresh_token)
#         await store_oauth_credentials(crm_name, new_credentials)
#         return new_credentials.access_token
#     return credentials.access_token


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

# @router.get("/oauth/{crm_name}/initiate")
# @rate_limit(MAX_REQUESTS_PER_MINUTE)
# async def oauth_initiate(crm_name: str, request: Request) -> RedirectResponse:
#     validate_crm(crm_name)

#     try:
#         auth_url = await initiate_oauth(crm_name)
#         logger.info(f"OAuth initiation successful for {crm_name}. Redirecting to: {auth_url}")

#         # Create a background task to automatically handle the callback
#         background_task = BackgroundTask(handle_oauth_callback, crm_name=crm_name, auth_url=auth_url)

#         return RedirectResponse(url=auth_url, background=background_task)
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


@router.get("/oauth/{crm_name}/callback")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def oauth_callback(
    crm_name: str,
    code: str = Query(
        None, description="The authorization code returned by the OAuth provider"),
    error: str = Query(None, description="Error message if OAuth failed"),
    error_description: str = Query(
        None, description="Detailed error description")
) -> JSONResponse:
    if error:
        logger.error(
            f"OAuth error for {crm_name}: {error}. Description: {error_description}")
        raise HTTPException(
            status_code=400, detail=f"OAuth error: {error}. {error_description}")

    if not code:
        raise HTTPException(
            status_code=400, detail="Authorization code is missing")

    validate_crm(crm_name)

    try:
        credentials = await exchange_code_for_token(crm_name, code)
        logger.info(f"Successfully exchanged code for token for {crm_name}")
        return JSONResponse(content={"message": "OAuth successful", "access_token": credentials.access_token})
    except (ValueError, ConnectionError) as e:
        logger.error(f"Error during OAuth for {crm_name}: {str(e)}")
        raise HTTPException(status_code=400 if isinstance(
            e, ValueError) else 503, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error exchanging code for token for {crm_name}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}")

HUBSPOT_API_BASE_URL = "https://api.hubapi.com"

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


async def get_valid_access_token() -> str:
    try:
        credentials = await get_oauth_credentials("hubspot")
        if credentials.is_expired():
            new_credentials = await refresh_hubspot_token(credentials.refresh_token)
            await store_oauth_credentials("hubspot", new_credentials)
            return new_credentials.access_token
        return credentials.access_token
    except Exception as e:
        logger.error(f"Error getting valid access token: {str(e)}")
        raise HTTPException(
            status_code=401, detail="Unable to authenticate with HubSpot")


async def create_lead_in_hubspot(lead: Lead, access_token: str) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/contacts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "properties": {
            "firstname": lead.name.split()[0] if lead.name else "",
            "lastname": lead.name.split()[-1] if lead.name and len(lead.name.split()) > 1 else "",
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "jobtitle": lead.position
        }
    }

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
async def create_hubspot_lead(lead: Lead):
    try:
        access_token = await get_valid_access_token()
        result = await create_lead_in_hubspot(lead, access_token)
        return JSONResponse(content={
            "message": "Lead created successfully in HubSpot",
            "result": result
        })
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Unexpected error creating lead in HubSpot: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Unexpected error creating lead: {str(e)}")


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

# @router.get("/oauth/{crm_name}/initiate")
# @rate_limit(MAX_REQUESTS_PER_MINUTE)
# async def oauth_initiate(crm_name: str):
#     validate_crm(crm_name)

#     try:
#         auth_url = await initiate_oauth(crm_name)
#         logger.info(f"OAuth initiation successful for {crm_name}. Redirecting to: {auth_url}")
#         return RedirectResponse(url=auth_url)
#     except Exception as e:
#         logger.error(f"Error initiating OAuth for {crm_name}: {str(e)}")
#         raise HTTPException(
#             status_code=500, detail=f"Error initiating OAuth: {str(e)}"
#         )


# @router.get("/auth-callback")
# async def auth_callback(code: str = Query(...)):
#     try:
#         token_url = "https://api.hubapi.com/oauth/v1/token"
#         data = {
#             "grant_type": "authorization_code",
#             "client_id": HUBSPOT_CLIENT_ID,
#             "client_secret": HUBSPOT_CLIENT_SECRET,
#             "redirect_uri": HUBSPOT_REDIRECT_URI,
#             "code": code,
#         }

#         async with aiohttp.ClientSession() as session:
#             async with session.post(token_url, data=data) as response:
#                 if response.status == 200:
#                     token_data = await response.json()
#                     access_token = token_data["access_token"]
#                     refresh_token = token_data.get("refresh_token")
#                     expires_in = token_data.get("expires_in", 3600)

#                     expires_at = int(
#                         (datetime.utcnow() + timedelta(seconds=expires_in)).timestamp()
#                     )

#                     await store_oauth_credentials("hubspot", OAuthCredentials(
#                         access_token=access_token,
#                         refresh_token=refresh_token,
#                         expires_at=expires_at
#                     ))

#                     redirect_params = urlencode({
#                         'access_token': access_token,
#                         'token_type': token_data.get('token_type', 'bearer'),
#                         'expires_in': expires_in
#                     })
#                     redirect_url = f"exp://192.168.68.103:8081/oauth-callback?{redirect_params}"
#                     return RedirectResponse(url=redirect_url)
#                 else:
#                     error_detail = await response.text()
#                     logger.error(f"Error exchanging code for token: {error_detail}")
#                     error_params = urlencode({
#                         'error': 'Error exchanging code for token'
#                     })
#                     error_redirect_url = f"exp://192.168.68.103:8081/oauth-callback?{error_params}"
#                     return RedirectResponse(url=error_redirect_url)
#     except Exception as e:
#         logger.error(f"Error in auth callback: {str(e)}")
#         error_params = urlencode({
#             'error': 'Unexpected error during authentication'
#         })
#         error_redirect_url = f"exp://192.168.68.103:8081/oauth-callback?{error_params}"
#         return RedirectResponse(url=error_redirect_url)

@router.get("/oauth/{crm_name}/initiate")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def oauth_initiate(crm_name: str, request: Request):
    validate_crm(crm_name)

    try:
        auth_url = await initiate_oauth(crm_name)
        logger.info(f"OAuth initiation successful for {crm_name}. Redirecting to: {auth_url}")
        
        # Extract any additional parameters from the request
        params = dict(request.query_params)
        
        # Add these parameters to the auth_url
        if params:
            auth_url += f"&{urlencode(params)}"
        
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"Error initiating OAuth for {crm_name}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error initiating OAuth: {str(e)}"
        )

@router.get("/auth-callback")
async def auth_callback(code: str = Query(...), crm_name: str = Query(...)):
    try:
        token_url = "https://api.hubapi.com/oauth/v1/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": HUBSPOT_CLIENT_ID,
            "client_secret": HUBSPOT_CLIENT_SECRET,
            "redirect_uri": HUBSPOT_REDIRECT_URI,
            "code": code,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    access_token = token_data["access_token"]
                    refresh_token = token_data.get("refresh_token")
                    expires_in = token_data.get("expires_in", 3600)

                    expires_at = int(
                        (datetime.utcnow() + timedelta(seconds=expires_in)).timestamp()
                    )

                    await store_oauth_credentials(crm_name, OAuthCredentials(
                        access_token=access_token,
                        refresh_token=refresh_token,
                        expires_at=expires_at
                    ))

                    redirect_params = urlencode({
                        'code': code,
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'expires_in': expires_in
                    })
                    
                    # HTML response that will close the web view and redirect to the mobile app
                    html_content = f"""
                    <html>
                        <head>
                            <script>
                                window.onload = function() {{
                                    window.location.href = "http://crm-rag.onrender.com/oauth/{crm_name}/initiate?{redirect_params}";
                                    window.close();
                                }}
                            </script>
                        </head>
                        <body>
                            <p>Authentication successful. This window will close automatically.</p>
                        </body>
                    </html>
                    """
                    return HTMLResponse(content=html_content, status_code=200)
                else:
                    error_detail = await response.text()
                    logger.error(f"Error exchanging code for token: {error_detail}")
                    error_params = urlencode({
                        'error': 'Error exchanging code for token'
                    })
                    html_content = f"""
                    <html>
                        <head>
                            <script>
                                window.onload = function() {{
                                    window.location.href = "http://crm-rag.onrender.com/oauth/{crm_name}/initiate?{error_params}";
                                    window.close();
                                }}
                            </script>
                        </head>
                        <body>
                            <p>Authentication failed. This window will close automatically.</p>
                        </body>
                    </html>
                    """
                    return HTMLResponse(content=html_content, status_code=400)
    except Exception as e:
        logger.error(f"Error in auth callback: {str(e)}")
        error_params = urlencode({
            'error': 'Unexpected error during authentication'
        })
        html_content = f"""
        <html>
            <head>
                <script>
                    window.onload = function() {{
                        window.location.href = "http://crm-rag.onrender.com/oauth/{crm_name}/initiate?{error_params}";
                        window.close();
                    }}
                </script>
            </head>
            <body>
                <p>An unexpected error occurred. This window will close automatically.</p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=500)

@router.post("/oauth/{crm_name}/exchange-token")
@rate_limit(MAX_REQUESTS_PER_MINUTE)
async def exchange_token(
    crm_name: str,
    code: str = Body(..., embed=True),
    user_id: str = Body(..., embed=True)
):
    validate_crm(crm_name)

    try:
        credentials = await exchange_code_for_token(crm_name, code)
        await store_oauth_credentials(user_id, crm_name, credentials)

        logger.info(f"Successfully exchanged code for token for {crm_name}")
        return JSONResponse(content={
            "message": "OAuth successful",
            "access_token": credentials.access_token
        })
    except Exception as e:
        logger.error(f"Error exchanging code for token for {crm_name}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error exchanging code for token: {str(e)}"
        )

