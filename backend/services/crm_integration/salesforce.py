import aiohttp
import logging
from typing import Dict, Any
from backend.models.lead import Lead
from backend.models.oauth import OAuthCredentials
from backend.config import SALESFORCE_CLIENT_ID, SALESFORCE_CLIENT_SECRET, SALESFORCE_REDIRECT_URI
import time

logger = logging.getLogger(__name__)

SALESFORCE_API_URL = "https://your-instance.salesforce.com/services/data/v52.0/sobjects/Lead"
SALESFORCE_AUTH_URL = "https://login.salesforce.com/services/oauth2/authorize"
SALESFORCE_TOKEN_URL = "https://login.salesforce.com/services/oauth2/token"

async def send_to_salesforce(lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json",
    }
    
    data = {
        "FirstName": lead.name.split()[0] if lead.name else "",
        "LastName": lead.name.split()[-1] if lead.name else "",
        "Email": lead.email,
        "Phone": lead.phone,
        "Company": lead.company,
        "Title": lead.position,
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(SALESFORCE_API_URL, headers=headers, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    logger.info(f"Successfully sent lead to Salesforce CRM: {result}")
                    return result
                else:
                    error_msg = await response.text()
                    logger.error(f"Failed to send lead to Salesforce CRM. Status: {response.status}, Error: {error_msg}")
                    raise ValueError(f"Salesforce CRM API error: {error_msg}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error while sending lead to Salesforce CRM: {str(e)}")
            raise ConnectionError(f"Network error: {str(e)}")

async def initiate_salesforce_oauth() -> str:
    params = {
        "client_id": SALESFORCE_CLIENT_ID,
        "redirect_uri": SALESFORCE_REDIRECT_URI,
        "response_type": "code",
        "scope": "api",
    }
    auth_url = f"{SALESFORCE_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    logger.info(f"Initiated Salesforce OAuth. Auth URL: {auth_url}")
    return auth_url

async def exchange_salesforce_code_for_token(code: str) -> OAuthCredentials:
    data = {
        "grant_type": "authorization_code",
        "client_id": SALESFORCE_CLIENT_ID,
        "client_secret": SALESFORCE_CLIENT_SECRET,
        "redirect_uri": SALESFORCE_REDIRECT_URI,
        "code": code,
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(SALESFORCE_TOKEN_URL, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    logger.info("Successfully exchanged code for Salesforce OAuth token")
                    return OAuthCredentials(
                        access_token=token_data["access_token"],
                        refresh_token=token_data.get("refresh_token"),
                        expires_at=int(token_data.get("expires_in", 3600)) + int(time.time())
                    )
                else:
                    error_msg = await response.text()
                    logger.error(f"Failed to exchange code for Salesforce OAuth token. Status: {response.status}, Error: {error_msg}")
                    raise ValueError(f"Salesforce OAuth error: {error_msg}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error while exchanging code for Salesforce OAuth token: {str(e)}")
            raise ConnectionError(f"Network error: {str(e)}")