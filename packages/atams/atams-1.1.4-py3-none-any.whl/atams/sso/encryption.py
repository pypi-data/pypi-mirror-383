"""
Atlas SSO Encryption utilities
Handles encryption/decryption for Atlas communication
"""
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import json
from typing import Dict, Any


class AtlasEncryption:
    """Atlas encryption/decryption handler"""

    def __init__(self, encryption_key: str, encryption_iv: str):
        self.key = encryption_key.encode('utf-8')[:32].ljust(32, b'\0')
        self.iv = encryption_iv.encode('utf-8')[:16].ljust(16, b'\0')

    def decrypt(self, encrypted_data: str) -> Dict[str, Any]:
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
