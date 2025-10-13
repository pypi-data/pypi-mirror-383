"""
users.py - SQLAlchemy models for User and Token.

Defines the User and Token models along with the UserRole enum.
This supports JWT authentication, role-based access control, and token management.
"""

from enum import Enum as PyEnum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    func,
    ForeignKey,
    Enum
)
from sqlalchemy.orm import relationship
from .base import Base


# -------------------------------------------------------------------
# Enum for user roles
# -------------------------------------------------------------------
class UserRole(PyEnum):
    """
    Enum representing possible user roles.
    """
    ADMIN = "admin"
    USER = "user"


# -------------------------------------------------------------------
# User model
# -------------------------------------------------------------------
class User(Base):
    """
    Represents an application user.

    Attributes:
        id (int): Primary key.
        role (UserRole): Role of the user (admin or user).
        email (str): Unique email address.
        full_name (str): Full name of the user.
        hashed_password (str): Hashed password.
        is_active (bool): Whether the user is active.
        created_at (datetime): Timestamp of user creation.
        updated_at (datetime): Timestamp of last update.
        tokens (List[Token]): Relationship to user's tokens.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(Enum(UserRole), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to tokens
    tokens = relationship("Token", back_populates="user")


# -------------------------------------------------------------------
# Token model
# -------------------------------------------------------------------
class Token(Base):
    """
    Represents a JWT token issued to a user.

    Attributes:
        id (int): Primary key.
        token (str): JWT token string.
        user_id (int): Foreign key to User.
        created_at (datetime): Timestamp of token creation.
        expired_at (datetime): Token expiration datetime.
        is_revoked (bool): Whether token has been revoked.
        is_refresh (bool): Indicates if token is a refresh token.
        user (User): Relationship to the owning user.
    """
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expired_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    is_refresh = Column(Boolean, default=False, nullable=True)

    # Relationship to user
    user = relationship("User", back_populates="tokens")
