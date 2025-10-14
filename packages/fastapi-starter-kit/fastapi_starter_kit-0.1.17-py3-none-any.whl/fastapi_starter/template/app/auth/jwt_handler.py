from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, Token

# OAuth2 scheme to extract token from the request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.login_url)


def decode_token(token: str) -> dict:
    """
    Decode a JWT token and return its payload.

    Args:
        token (str): JWT token string.

    Returns:
        dict: Payload of the JWT token.

    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Retrieve the currently authenticated user from the JWT token.

    Steps:
    1. Decode the token and extract `user_id`.
    2. Check if the token exists in the database and is not revoked.
    3. Retrieve the corresponding user from the database.

    Args:
        db (Session): SQLAlchemy database session.
        token (str): JWT token extracted via OAuth2 scheme.

    Returns:
        User: Authenticated user object.

    Raises:
        HTTPException: If token is invalid, revoked, or user not found.
    """
    payload = decode_token(token)
    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Check if token exists in DB and is not revoked
    db_token = db.query(Token).filter(
        Token.token == token,
        Token.is_revoked.is_(False)
    ).first()
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is revoked or invalid"
        )

    # Retrieve user from DB
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
