from typing import Dict, Callable, Any
from models.lead import Lead
from models.oauth import OAuthCredentials

# Import CRM-specific functions
from .zoho import send_to_zoho, initiate_zoho_oauth, exchange_zoho_code_for_token
#Uncomment and import other CRM functions as they are implemented
from .salesforce import send_to_salesforce, initiate_salesforce_oauth, exchange_salesforce_code_for_token
from .hubspot import create_lead_in_hubspot, initiate_hubspot_oauth, exchange_hubspot_code_for_token
from .dynamics import send_to_dynamics, initiate_dynamics_oauth, exchange_dynamics_code_for_token

# Type aliases for clarity
SendLeadFunc = Callable[[Lead, OAuthCredentials], Any]
InitiateOAuthFunc = Callable[[], str]
ExchangeCodeFunc = Callable[[str], OAuthCredentials]

# Mappings for CRM functions
send_lead_funcs: Dict[str, SendLeadFunc] = {
    "zoho": send_to_zoho,
    "salesforce": send_to_salesforce,
    "hubspot": create_lead_in_hubspot,
    "dynamics": send_to_dynamics,
}

initiate_oauth_funcs: Dict[str, InitiateOAuthFunc] = {
    "zoho": initiate_zoho_oauth,
    "salesforce": initiate_salesforce_oauth,
    "hubspot": initiate_hubspot_oauth,
    "dynamics": initiate_dynamics_oauth,
}

exchange_code_funcs: Dict[str, ExchangeCodeFunc] = {
    "zoho": exchange_zoho_code_for_token,
    "salesforce": exchange_salesforce_code_for_token,
    "hubspot": exchange_hubspot_code_for_token,
    "dynamics": exchange_dynamics_code_for_token,
}

async def send_lead_to_crm(crm_name: str, lead: Lead, credentials: OAuthCredentials) -> Any:
    if crm_name not in send_lead_funcs:
        raise ValueError(f"Unsupported CRM: {crm_name}")
    return await send_lead_funcs[crm_name](lead, credentials)

async def initiate_oauth(crm_name: str) -> str:
    if crm_name not in initiate_oauth_funcs:
        raise ValueError(f"Unsupported CRM for OAuth initiation: {crm_name}")
    return await initiate_oauth_funcs[crm_name]()

async def exchange_code_for_token(crm_name: str, code: str) -> OAuthCredentials:
    if crm_name not in exchange_code_funcs:
        raise ValueError(f"Unsupported CRM for code exchange: {crm_name}")
    return await exchange_code_funcs[crm_name](code)