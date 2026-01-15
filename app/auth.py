import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.hash import bcrypt
from dotenv import load_dotenv

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

if not SECRET_KEY:
    raise RuntimeError("❌ SECRET_KEY is not set in environment variables")

# -----------------------------
# Bcrypt password limit
# -----------------------------
BCRYPT_MAX_CHARS = 72  # bcrypt ignores chars beyond this

# -----------------------------
# Password hashing / verification
# -----------------------------
def hash_password(password: str) -> str:
    """Hash a password safely (truncate to bcrypt limit)."""
    safe_password = password[:BCRYPT_MAX_CHARS]
    return bcrypt.hash(safe_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password safely."""
    safe_password = plain_password[:BCRYPT_MAX_CHARS]
    return bcrypt.verify(safe_password, hashed_password)

# -----------------------------
# OAuth2 / JWT
# -----------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    if "sub" not in to_encode:
        raise ValueError("❌ 'sub' key is required in JWT payload")

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> str:
    """Extract and return user email from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: Optional[str] = payload.get("sub")
        if not email:
            raise credentials_exception
        return email

    except JWTError:
        raise credentials_exception
