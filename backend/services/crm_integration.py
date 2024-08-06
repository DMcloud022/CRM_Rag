import logging
from typing import Dict, Any, Callable
from models.lead import Lead
from models.oauth import OAuthCredentials
from config import SUPPORTED_CRMS


logger = logging.getLogger(__name__)

# Type hint for CRM integration functions
CRMIntegrationFunc = Callable[[Lead, OAuthCredentials], Dict[str, Any]]

# Dictionary to map CRM names to their respective integration functions
crm_integrations: Dict[str, CRMIntegrationFunc] = {}

def register_crm_integration(crm_name: str):
    """
    Decorator to register CRM integration functions.
    """
    def decorator(func: CRMIntegrationFunc):
        crm_integrations[crm_name] = func
        return func
    return decorator

async def send_lead_to_crm(crm_name: str, lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    """
    Send a lead to the specified CRM system.
    """
    if crm_name not in SUPPORTED_CRMS:
        raise ValueError(f"Unsupported CRM: {crm_name}")
    
    if crm_name not in crm_integrations:
        raise f"Integration for {crm_name} is not implemented"
    
    try:
        result = await crm_integrations[crm_name](lead, credentials)
        logger.info(f"Successfully sent lead to {crm_name} CRM")
        return result
    except Exception as e:
        logger.error(f"Error sending lead to {crm_name} CRM: {str(e)}")
        raise f"Failed to send lead to {crm_name} CRM: {str(e)}"

@register_crm_integration("zoho")
async def send_to_zoho(lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    # Implement Zoho CRM integration
    # This is a placeholder implementation
    return {"status": "success", "crm": "Zoho", "lead_id": "12345"}

@register_crm_integration("salesforce")
async def send_to_salesforce(lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    # Implement Salesforce CRM integration
    # This is a placeholder implementation
    return {"status": "success", "crm": "Salesforce", "lead_id": "SF67890"}

@register_crm_integration("hubspot")
async def send_to_hubspot(lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    # Implement HubSpot CRM integration
    # This is a placeholder implementation
    return {"status": "success", "crm": "HubSpot", "lead_id": "HB54321"}

@register_crm_integration("dynamics")
async def send_to_dynamics(lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    # Implement Microsoft Dynamics CRM integration
    # This is a placeholder implementation
    return {"status": "success", "crm": "Dynamics", "lead_id": "MD98765"}

async def initiate_oauth(crm_name: str) -> str:
    # Implement OAuth initiation logic
    # This is a placeholder implementation
    return f"https://{crm_name}.example.com/oauth/authorize"

async def exchange_code_for_token(crm_name: str, code: str) -> OAuthCredentials:
    # Implement code exchange logic
    # This is a placeholder implementation
    return OAuthCredentials(
        access_token="fake_access_token",
        refresh_token="fake_refresh_token",
        expires_in=3600
    )