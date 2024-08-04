from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models.oauth import OAuthCredentials

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_oauth_credentials(token: str = Depends(oauth2_scheme)) -> OAuthCredentials:
    # In a real-world scenario, you would validate the token and retrieve the corresponding credentials
    # This is a simplified example
    if token == "fake_token":
        return OAuthCredentials(access_token=token)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )