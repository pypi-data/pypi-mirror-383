"""
Atlas SSO Integration
====================
Handles authentication and authorization via Atlas SSO.

Usage in user project:
    from atams.sso import create_atlas_client, create_auth_dependencies
    from app.core.config import settings

    # Create Atlas client
    atlas_client = create_atlas_client(settings)

    # Create auth dependencies
    get_current_user, require_auth, require_min_role_level, require_role_level = create_auth_dependencies(atlas_client)
"""
from atams.sso.client import AtlasClient, create_atlas_client
from atams.sso.deps import create_auth_dependencies
from atams.sso.encryption import AtlasEncryption

__all__ = [
    "AtlasClient",
    "create_atlas_client",
    "create_auth_dependencies",
    "AtlasEncryption",
]
