"""
User service for handling user-related operations.
"""

import sqlite3
import bcrypt
import os
import re
from typing import Optional, Tuple
from fastapi import HTTPException

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'workout.db')

def get_db_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password complexity.
    
    Requirements:
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, ""

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Check a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(email: str, password: str) -> dict:
    """
    Create a new user.
    
    Args:
        email: User's email address
        password: User's password (will be hashed)
        
    Returns:
        Dictionary with user information (without password)
        
    Raises:
        HTTPException: If validation fails or user already exists
    """
    # Validate email
    if not validate_email(email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Validate password
    is_valid, message = validate_password(password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Insert user into database
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, hashed_password)
            )
            user_id = cursor.lastrowid
            conn.commit()
            
            return {
                "id": user_id,
                "email": email,
                "created_at": None,  # Will be set by database
                "updated_at": None   # Will be set by database
            }
    except sqlite3.IntegrityError as e:
        if "email" in str(e).lower():
            raise HTTPException(status_code=409, detail="User with this email already exists")
        raise HTTPException(status_code=500, detail="Database error")

def get_user_by_email(email: str) -> Optional[dict]:
    """
    Get user by email.
    
    Args:
        email: User's email address
        
    Returns:
        Dictionary with user information or None if not found
    """
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT id, email, password_hash, created_at, updated_at FROM users WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "email": row["email"],
                "password_hash": row["password_hash"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        return None

def authenticate_user(email: str, password: str) -> Optional[dict]:
    """
    Authenticate a user.
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        Dictionary with user information or None if authentication fails
    """
    user = get_user_by_email(email)
    if user and check_password(password, user["password_hash"]):
        # Remove password_hash from returned user data
        user.pop("password_hash")
        return user
    return None