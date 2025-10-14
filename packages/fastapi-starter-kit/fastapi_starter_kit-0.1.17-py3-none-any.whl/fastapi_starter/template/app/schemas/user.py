"""
user.py - Pydantic schemas for User-related requests and responses.

Includes request and response models for registration, login, token management,
and retrieving current user information.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


# -------------------------------------------------------------------
# Enum for user roles
# -------------------------------------------------------------------
class UserRole(str, Enum):
    """
    Enum representing possible user roles.
    """
    ADMIN = "admin"
    USER = "user"


# -------------------------------------------------------------------
# Request schemas
# -------------------------------------------------------------------
class UserRegister(BaseModel):
    """
    Schema for user registration request.
    
    Attributes:
        email (EmailStr): User's email address.
        full_name (str): Full name of the user.
        password (str): Plain-text password.
        role (UserRole): Role of the user (default: USER).
    """
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.USER

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    """
    Schema for user login request.
    
    Attributes:
        email (EmailStr): User's email.
        password (str): Plain-text password.
    """
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


# -------------------------------------------------------------------
# Response schemas
# -------------------------------------------------------------------
class UserResponse(BaseModel):
    """
    Schema used when returning user information.

    Attributes:
        id (int): User ID.
        email (EmailStr): User's email.
        full_name (str): Full name.
        role (UserRole): Role of the user.
        is_active (bool): Active status.
    """
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    """
    Schema for token response.

    Attributes:
        access_token (str): JWT access token.
        refresh_token (Optional[str]): JWT refresh token (optional).
        token_type (str): Token type (default: bearer).
    """
    access_token: str
    refresh_token: Optional[str]
    token_type: str = "bearer"


class MeSchema(UserResponse):
    """
    Schema returned by /users/me endpoint.

    Inherits from UserResponse and excludes sensitive fields like hashed_password.
    """
    pass
