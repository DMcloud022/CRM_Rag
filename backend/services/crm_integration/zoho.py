import aiohttp
from models.lead import Lead
from models.oauth import OAuthCredentials
from config import ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REDIRECT_URI

ZOHO_API_URL = "https://www.zohoapis.com/crm/v2/Leads"
ZOHO_AUTH_URL = "https://accounts.zoho.com/oauth/v2/auth"
ZOHO_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"

async def send_to_zoho(lead: Lead, credentials: OAuthCredentials):
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
    
    async with aiohttp.ClientSession() as session:
        async with session.post(ZOHO_API_URL, headers=headers, json=data) as response:
            return await response.json()

async def initiate_zoho_oauth():
    params = {
        "client_id": ZOHO_CLIENT_ID,
        "redirect_uri": ZOHO_REDIRECT_URI,
        "scope": "ZohoCRM.modules.ALL",
        "response_type": "code",
        "access_type": "offline",
    }
    return f"{ZOHO_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

async def exchange_zoho_code_for_token(code: str):
    data = {
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "redirect_uri": ZOHO_REDIRECT_URI,
        "code": code,
        "grant_type": "authorization_code",
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(ZOHO_TOKEN_URL, data=data) as response:
            token_data = await response.json()
            return OAuthCredentials(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_at=token_data.get("expires_in")
            )