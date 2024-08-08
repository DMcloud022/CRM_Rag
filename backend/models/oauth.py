from pydantic import BaseModel
from typing import Optional

class OAuthCredentials(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None