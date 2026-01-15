from pydantic import BaseModel, EmailStr
from typing import Optional

# -----------------------------
# User Registration Schema
# -----------------------------
class UserRegister(BaseModel):
    """Schema for user registration request."""
    name: str
    email: EmailStr
    password: str

# -----------------------------
# User Login Schema
# -----------------------------
class UserLogin(BaseModel):
    """Schema for user login request."""
    email: EmailStr
    password: str

# -----------------------------
# JWT Token Response Schema
# -----------------------------
class Token(BaseModel):
    """Schema for JWT access token response."""
    access_token: str
    token_type: str = "bearer"

# -----------------------------
# Token Data Schema
# -----------------------------
class TokenData(BaseModel):
    """Schema for decoded JWT token data."""
    email: Optional[str] = None
