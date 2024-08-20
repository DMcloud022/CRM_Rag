import logging
from typing import Dict, Any, Callable
from backend.models.lead import Lead
from backend.models.oauth import OAuthCredentials
from backend.config import SUPPORTED_CRMS
from backend.services.crm_integration.zoho import send_to_zoho, initiate_zoho_oauth, exchange_zoho_code_for_token
from backend.services.crm_integration.hubspot import send_to_hubspot, initiate_hubspot_oauth, exchange_hubspot_code_for_token
from backend.services.crm_integration.salesforce import send_to_salesforce, initiate_salesforce_oauth, exchange_salesforce_code_for_token
from backend.services.crm_integration.dynamics import send_to_dynamics, initiate_dynamics_oauth, exchange_dynamics_code_for_token
# Import other CRM-specific functions as needed

logger = logging.getLogger(__name__)

CRMIntegrationFunc = Callable[[Lead, OAuthCredentials], Dict[str, Any]]


crm_integrations: Dict[str, CRMIntegrationFunc] = {
    "zoho": send_to_zoho,
    "hubspot": send_to_hubspot,
    "salesforce": send_to_salesforce,
    "dynamics": send_to_dynamics,
    # Add other CRM integrations here
}

oauth_initiation_funcs: Dict[str, Callable[[], str]] = {
    "zoho": initiate_zoho_oauth,
    "hubspot": initiate_hubspot_oauth,
    "salesforce": initiate_salesforce_oauth,
    "dynamics": initiate_dynamics_oauth,
    # Add other OAuth initiation functions here
}

oauth_exchange_funcs: Dict[str, Callable[[str], OAuthCredentials]] = {
    "zoho": exchange_zoho_code_for_token,
    "hubspot": exchange_hubspot_code_for_token,
    "salesforce": exchange_salesforce_code_for_token,
    "dynamics": exchange_dynamics_code_for_token,
    # Add other OAuth exchange functions here
}

async def send_lead_to_crm(crm_name: str, lead: Lead, credentials: OAuthCredentials) -> Dict[str, Any]:
    if crm_name not in SUPPORTED_CRMS:
        raise ValueError(f"Unsupported CRM: {crm_name}")
    
    if crm_name not in crm_integrations:
        raise NotImplementedError(f"Integration for {crm_name} is not implemented")
    
    try:
        result = await crm_integrations[crm_name](lead, credentials)
        logger.info(f"Successfully sent lead to {crm_name} CRM")
        return result
    except Exception as e:
        logger.error(f"Error sending lead to {crm_name} CRM: {str(e)}")
        raise

async def initiate_oauth(crm_name: str) -> str:
    if crm_name not in SUPPORTED_CRMS:
        raise ValueError(f"Unsupported CRM: {crm_name}")
    
    if crm_name not in oauth_initiation_funcs:
        raise NotImplementedError(f"OAuth initiation for {crm_name} is not implemented")
    
    try:
        return await oauth_initiation_funcs[crm_name]()
    except Exception as e:
        logger.error(f"Error initiating OAuth for {crm_name}: {str(e)}")
        raise

async def exchange_code_for_token(crm_name: str, code: str) -> OAuthCredentials:
    if crm_name not in SUPPORTED_CRMS:
        raise ValueError(f"Unsupported CRM: {crm_name}")
    
    if crm_name not in oauth_exchange_funcs:
        raise NotImplementedError(f"OAuth code exchange for {crm_name} is not implemented")
    
    try:
        return await oauth_exchange_funcs[crm_name](code)
    except Exception as e:
        logger.error(f"Error exchanging code for token for {crm_name}: {str(e)}")
        raise