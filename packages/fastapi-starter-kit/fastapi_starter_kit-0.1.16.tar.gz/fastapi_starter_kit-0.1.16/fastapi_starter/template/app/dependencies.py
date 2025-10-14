"""
dependencies.py - Custom FastAPI dependencies.

This module provides reusable dependencies such as role-based access control (RBAC)
for protecting routes based on user roles.
"""

from typing import List, Optional
from fastapi import Depends, HTTPException, status

from app.models.user import User, UserRole
from app.auth.jwt_handler import get_current_user  # JWT authentication dependency


# -------------------------------------------------------------------
# Role-based access control dependency
# -------------------------------------------------------------------
def require_roles(allowed_roles: Optional[List[UserRole]] = None):
    """
    Dependency to enforce role-based access control (RBAC).

    This dependency checks whether the current authenticated user's role
    is included in the list of `allowed_roles`. If not, access is denied.

    Args:
        allowed_roles (Optional[List[UserRole]]): List of roles permitted to access the endpoint.
            If None or empty, any authenticated user is allowed.

    Returns:
        function: A dependency function for FastAPI route protection.

    Raises:
        HTTPException: If the user's role is invalid or not allowed.
    """

    def role_checker(current_user: User = Depends(get_current_user)):
        try:
            # Ensure the role is a valid UserRole enum
            user_role = UserRole(current_user.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User has invalid role: {current_user.role}",
            )

        # If allowed_roles is defined and user_role is not in the list → deny access
        if allowed_roles and user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )

        return current_user

    return role_checker
