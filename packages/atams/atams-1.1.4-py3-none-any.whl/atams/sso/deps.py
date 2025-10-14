"""
API Dependencies
Handles authentication and authorization via Atlas SSO

Usage in user project (app/api/deps.py):
    from atams.sso import create_atlas_client, create_auth_dependencies
    from app.core.config import settings

    atlas_client = create_atlas_client(settings)
    get_current_user, require_auth, require_min_role_level, require_role_level = create_auth_dependencies(atlas_client)
"""
from typing import Optional, List, TYPE_CHECKING, Callable, Tuple
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

if TYPE_CHECKING:
    from atams.sso.client import AtlasClient

# JWT Bearer token security
security = HTTPBearer(auto_error=False)


def create_auth_dependencies(atlas_client: 'AtlasClient') -> Tuple[Callable, Callable, Callable, Callable]:
    """
    Create authentication dependency functions with configured atlas_client

    Args:
        atlas_client: Configured AtlasClient instance

    Returns:
        Tuple of (get_current_user, require_auth, require_min_role_level, require_role_level)

    Example:
        from atams.sso import create_atlas_client, create_auth_dependencies
        from app.core.config import settings

        atlas_client = create_atlas_client(settings)
        get_current_user, require_auth, require_min_role_level, require_role_level = create_auth_dependencies(atlas_client)
    """

    async def get_current_user(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[dict]:
        """
        Get current user from Atlas SSO with auto-refresh capability

        Flow:
        1. Try to get access token from Bearer header or ATLASTOKEN cookie
        2. Validate token with Atlas /auth/me
        3. If expired, try auto-refresh using ATLASREFRESH cookie
        4. Validate app access based on ATLAS_APP_CODE
        5. Return user info with roles

        Returns:
            User dict with: user_id, username, email, role_level, roles
            None if not authenticated
        """
        access_token = None
        refresh_token = None

        # 1. Try to get access token from cookie first
        access_token = request.cookies.get("ATLASTOKEN")

        # 2. If not in cookie, try Bearer header
        if not access_token and credentials:
            access_token = credentials.credentials

        # 3. Validate access token with Atlas
        if access_token:
            user_info = await atlas_client.get_user_info(access_token)

            if user_info:
                # Validate app access
                if not atlas_client.validate_app_access(user_info):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"No access to application"
                    )

                # Return user info
                return {
                    "user_id": user_info.get("u_id"),
                    "username": user_info.get("u_username"),
                    "email": user_info.get("u_email"),
                    "role_level": atlas_client.get_user_role_level(user_info),
                    "roles": atlas_client.get_user_roles_for_app(user_info),
                    "full_name": user_info.get("u_full_name"),
                    "status": user_info.get("u_status")
                }

        # 4. Access token invalid/expired, try auto-refresh
        refresh_token = request.cookies.get("ATLASREFRESH")

        if refresh_token:
            new_tokens = await atlas_client.refresh_access_token(refresh_token)

            if new_tokens:
                new_access_token = new_tokens.get("access_token")

                # Validate new access token
                user_info = await atlas_client.get_user_info(new_access_token)

                if user_info and atlas_client.validate_app_access(user_info):
                    return {
                        "user_id": user_info.get("u_id"),
                        "username": user_info.get("u_username"),
                        "email": user_info.get("u_email"),
                        "role_level": atlas_client.get_user_role_level(user_info),
                        "roles": atlas_client.get_user_roles_for_app(user_info),
                        "full_name": user_info.get("u_full_name"),
                        "status": user_info.get("u_status"),
                        "_new_access_token": new_access_token  # Flag for updating cookie
                    }

        # 5. All methods failed
        return None

    def require_auth(
        current_user: Optional[dict] = Depends(get_current_user)
    ) -> dict:
        """
        Require authenticated user

        Raises:
            HTTPException 401 if user not authenticated
        """
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return current_user

    def require_role_level(allowed_levels: List[int]):
        """
        Require user to have one of the allowed role levels

        This is the FIRST level validation at route level.
        Second level validation (what each level can do) should be in service layer.

        Example usage:
            @router.get("/admin/dashboard", dependencies=[Depends(require_role_level([50, 100]))])
            async def admin_dashboard():
                # Only users with role level 50 or 100 can access

        Args:
            allowed_levels: List of allowed role levels

        Raises:
            HTTPException 403 if user doesn't have required level
        """
        async def _check_role_level(
            current_user: dict = Depends(require_auth)
        ):
            user_role_level = current_user.get("role_level", 0)

            if user_role_level not in allowed_levels:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permission. Required role level: {allowed_levels}"
                )

        return _check_role_level

    def require_min_role_level(min_level: int):
        """
        Require user to have minimum role level

        Example usage:
            @router.get("/admin/users", dependencies=[Depends(require_min_role_level(50))])
            async def list_users():
                # Only users with role level >= 50 can access

        Args:
            min_level: Minimum required role level

        Raises:
            HTTPException 403 if user doesn't have required level
        """
        async def _check_min_level(
            current_user: dict = Depends(require_auth)
        ):
            user_role_level = current_user.get("role_level", 0)

            if user_role_level < min_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permission. Required minimum role level: {min_level}"
                )

        return _check_min_level

    return get_current_user, require_auth, require_min_role_level, require_role_level
