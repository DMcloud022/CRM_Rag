from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models.oauth import OAuthCredentials
from typing import Dict, Optional
from datetime import datetime, timedelta
import jwt
from config import JWT_SECRET_KEY, JWT_ALGORITHM, TOKEN_EXPIRE_MINUTES
# from utils.exceptions import AuthenticationError

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
            raise f"Invalid token payload"
    except jwt.PyJWTError:
        raise f"Could not validate credentials"
    
    credentials = oauth_credentials.get(user_id, {}).get(crm_name)
    if credentials is None:
        raise f"Credentials not found"
    
    return credentials

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
    # Check if the token is expired or about to expire
    if credentials.is_expired():
        # Implement token refresh logic here
        # For now, we'll just raise an exception
        raise f"Token expired and refresh not implemented"
    return credentials