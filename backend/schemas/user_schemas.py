"""
Pydantic models for user-related API endpoints.
"""

from pydantic import BaseModel, EmailStr, validator

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserRegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: int = None

class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserLoginResponse(BaseModel):
    success: bool
    message: str
    user_id: int = None
    token: str = None