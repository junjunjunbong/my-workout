from pydantic import BaseModel, AnyUrl
from typing import Optional

class UserProfileResponse(BaseModel):
    id: int
    email: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    goal: Optional[str] = None

class UserProfileUpdateRequest(BaseModel):
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    goal: Optional[str] = None