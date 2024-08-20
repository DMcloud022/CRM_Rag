import aiohttp
import logging
from typing import Dict, Any
from backend.models.lead import Lead
from backend.models.oauth import OAuthCredentials
from backend.config import DYNAMICS_CLIENT_ID, DYNAMICS_CLIENT_SECRET, DYNAMICS_REDIRECT_URI, DYNAMICS_TENANT_ID
import time

logger = logging.getLogger(__name__)

DYNAMICS_API_URL = "https://your-org.api.crm.dynamics.com/api/data/v9.2/leads"
DYNAMICS_AUTH_URL = f"https://login.microsoftonline.com/{DYNAMICS_TENANT_ID}/oauth2/v2.0/authorize"
DYNAMICS_TOKEN_URL = f"https://login.microsoftonline.com/{DYNAMICS_TENANT_ID}/oauth2/v2.0/token"

async def send_to_dynamics(lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json",
    }
    
    data = {
        "firstname": lead.name.split()[0] if lead.name else "",
        "lastname": lead.name.split()[-1] if lead.name else "",
        "emailaddress1": lead.email,
        "telephone1": lead.phone,
        "companyname": lead.company,
        "jobtitle": lead.position,
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(DYNAMICS_API_URL, headers=headers, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    logger.info(f"Successfully sent lead to Dynamics CRM: {result}")
                    return result
                else:
                    error_msg = await response.text()
                    logger.error(f"Failed to send lead to Dynamics CRM. Status: {response.status}, Error: {error_msg}")
                    raise ValueError(f"Dynamics CRM API error: {error_msg}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error while sending lead to Dynamics CRM: {str(e)}")
            raise ConnectionError(f"Network error: {str(e)}")

async def initiate_dynamics_oauth() -> str:
    params = {
        "client_id": DYNAMICS_CLIENT_ID,
        "redirect_uri": DYNAMICS_REDIRECT_URI,
        "response_type": "code",
        "scope": "https://your-org.crm.dynamics.com/.default",
    }
    auth_url = f"{DYNAMICS_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    logger.info(f"Initiated Dynamics OAuth. Auth URL: {auth_url}")
    return auth_url

async def exchange_dynamics_code_for_token(code: str) -> OAuthCredentials:
    data = {
        "grant_type": "authorization_code",
        "client_id": DYNAMICS_CLIENT_ID,
        "client_secret": DYNAMICS_CLIENT_SECRET,
        "redirect_uri": DYNAMICS_REDIRECT_URI,
        "code": code,
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(DYNAMICS_TOKEN_URL, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    logger.info("Successfully exchanged code for Dynamics OAuth token")
                    return OAuthCredentials(
                        access_token=token_data["access_token"],
                        refresh_token=token_data.get("refresh_token"),
                        expires_at=int(token_data.get("expires_in", 3600)) + int(time.time())
                    )
                else:
                    error_msg = await response.text()
                    logger.error(f"Failed to exchange code for Dynamics OAuth token. Status: {response.status}, Error: {error_msg}")
                    raise ValueError(f"Dynamics OAuth error: {error_msg}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error while exchanging code for Dynamics OAuth token: {str(e)}")
            raise ConnectionError(f"Network error: {str(e)}")