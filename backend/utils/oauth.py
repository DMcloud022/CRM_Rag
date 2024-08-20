from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models.oauth import OAuthCredentials
from typing import Dict, Optional
from datetime import datetime, timedelta
import jwt
import httpx
from config import JWT_SECRET_KEY, JWT_ALGORITHM, TOKEN_EXPIRE_MINUTES
from config import HUBSPOT_CLIENT_ID, HUBSPOT_CLIENT_SECRET, HUBSPOT_REDIRECT_URI

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory storage for OAuth credentials (replace with database in production)
oauth_credentials: Dict[str, Dict[str, OAuthCredentials]] = {}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_oauth_credentials(token: str = Depends(oauth2_scheme)) -> OAuthCredentials:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        crm_name: str = payload.get("crm")
        if user_id is None or crm_name is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    credentials = oauth_credentials.get(user_id, {}).get(crm_name)
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credentials not found")
    
    return await validate_and_refresh_token(credentials)

async def store_oauth_credentials(user_id: str, crm_name: str, credentials: OAuthCredentials):
    if user_id not in oauth_credentials:
        oauth_credentials[user_id] = {}
    oauth_credentials[user_id][crm_name] = credentials

async def get_user_credentials(user_id: str, crm_name: str) -> Optional[OAuthCredentials]:
    return oauth_credentials.get(user_id, {}).get(crm_name)

async def create_user_token(user_id: str, crm_name: str) -> str:
    access_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id, "crm": crm_name}, expires_delta=access_token_expires
    )
    return access_token

async def validate_and_refresh_token(credentials: OAuthCredentials) -> OAuthCredentials:
    if credentials.is_expired():
        # Implement token refresh logic here
        # For this example, we'll raise an exception, but in a real-world scenario,
        # you would refresh the token using the refresh_token
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired and refresh not implemented")
    return credentials

async def get_or_create_credentials(user_id: str, crm_name: str) -> OAuthCredentials:
    credentials = await get_user_credentials(user_id, crm_name)
    if credentials is None:
        # If credentials don't exist, initiate the OAuth flow
        # This is a placeholder and should be replaced with actual OAuth initiation logic
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OAuth credentials not found. Please authenticate.")
    return credentials

async def handle_oauth_callback(user_id: str, crm_name: str, code: str):
    # This function should be called after receiving the OAuth callback
    # It should exchange the code for tokens and store the credentials
    credentials = await exchange_code_for_token(crm_name, code)
    await store_oauth_credentials(user_id, crm_name, credentials)
    return await create_user_token(user_id, crm_name)

async def exchange_code_for_token(crm_name: str, code: str) -> OAuthCredentials:
    # Implement the token exchange logic here
    # This is a placeholder and should be replaced with actual API calls to the CRM's token endpoint
    if crm_name == "hubspot":
        # Example for HubSpot
        token_url = "https://api.hubapi.com/oauth/v1/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": HUBSPOT_CLIENT_ID,
            "client_secret": HUBSPOT_CLIENT_SECRET,
            "redirect_uri": HUBSPOT_REDIRECT_URI,
            "code": code
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                return OAuthCredentials(
                    access_token=token_data["access_token"],
                    refresh_token=token_data.get("refresh_token"),
                    expires_at=datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
                )
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to exchange code for token")
    else:
        raise NotImplementedError(f"Token exchange for {crm_name} is not implemented")