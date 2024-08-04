from models.lead import Lead

async def send_lead_to_crm(crm_name: str, lead: Lead):
    if crm_name == "zoho":
        return await send_to_zoho(lead)
    elif crm_name == "salesforce":
        return await send_to_salesforce(lead)
    elif crm_name == "hubspot":
        return await send_to_hubspot(lead)
    elif crm_name == "dynamics":
        return await send_to_dynamics(lead)
    else:
        raise ValueError(f"Unsupported CRM: {crm_name}")

async def send_to_zoho(lead: Lead):
    # Implement Zoho CRM integration
    pass

async def send_to_salesforce(lead: Lead):
    # Implement Salesforce CRM integration
    pass

async def send_to_hubspot(lead: Lead):
    # Implement HubSpot CRM integration
    pass

async def send_to_dynamics(lead: Lead):
    # Implement Microsoft Dynamics CRM integration
    pass