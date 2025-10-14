"""
Atlas SSO Client
Handles communication with Atlas SSO service for authentication and authorization
"""
import httpx
import json
from typing import Optional, Dict, Any, TYPE_CHECKING
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

if TYPE_CHECKING:
    from atams.config.base import AtamsBaseSettings


class AtlasClient:
    """Client for Atlas SSO API communication"""

    def __init__(
        self,
        base_url: str,
        app_code: str,
        encryption_key: str = "atams_apps_secret_key_goes_here",
        encryption_iv: str = "atams_apps_iv!!"
    ):
        """
        Initialize Atlas SSO client

        Args:
            base_url: Atlas SSO base URL
            app_code: Application code for role validation
            encryption_key: Atlas encryption key (default for ATAMS ecosystem)
            encryption_iv: Atlas encryption IV (default for ATAMS ecosystem)
        """
        self.base_url = base_url
        self.app_code = app_code
        # Setup decryption for Atlas responses
        self.key = encryption_key.encode('utf-8')[:32].ljust(32, b'\0')
        self.iv = encryption_iv.encode('utf-8')[:16].ljust(16, b'\0')

    def _decrypt_atlas_response(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Decrypt Atlas encrypted response

        Args:
            encrypted_data: Base64 encoded encrypted string from Atlas

        Returns:
            Decrypted JSON data as dict
        """
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            encrypted_bytes = base64.b64decode(encrypted_data)
            decrypted = cipher.decrypt(encrypted_bytes)
            unpadded = unpad(decrypted, AES.block_size)
            return json.loads(unpadded.decode('utf-8'))
        except Exception as e:
            # If decryption fails, return empty dict
            return {}

    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user info from Atlas /auth/me endpoint

        Args:
            access_token: JWT access token from Atlas

        Returns:
            User info dict with roles, or None if token invalid
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/auth/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )

                if response.status_code == 200:
                    response_data = response.json()

                    # Check if response is encrypted
                    if response_data.get("encrypted"):
                        # Decrypt Atlas response
                        encrypted_data = response_data.get("data")
                        decrypted = self._decrypt_atlas_response(encrypted_data)
                        return decrypted.get("data")
                    else:
                        # Plain response
                        return response_data.get("data")

                return None

        except httpx.RequestError:
            # Connection error to Atlas
            return None
        except Exception:
            return None

    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: JWT refresh token from Atlas

        Returns:
            Dict with new access_token and refresh_token, or None if failed
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/auth/refresh",
                    json={"refresh_token": refresh_token},
                    timeout=10.0
                )

                if response.status_code == 200:
                    response_data = response.json()

                    # Check if response is encrypted
                    if response_data.get("encrypted"):
                        # Decrypt Atlas response
                        encrypted_data = response_data.get("data")
                        decrypted = self._decrypt_atlas_response(encrypted_data)
                        return decrypted.get("data")
                    else:
                        # Plain response
                        return response_data.get("data")

                return None

        except httpx.RequestError:
            return None
        except Exception:
            return None

    def validate_app_access(self, user_info: Dict[str, Any]) -> bool:
        """
        Validate if user has access to this application

        Args:
            user_info: User info from Atlas /auth/me

        Returns:
            True if user has role for this app, False otherwise
        """
        roles = user_info.get("roles", [])

        # Check if user has any role for this app (case-insensitive)
        has_access = any(
            role.get("app_code", "").lower() == self.app_code.lower()
            for role in roles
        )

        # Also allow SUPER_ADMIN from ATLAS to access any app
        is_super_admin = any(
            role.get("app_code", "").upper() == "ATLAS" and
            role.get("role_code", "").upper() == "SUPER_ADMIN"
            for role in roles
        )

        return has_access or is_super_admin

    def get_user_role_level(self, user_info: Dict[str, Any]) -> int:
        """
        Get highest role level for this application

        Args:
            user_info: User info from Atlas /auth/me

        Returns:
            Highest role level (0 if no roles)
        """
        roles = user_info.get("roles", [])

        # Get all role levels for this app (case-insensitive)
        app_role_levels = [
            role.get("role_level", 0)
            for role in roles
            if role.get("app_code", "").lower() == self.app_code.lower()
        ]

        # SUPER_ADMIN from ATLAS has level 100
        is_super_admin = any(
            role.get("app_code", "").upper() == "ATLAS" and
            role.get("role_code", "").upper() == "SUPER_ADMIN"
            for role in roles
        )

        if is_super_admin:
            return 100

        return max(app_role_levels) if app_role_levels else 0

    def get_user_roles_for_app(self, user_info: Dict[str, Any]) -> list:
        """
        Get all roles for this application

        Args:
            user_info: User info from Atlas /auth/me

        Returns:
            List of roles for this app
        """
        roles = user_info.get("roles", [])

        return [
            role for role in roles
            if role.get("app_code", "").lower() == self.app_code.lower()
        ]


def create_atlas_client(settings: 'AtamsBaseSettings') -> AtlasClient:
    """
    Create AtlasClient from settings

    Args:
        settings: Application settings

    Returns:
        Configured AtlasClient instance

    Example:
        from app.core.config import settings
        from atams.sso import create_atlas_client

        atlas_client = create_atlas_client(settings)
    """
    return AtlasClient(
        base_url=settings.ATLAS_SSO_URL,
        app_code=settings.ATLAS_APP_CODE,
        encryption_key=settings.ATLAS_ENCRYPTION_KEY,
        encryption_iv=settings.ATLAS_ENCRYPTION_IV
    )
