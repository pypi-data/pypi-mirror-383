"""
user.py - User-related API endpoints.

Provides registration, login, logout, token refresh, and role-based access endpoints.
Supports JWT authentication and role-based authorization.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User, UserRole, Token
from app.schemas.user import UserRegister, UserResponse, UserLogin, MeSchema
from app.core.database import get_db
from app.utils.token import (
    create_access_token,
    create_refresh_token,
    store_token,
    get_current_user,
    verify_token
)
from app.core.config import settings
from app.auth.password_utils import hash_password, verify_password
from app.dependencies import require_roles

# -------------------------------------------------------------------
# Router setup
# -------------------------------------------------------------------
user_router = APIRouter(prefix="/users", tags=["Users"])

ACCESS_TOKEN_EXPIRE_MINUTES = settings.jwt_access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.jwt_refresh_token_expire_minutes


# -------------------------------------------------------------------
# Registration endpoint
# -------------------------------------------------------------------
@user_router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.

    Steps:
    1. Check if the email is already registered.
    2. Validate user role.
    3. Hash password and create a new user.
    4. Save user to database and return user data.
    """
    # Check for existing user
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role
    if user.role not in UserRole._value2member_map_:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Create new user
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        role=UserRole(user.role),
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# -------------------------------------------------------------------
# Login endpoint
# -------------------------------------------------------------------
@user_router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access and refresh tokens.

    Steps:
    1. Verify user credentials.
    2. Create JWT access and refresh tokens.
    3. Store tokens in the database.
    4. Return tokens to client.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        user_email=db_user.email,
        user_id=db_user.id,
        role=db_user.role.value,
        expires_delta=access_expires
    )
    refresh_token = create_refresh_token(
        user_email=db_user.email,
        user_id=db_user.id,
        expires_delta=refresh_expires
    )

    # Store tokens in DB
    store_token(db, token=access_token, user_id=db_user.id, expires_delta=access_expires, is_refresh=False)
    store_token(db, token=refresh_token, user_id=db_user.id, expires_delta=refresh_expires, is_refresh=True)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# -------------------------------------------------------------------
# Refresh access token
# -------------------------------------------------------------------
@user_router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Generate a new access token using a valid refresh token.

    Args:
        refresh_token (str): Refresh token string.

    Returns:
        dict: New access token with type.
    """
    payload = verify_token(refresh_token, db, is_refresh=True)
    user_id = payload.get("user_id")
    email = payload.get("email")
    role = db.query(User).filter(User.id == user_id).first().role.value

    access_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        user_email=email,
        user_id=user_id,
        role=role,
        expires_delta=access_expires
    )

    store_token(db, token=new_access_token, user_id=user_id, expires_delta=access_expires, is_refresh=False)

    return {"access_token": new_access_token, "token_type": "bearer"}


# -------------------------------------------------------------------
# Logout endpoint
# -------------------------------------------------------------------
@user_router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    """
    Logout user by revoking the provided refresh token.

    Args:
        refresh_token (str): Refresh token to revoke.

    Returns:
        dict: Success message if token is revoked.

    Raises:
        HTTPException: If refresh token is invalid.
    """
    db_token = db.query(Token).filter(Token.token == refresh_token, Token.is_refresh == True).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()
        return {"message": "Refresh token revoked successfully"}

    raise HTTPException(status_code=400, detail="Invalid refresh token")


# -------------------------------------------------------------------
# Get current logged-in user
# -------------------------------------------------------------------
@user_router.get("/me", response_model=MeSchema)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve the currently authenticated user.
    """
    return current_user


# -------------------------------------------------------------------
# Role-based access test endpoints
# -------------------------------------------------------------------
@user_router.get("/admin-role")
def admin_role_api(current_user: User = Depends(require_roles([UserRole.ADMIN]))):
    """
    Test endpoint accessible only by Admin users.
    """
    return {
        "message": "This API is only accessible by the user who has the Admin role",
        "user": current_user.full_name,
        "role": current_user.role.value
    }


@user_router.get("/user-role")
def user_role_api(current_user: User = Depends(require_roles([UserRole.USER]))):
    """
    Test endpoint accessible only by User role.
    """
    return {
        "message": "This API is only accessible by the user who has the User role",
        "user": current_user.full_name,
        "role": current_user.role.value
    }


@user_router.get("/multi-role")
def multiple_role_api(current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.USER]))):
    """
    Test endpoint accessible by users with Admin or User roles.
    """
    return {
        "message": "This API is only accessible by the user who has the User and Admin role",
        "user": current_user.full_name,
        "role": current_user.role.value
    }
