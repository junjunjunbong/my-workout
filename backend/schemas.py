from pydantic import BaseModel, validator
from typing import List, Optional
import re

class SetRecordModel(BaseModel):
    weight_kg: float
    reps: int

class CardioRecordModel(BaseModel):
    minutes: float
    distance_km: Optional[float] = None

class WorkoutCreateModel(BaseModel):
    date: str
    category: str
    exercise: str
    type: str
    sets: Optional[List[SetRecordModel]] = None
    cardio: Optional[CardioRecordModel] = None
    notes: Optional[str] = None

class RoutineCreateModel(BaseModel):
    name: str
    memo: Optional[str] = None
    items: List[dict]

class UserRegistrationModel(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def validate_email(cls, v):
        # Basic email validation regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        # Password complexity requirements:
        # - At least 8 characters
        # - Contains at least one uppercase letter
        # - Contains at least one lowercase letter
        # - Contains at least one digit
        # - Contains at least one special character
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v

class UserLoginModel(BaseModel):
    email: str
    password: str