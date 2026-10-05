"""
Authentication Decorators
Provides dependency injection functions for FastAPI route protection
"""

from typing import Optional
from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    from .user_manager import user_manager
except ImportError:
    from app.auth.user_manager import user_manager

# Security scheme for Swagger UI
security = HTTPBearer()


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token

    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user": user["username"]}
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please provide Authorization header."
        )

    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme. Use 'Bearer <token>'"
            )
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Use 'Bearer <token>'"
        )

    # Verify token
    user_data = user_manager.verify_token(token)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return user_data


async def get_current_admin(
    user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to ensure current user is an admin

    Usage:
        @app.delete("/users/{username}")
        async def delete_user(username: str, admin: dict = Depends(get_current_admin)):
            # Only admins can access this route
            pass
    """
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )

    return user


async def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """
    Dependency to optionally get current user (doesn't fail if not authenticated)

    Usage:
        @app.get("/public")
        async def public_route(user: Optional[dict] = Depends(get_optional_user)):
            if user:
                return {"message": f"Hello {user['username']}"}
            return {"message": "Hello guest"}
    """
    if not authorization:
        return None

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None

        user_data = user_manager.verify_token(token)
        return user_data
    except (ValueError, Exception):
        return None


def require_role(required_role: str):
    """
    Dependency factory to require a specific role

    Usage:
        @app.post("/admin-action")
        async def admin_action(user: dict = Depends(require_role("admin"))):
            pass
    """
    async def role_checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{required_role}' required"
            )
        return user

    return role_checker
