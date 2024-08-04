from .zoho import send_to_zoho, initiate_zoho_oauth, exchange_zoho_code_for_token
# from .salesforce import send_to_salesforce, initiate_salesforce_oauth
# from .hubspot import send_to_hubspot, initiate_hubspot_oauth
# from .dynamics import send_to_dynamics, initiate_dynamics_oauth

async def send_lead_to_crm(crm_name: str, lead, credentials):
    if crm_name == "zoho":
        return await send_to_zoho(lead, credentials)
    # elif crm_name == "salesforce":
    #     return await send_to_salesforce(lead, credentials)
    # elif crm_name == "hubspot":
    #     return await send_to_hubspot(lead, credentials)
    # elif crm_name == "dynamics":
    #     return await send_to_dynamics(lead, credentials)
    else:
        raise ValueError(f"Unsupported CRM: {crm_name}")

async def initiate_oauth(crm_name: str):
    if crm_name == "zoho":
        return await initiate_zoho_oauth()
    # elif crm_name == "salesforce":
    #     return await initiate_salesforce_oauth()
    # elif crm_name == "hubspot":
    #     return await initiate_hubspot_oauth()
    # elif crm_name == "dynamics":
    #     return await initiate_dynamics_oauth()
    else:
        raise ValueError(f"Unsupported CRM: {crm_name}")

async def exchange_code_for_token(crm_name: str, code: str):
    if crm_name == "zoho":
        return await exchange_zoho_code_for_token(code)
    # elif crm_name == "salesforce":
    #     return await exchange_salesforce_code_for_token(code)
    # elif crm_name == "hubspot":
    #     return await exchange_hubspot_code_for_token(code)
    # elif crm_name == "dynamics":
    #     return await exchange_dynamics_code_for_token(code)
    else:
        raise ValueError(f"Unsupported CRM: {crm_name}")