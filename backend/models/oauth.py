from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OAuthCredentials(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None

    def is_expired(self) -> bool:
        return datetime.utcnow().timestamp() > self.expires_at

    class Config:
        arbitrary_types_allowed = True
