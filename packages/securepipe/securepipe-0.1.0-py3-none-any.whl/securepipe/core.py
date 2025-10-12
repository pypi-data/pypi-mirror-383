import json
import base64
import hmac
import hashlib
import os
import time
import uuid as uuidlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from securepipe.utils import UUIDClass

class SecurePipe:
    def __init__(self, secret_key: str, uuid: str | None = None, tolerance: int = 30):
        length = 16
        if len(secret_key) < length:
            raise ValueError(f"Secret key must be at least {length} characters")
        self.secret_key = secret_key.encode()
        self.uuid = UUIDClass(uuid) if uuid else None
        self.tolerance = tolerance # this is in seconds

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive encryption key from secret key and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.secret_key))

    def _sign(self, data: bytes) -> str:
        """Generate HMAC signature for data."""
        signature = hmac.new(self.secret_key, data, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(signature).decode()

    def _verify_signature(self, data: bytes, signature: str) -> bool:
        """Verify HMAC signature."""
        expected_sig = hmac.new(self.secret_key, data, hashlib.sha256).digest()
        return hmac.compare_digest(base64.urlsafe_b64encode(expected_sig).decode(), signature)

    def encrypt(self, data, expires_in: int | None = None) -> str:
        """Encrypt data with optional expiration."""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data)
        else:
            data_str = str(data)

        salt = os.urandom(16)
        key1 = self._derive_key(salt)
        fernet1 = Fernet(key1)
        encrypted1 = fernet1.encrypt(data_str.encode())

        # Layer 2: UUID-based encryption
        if self.uuid:
            key2 = self._derive_key(self.uuid)
            uuid_used = None
        else:
            uuid_used = uuidlib.uuid4().bytes
            key2 = self._derive_key(uuid_used)

        fernet2 = Fernet(key2)
        encrypted2 = fernet2.encrypt(encrypted1)

        token_data = {
            "data": base64.urlsafe_b64encode(encrypted2).decode(),
            "salt": base64.urlsafe_b64encode(salt).decode(),
        }

        if uuid_used:
            token_data["uuid"] = base64.urlsafe_b64encode(uuid_used).decode()

        # Layer 3: Expiration
        if expires_in:
            token_data["expires_at"] = int(time.time()) + expires_in # expires_in is in seconds

        # Layer 4: Integrity HMAC
        json_data = json.dumps(token_data).encode()
        signature = self._sign(json_data)

        full_package = {
            "payload": base64.urlsafe_b64encode(json_data).decode(),
            "signature": signature,
        }

        return base64.urlsafe_b64encode(json.dumps(full_package).encode()).decode()

    def decrypt(self, token: str):
        """Decrypt token and verify integrity, expiration, and layers."""
        try:
            # Decode main wrapper
            decoded = base64.urlsafe_b64decode(token.encode())
            full_package = json.loads(decoded)

            payload = base64.urlsafe_b64decode(full_package["payload"].encode())
            signature = full_package["signature"]

            # Verify integrity
            if not self._verify_signature(payload, signature):
                return {"error": "Integrity check failed: invalid signature"}

            token_data = json.loads(payload)

            # Expiration check (if exists)
            if "expires_at" in token_data:
                now = int(time.time())
                if now > token_data["expires_at"] + self.tolerance:
                    return {"error": "Token expired"}

            # Retrieve components
            encrypted_data = base64.urlsafe_b64decode(token_data["data"])
            salt = base64.urlsafe_b64decode(token_data["salt"])
            key1 = self._derive_key(salt)

            # Second layer decryption
            if "uuid" in token_data:
                uuid_bytes = base64.urlsafe_b64decode(token_data["uuid"])
                key2 = self._derive_key(uuid_bytes)
            elif self.uuid:
                key2 = self._derive_key(self.uuid)
            else:
                return {"error": "Missing UUID for decryption"}

            fernet2 = Fernet(key2)
            decrypted1 = fernet2.decrypt(encrypted_data)

            fernet1 = Fernet(key1)
            decrypted_data = fernet1.decrypt(decrypted1).decode()

            try:
                return json.loads(decrypted_data)
            except json.JSONDecodeError:
                return decrypted_data

        except Exception as e:
            return {"error": f"Decryption failed: {str(e)}"}
    def decode_token_info(self, token: str):
        """
        Decode metadata from a token without decrypting the payload.
        Returns dictionary with:
            - salt (bytes)
            - uuid (bytes, if present)
            - expires_at (int, if present)
        Does NOT verify integrity or decrypt data.
        """
        try:
            # Decode main wrapper
            decoded = base64.urlsafe_b64decode(token.encode())
            full_package = json.loads(decoded)

            payload_encoded = full_package.get("payload")
            if not payload_encoded:
                return {"error": "Invalid token format: missing payload"}

            payload = base64.urlsafe_b64decode(payload_encoded.encode())
            token_data = json.loads(payload)

            info = {
                "salt": base64.urlsafe_b64decode(token_data["salt"]) if "salt" in token_data else None,
                "uuid": base64.urlsafe_b64decode(token_data["uuid"]) if "uuid" in token_data else None,
                "expires_at": token_data.get("expires_at")
            }

            return info

        except Exception as e:
            return {"error": f"Failed to decode token info: {str(e)}"}
