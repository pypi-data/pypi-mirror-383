"""
Response Encryption
==================
AES-256 encryption for GET endpoint responses.

Usage:
    from atams.encryption import encrypt_response_data
    from app.core.config import settings

    response = DataResponse(success=True, data=user_data)
    return encrypt_response_data(response, settings)
"""
from atams.encryption.response import ResponseEncryption, encrypt_response_data

__all__ = [
    "ResponseEncryption",
    "encrypt_response_data",
]
