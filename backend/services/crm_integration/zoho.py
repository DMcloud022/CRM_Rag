import aiohttp
import logging
from typing import Dict, Any
from models.lead import Lead
from models.oauth import OAuthCredentials
from config import ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REDIRECT_URI


logger = logging.getLogger(__name__)

ZOHO_API_URL = "https://www.zohoapis.com/crm/v2/Leads"
ZOHO_AUTH_URL = "https://accounts.zoho.com/oauth/v2/auth"
ZOHO_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"

async def send_to_zoho(lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json",
    }
    
    data = {
        "data": [
            {
                "Last_Name": lead.name,
                "Email": lead.email,
                "Phone": lead.phone,
                "Company": lead.company,
                "Designation": lead.position,
            }
        ]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ZOHO_API_URL, headers=headers, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    logger.info(f"Successfully sent lead to Zoho CRM: {result}")
                    return result
                else:
                    error_msg = await response.text()
                    logger.error(f"Failed to send lead to Zoho CRM. Status: {response.status}, Error: {error_msg}")
                    raise f"Zoho CRM API error: {error_msg}"
    except aiohttp.ClientError as e:
        logger.error(f"Network error while sending lead to Zoho CRM: {str(e)}")
        raise f"Network error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error while sending lead to Zoho CRM: {str(e)}")
        raise f"Unexpected error: {str(e)}"

async def initiate_zoho_oauth() -> str:
    params = {
        "client_id": ZOHO_CLIENT_ID,
        "redirect_uri": ZOHO_REDIRECT_URI,
        "scope": "ZohoCRM.modules.ALL",
        "response_type": "code",
        "access_type": "offline",
    }
    auth_url = f"{ZOHO_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    logger.info(f"Initiated Zoho OAuth. Auth URL: {auth_url}")
    return auth_url

async def exchange_zoho_code_for_token(code: str) -> OAuthCredentials:
    data = {
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "redirect_uri": ZOHO_REDIRECT_URI,
        "code": code,
        "grant_type": "authorization_code",
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ZOHO_TOKEN_URL, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    logger.info("Successfully exchanged code for Zoho OAuth token")
                    return OAuthCredentials(
                        access_token=token_data["access_token"],
                        refresh_token=token_data.get("refresh_token"),
                        expires_in=token_data.get("expires_in")
                    )
                else:
                    error_msg = await response.text()
                    logger.error(f"Failed to exchange code for Zoho OAuth token. Status: {response.status}, Error: {error_msg}")
                    raise f"Zoho OAuth error: {error_msg}"
    except aiohttp.ClientError as e:
        logger.error(f"Network error while exchanging code for Zoho OAuth token: {str(e)}")
        raise f"Network error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error while exchanging code for Zoho OAuth token: {str(e)}")
        raise f"Unexpected error: {str(e)}"

async def refresh_zoho_token(refresh_token: str) -> OAuthCredentials:
    data = {
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ZOHO_TOKEN_URL, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    logger.info("Successfully refreshed Zoho OAuth token")
                    return OAuthCredentials(
                        access_token=token_data["access_token"],
                        refresh_token=refresh_token,  # Use the same refresh token
                        expires_in=token_data.get("expires_in")
                    )
                else:
                    error_msg = await response.text()
                    logger.error(f"Failed to refresh Zoho OAuth token. Status: {response.status}, Error: {error_msg}")
                    raise f"Zoho OAuth refresh error: {error_msg}"
    except aiohttp.ClientError as e:
        logger.error(f"Network error while refreshing Zoho OAuth token: {str(e)}")
        raise f"Network error: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error while refreshing Zoho OAuth token: {str(e)}")
        raise f"Unexpected error: {str(e)}"