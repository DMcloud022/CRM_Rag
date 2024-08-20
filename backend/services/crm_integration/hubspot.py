import aiohttp
import logging
from typing import Dict, Any, List
from models.lead import Lead
from models.oauth import OAuthCredentials
from config import HUBSPOT_CLIENT_ID, HUBSPOT_CLIENT_SECRET, HUBSPOT_REDIRECT_URI
import time

logger = logging.getLogger(__name__)

HUBSPOT_API_BASE_URL = "https://api.hubapi.com"
HUBSPOT_AUTH_URL = "https://app.hubspot.com/oauth/authorize"
HUBSPOT_TOKEN_URL = "https://api.hubapi.com/oauth/v1/token"

HUBSPOT_SCOPES = [
    "crm.objects.companies.read",
    "crm.objects.companies.write",
    "crm.objects.contacts.read",
    "crm.objects.contacts.write",
    "crm.objects.custom.read",
    "crm.objects.custom.write",
    "crm.objects.leads.read",
    "crm.objects.leads.write",
    "crm.schemas.companies.read",
    "crm.schemas.companies.write",
    "crm.schemas.contacts.read",
    "crm.schemas.contacts.write",
    "crm.schemas.custom.read",
    "oauth"
]

async def send_to_hubspot(lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    return await create_lead(lead, credentials)

async def create_lead(lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/leads"
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
    return await _make_request("POST", url, headers, json=data)

async def batch_create_leads(leads: List[Lead], credentials: OAuthCredentials) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/leads/batch/create"
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "inputs": [
            {
                "properties": {
                    "firstname": lead.name.split()[0] if lead.name else "",
                    "lastname": lead.name.split()[-1] if lead.name else "",
                    "email": lead.email,
                    "phone": lead.phone,
                    "company": lead.company,
                    "jobtitle": lead.position,
                }
            }
            for lead in leads
        ]
    }
    return await _make_request("POST", url, headers, json=data)

async def batch_read_leads(lead_ids: List[str], credentials: OAuthCredentials) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/leads/batch/read"
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json",
    }
    data = {
        "properties": ["firstname", "lastname", "email", "phone", "company", "jobtitle"],
        "inputs": [{"id": lead_id} for lead_id in lead_ids]
    }
    return await _make_request("POST", url, headers, json=data)

async def batch_update_leads(leads: List[Dict[str, Any]], credentials: OAuthCredentials) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/leads/batch/update"
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json",
    }
    data = {"inputs": leads}
    return await _make_request("POST", url, headers, json=data)

async def batch_upsert_leads(leads: List[Dict[str, Any]], credentials: OAuthCredentials) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/leads/batch/upsert"
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json",
    }
    data = {"inputs": leads}
    return await _make_request("POST", url, headers, json=data)

async def get_all_leads(credentials: OAuthCredentials, limit: int = 100) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/leads"
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
    }
    params = {"limit": limit}
    return await _make_request("GET", url, headers, params=params)

async def get_lead_by_id(lead_id: str, credentials: OAuthCredentials) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/leads/{lead_id}"
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
    }
    return await _make_request("GET", url, headers)

async def update_lead(lead_id: str, properties: Dict[str, Any], credentials: OAuthCredentials) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/leads/{lead_id}"
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json",
    }
    data = {"properties": properties}
    return await _make_request("PATCH", url, headers, json=data)

async def search_leads(search_query: Dict[str, Any], credentials: OAuthCredentials) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/leads/search"
    headers = {
        "Authorization": f"Bearer {credentials.access_token}",
        "Content-Type": "application/json",
    }
    return await _make_request("POST", url, headers, json=search_query)

async def _make_request(method: str, url: str, headers: Dict[str, str], **kwargs) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(method, url, headers=headers, **kwargs) as response:
                if response.status in (200, 201):
                    result = await response.json()
                    logger.info(f"Successfully made {method} request to {url}")
                    return result
                else:
                    error_msg = await response.text()
                    logger.error(f"Failed to make {method} request to {url}. Status: {response.status}, Error: {error_msg}")
                    raise ValueError(f"HubSpot API error: {error_msg}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error while making {method} request to {url}: {str(e)}")
            raise ConnectionError(f"Network error: {str(e)}")

async def initiate_hubspot_oauth() -> str:
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