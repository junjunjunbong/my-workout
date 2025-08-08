"""
Authentication utilities: JWT creation and verification, FastAPI dependency for protected routes.
"""
from datetime import datetime, timedelta, timezone
import os
from typing import Optional, Dict

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

from .user_service import get_user_by_email

# Load environment variables from backend/.env if present
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

JWT_SECRET = os.getenv("JWT_SECRET", "dev-insecure-secret-change-me")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))

http_bearer = HTTPBearer(auto_error=False)


def create_access_token(subject: str | int, extra_claims: Optional[Dict] = None, expires_minutes: Optional[int] = None) -> str:
    now = datetime.now(timezone.utc)
    exp_minutes = expires_minutes if expires_minutes is not None else JWT_EXPIRES_MINUTES
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return token


def verify_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def auth_dependency(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)) -> Dict:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing or invalid")
    payload = verify_token(credentials.credentials)
    return payload  # includes sub=user_id
