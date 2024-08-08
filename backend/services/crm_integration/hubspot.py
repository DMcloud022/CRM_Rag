import aiohttp
import logging
from typing import Dict, Any
from models.lead import Lead
from models.oauth import OAuthCredentials
from config import HUBSPOT_CLIENT_ID, HUBSPOT_CLIENT_SECRET, HUBSPOT_REDIRECT_URI
import time

logger = logging.getLogger(__name__)

HUBSPOT_API_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
HUBSPOT_AUTH_URL = "https://app.hubspot.com/oauth/authorize"
HUBSPOT_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"

# List of required scopes
HUBSPOT_SCOPES = [
    "crm.objects.contacts.read",
    "crm.objects.contacts.write",
    "crm.schemas.contacts.read",
    "crm.schemas.contacts.write",
    "oauth",
]

async def send_to_hubspot(lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json",
    }
    
    data = {
        "properties": {
            "firstname": lead.name.split()[0] if lead.name else "",
            "lastname": lead.name.split()[-1] if lead.name else "",
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "jobtitle": lead.position,
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(HUBSPOT_API_URL, headers=headers, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    logger.info(f"Successfully sent lead to HubSpot CRM: {result}")
                    return result
                else:
                    error_msg = await response.text()
                    logger.error(f"Failed to send lead to HubSpot CRM. Status: {response.status}, Error: {error_msg}")
                    raise ValueError(f"HubSpot CRM API error: {error_msg}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error while sending lead to HubSpot CRM: {str(e)}")
            raise ConnectionError(f"Network error: {str(e)}")

async def initiate_hubspot_oauth() -> str:
    # Join the scopes into a single string
    scope_string = " ".join(HUBSPOT_SCOPES)
    params = {
        "client_id": HUBSPOT_CLIENT_ID,
        "redirect_uri": HUBSPOT_REDIRECT_URI,
        "scope": scope_string,
        "response_type": "code",
    }
    auth_url = f"{HUBSPOT_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    logger.info(f"Initiated HubSpot OAuth. Auth URL: {auth_url}")
    return auth_url

async def exchange_hubspot_code_for_token(code: str) -> OAuthCredentials:
    data = {
        "grant_type": "authorization_code",
        "client_id": HUBSPOT_CLIENT_ID,
        "client_secret": HUBSPOT_CLIENT_SECRET,
        "redirect_uri": HUBSPOT_REDIRECT_URI,
        "code": code,
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(HUBSPOT_TOKEN_URL, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    logger.info("Successfully exchanged code for HubSpot OAuth token")
                    return OAuthCredentials(
                        access_token=token_data["access_token"],
                        refresh_token=token_data.get("refresh_token"),
                        expires_at=int(token_data.get("expires_in", 3600)) + int(time.time())
                    )
                else:
                    error_msg = await response.text()
                    logger.error(f"Failed to exchange code for HubSpot OAuth token. Status: {response.status}, Error: {error_msg}")
                    raise ValueError(f"HubSpot OAuth error: {error_msg}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error while exchanging code for HubSpot OAuth token: {str(e)}")
            raise ConnectionError(f"Network error: {str(e)}")
