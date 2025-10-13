"""
token.py - Utility functions for JWT token management.

Handles creation, storage, and validation of JWT access and refresh tokens,
and provides utilities to retrieve the currently authenticated user.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session

from app.models.user import Token, User
from app.core.config import settings
from app.core.database import get_db

# -------------------------------------------------------------------
# OAuth2 scheme setup
# -------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# -------------------------------------------------------------------
# Token creation utilities
# -------------------------------------------------------------------
def create_access_token(
    user_email: str,
    user_id: int,
    expires_delta: Optional[timedelta] = None,
    role: Optional[str] = None,
    permissions: Optional[List[str]] = None,
) -> str:
    """
    Generate a JWT access token with optional role and permissions.

    Args:
        user_email (str): Email of the user.
        user_id (int): User ID.
        expires_delta (Optional[timedelta]): Expiration time for token.
        role (Optional[str]): User role (e.g., "admin" or "user").
        permissions (Optional[List[str]]): List of granted permissions.

    Returns:
        str: Encoded JWT access token.
    """
    expires_delta = expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    expire_time = datetime.utcnow() + expires_delta

    payload = {
        "email": user_email,
        "exp": expire_time,
        "user_id": user_id,
        "role": role,
        "permissions": permissions or []
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    user_email: str,
    user_id: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a JWT refresh token.

    Args:
        user_email (str): Email of the user.
        user_id (int): User ID.
        expires_delta (Optional[timedelta]): Expiration duration.

    Returns:
        str: Encoded JWT refresh token.
    """
    expires_delta = expires_delta or timedelta(minutes=settings.jwt_refresh_token_expire_minutes)
    expire_time = datetime.utcnow() + expires_delta

    payload = {
        "email": user_email,
        "exp": expire_time,
        "user_id": user_id
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# -------------------------------------------------------------------
# Token persistence utilities
# -------------------------------------------------------------------
def store_token(
    db: Session,
    token: str,
    user_id: int,
    expires_delta: timedelta,
    is_refresh: bool = False
) -> Token:
    """
    Store a JWT token (access or refresh) in the database.

    Args:
        db (Session): SQLAlchemy session.
        token (str): JWT token string.
        user_id (int): ID of the user.
        expires_delta (timedelta): Expiration duration.
        is_refresh (bool): True if refresh token, else False.

    Returns:
        Token: Stored Token object.
    """
    expire_time = datetime.utcnow() + expires_delta
    db_token = Token(
        token=token,
        user_id=user_id,
        expired_at=expire_time,
        is_revoked=False,
        is_refresh=is_refresh
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


# -------------------------------------------------------------------
# Token verification
# -------------------------------------------------------------------
def verify_token(token: str, db: Session, is_refresh: bool = False) -> dict:
    """
    Verify JWT token validity and ensure it’s not revoked in the database.

    Args:
        token (str): JWT token string.
        db (Session): SQLAlchemy session.
        is_refresh (bool): Whether the token is a refresh token.

    Returns:
        dict: Decoded token payload.

    Raises:
        HTTPException: If token is invalid, revoked, or expired.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        db_token = db.query(Token).filter(Token.token == token, Token.is_refresh == is_refresh).first()
        if not db_token or db_token.is_revoked:
            raise HTTPException(status_code=401, detail="Token revoked or invalid")

        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=498, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# -------------------------------------------------------------------
# Current user retrieval
# -------------------------------------------------------------------
def get_current_user(
    token: str = Security(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency that retrieves the currently authenticated user.

    Args:
        token (str): JWT token extracted via OAuth2 scheme.
        db (Session): SQLAlchemy session.

    Returns:
        User: Authenticated user instance.

    Raises:
        HTTPException: If token or user is invalid.
    """
    payload = verify_token(token, db, is_refresh=False)
    user_id = payload.get("user_id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
