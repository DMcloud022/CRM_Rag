import aiohttp
import logging
from typing import Dict, Any
from models.lead import Lead, Company, CustomObject, Note
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

async def create_object_in_hubspot(object_type: str, data: Dict[str, Any], access_token: str) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/{object_type}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    return await _make_request("POST", url, headers, json=data)

async def update_object_in_hubspot(object_type: str, object_id: str, data: Dict[str, Any], access_token: str) -> Dict[str, Any]:
    url = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/{object_type}/{object_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    return await _make_request("PATCH", url, headers, json=data)

async def create_lead_in_hubspot(lead: Lead, access_token: str) -> Dict[str, Any]:
    properties = lead_to_hubspot_properties(lead)
    data = {"properties": properties}
    return await create_object_in_hubspot("contacts", data, access_token)

async def update_lead_in_hubspot(lead_id: str, lead: Lead, access_token: str) -> Dict[str, Any]:
    properties = lead_to_hubspot_properties(lead)
    data = {"properties": properties}
    return await update_object_in_hubspot("contacts", lead_id, data, access_token)

async def create_company_in_hubspot(company: Company, access_token: str) -> Dict[str, Any]:
    properties = company_to_hubspot_properties(company)
    data = {"properties": properties}
    return await create_object_in_hubspot("companies", data, access_token)

async def create_note_in_hubspot(note: Note, access_token: str) -> Dict[str, Any]:
    properties = note_to_hubspot_properties(note)
    data = {
        "properties": properties,
        "associations": [
            {
                "to": {"id": note.associated_object_id},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": note.association_type}]
            }
        ]
    }
    return await create_object_in_hubspot("notes", data, access_token)

async def create_custom_object_in_hubspot(custom_object: CustomObject, object_type: str, access_token: str) -> Dict[str, Any]:
    return await create_object_in_hubspot(object_type, {"properties": custom_object.properties}, access_token)

def lead_to_hubspot_properties(lead: Lead) -> Dict[str, Any]:
    properties = {
        "firstname": lead.first_name,
        "lastname": lead.last_name,
        "email": lead.email,
        "phone": lead.phone,
        "company": lead.company,
        "jobtitle": lead.job_title,
        "website": str(lead.website) if lead.website else None,
        "twitter_handle": lead.twitter_handle,
        "lifecyclestage": lead.lifecycle_stage,
    }

    if lead.address:
        properties.update({
            "address": lead.address.street,
            "city": lead.address.city,
            "state": lead.address.state,
            "zip": lead.address.postal_code,
            "country": lead.address.country,
        })

    if lead.public_data:
        properties.update({
            "bio": lead.public_data.bio,
            "skills": ",".join(lead.public_data.skills),
            "languages": ",".join(lead.public_data.languages),
            "interests": ",".join(lead.public_data.interests),
            "publications": ",".join(lead.public_data.publications),
            "awards": ",".join(lead.public_data.awards),
        })

    return {k: v for k, v in properties.items() if v is not None}

def company_to_hubspot_properties(company: Company) -> Dict[str, Any]:
    return {
        "name": company.name,
        "domain": company.domain,
        "industry": company.industry,
        # Add more properties as needed
    }

def note_to_hubspot_properties(note: Note) -> Dict[str, Any]:
    return {
        "hs_note_body": note.content,
        "hs_timestamp": note.timestamp.isoformat(),
    }

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