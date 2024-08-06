import os
from dotenv import load_dotenv

load_dotenv()

# General settings
SUPPORTED_CRMS = ['salesforce', 'hubspot', 'zoho']  # Add all supported CRMs
MAX_REQUESTS_PER_MINUTE = 60

# API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

# Database settings (for future use)
DATABASE_URL = os.getenv("DATABASE_URL")

# Zoho CRM configuration
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI")

# Salesforce CRM configuration
SALESFORCE_CLIENT_ID = os.getenv("SALESFORCE_CLIENT_ID")
SALESFORCE_CLIENT_SECRET = os.getenv("SALESFORCE_CLIENT_SECRET")
SALESFORCE_REDIRECT_URI = os.getenv("SALESFORCE_REDIRECT_URI")

# HubSpot CRM configuration
HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")
HUBSPOT_REDIRECT_URI = os.getenv("HUBSPOT_REDIRECT_URI")

# Microsoft Dynamics CRM configuration
DYNAMICS_CLIENT_ID = os.getenv("DYNAMICS_CLIENT_ID")
DYNAMICS_CLIENT_SECRET = os.getenv("DYNAMICS_CLIENT_SECRET")
DYNAMICS_REDIRECT_URI = os.getenv("DYNAMICS_REDIRECT_URI")

# Environment-specific settings
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Security settings
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:8000").split(",")

def get_crm_config(crm_name: str) -> dict:
    """
    Get the configuration for a specific CRM.
    """
    crm_configs = {
        "zoho": {
            "client_id": ZOHO_CLIENT_ID,
            "client_secret": ZOHO_CLIENT_SECRET,
            "redirect_uri": ZOHO_REDIRECT_URI,
        },
        "salesforce": {
            "client_id": SALESFORCE_CLIENT_ID,
            "client_secret": SALESFORCE_CLIENT_SECRET,
            "redirect_uri": SALESFORCE_REDIRECT_URI,
        },
        "hubspot": {
            "client_id": HUBSPOT_CLIENT_ID,
            "client_secret": HUBSPOT_CLIENT_SECRET,
            "redirect_uri": HUBSPOT_REDIRECT_URI,
        },
        "dynamics": {
            "client_id": DYNAMICS_CLIENT_ID,
            "client_secret": DYNAMICS_CLIENT_SECRET,
            "redirect_uri": DYNAMICS_REDIRECT_URI,
        },
    }
    return crm_configs.get(crm_name.lower(), {})