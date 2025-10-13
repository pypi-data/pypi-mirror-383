"""
Secrets Management

Provides secure storage and retrieval of sensitive data:
- API keys
- Passwords
- Tokens
- Certificates
- Encryption/decryption
"""

import os
import json
import base64
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta
import hashlib


@dataclass
class Secret:
    """
    Secret data container

    Attributes:
        name: Secret name
        value: Secret value
        created_at: Creation timestamp
        expires_at: Expiration timestamp
        metadata: Additional metadata
    """

    name: str
    value: str
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

    def is_expired(self) -> bool:
        """Check if secret is expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class SecretsManager:
    """
    Secrets manager for secure storage

    Features:
    - Encrypted storage
    - Secret rotation
    - Expiration tracking
    - Access logging
    - Environment variable integration

    Example:
        ```python
        # Create secrets manager
        secrets = SecretsManager(storage_path="secrets.enc")

        # Store secret
        secrets.set_secret(
            "openai_api_key",
            "sk-...",
            expires_in_days=90
        )

        # Retrieve secret
        api_key = secrets.get_secret("openai_api_key")

        # List secrets
        for name in secrets.list_secrets():
            print(name)

        # Delete secret
        secrets.delete_secret("openai_api_key")
        ```
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        encryption_key: Optional[str] = None,
    ):
        """
        Initialize secrets manager

        Args:
            storage_path: Path to secrets storage file
            encryption_key: Encryption key (uses env var if None)
        """
        self.storage_path = storage_path or ".secrets"
        self.encryption_key = encryption_key or os.getenv("SECRETS_KEY", "default-key")

        # In-memory secret store
        self._secrets: Dict[str, Secret] = {}

        # Load existing secrets
        self._load_secrets()

        # Metrics
        self.access_count: Dict[str, int] = {}

    def _get_encryption_key(self) -> bytes:
        """Get encryption key as bytes"""
        return self.encryption_key.encode()

    def _encrypt(self, value: str) -> str:
        """
        Simple encryption (base64 for demo)

        Note: In production, use proper encryption (e.g., Fernet, AWS KMS)

        Args:
            value: Value to encrypt

        Returns:
            Encrypted value
        """
        # Simple XOR encryption with key (for demo purposes)
        key_bytes = self._get_encryption_key()
        value_bytes = value.encode()

        encrypted = bytearray()
        for i, byte in enumerate(value_bytes):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])

        return base64.b64encode(encrypted).decode()

    def _decrypt(self, encrypted: str) -> str:
        """
        Simple decryption

        Args:
            encrypted: Encrypted value

        Returns:
            Decrypted value
        """
        # XOR decryption
        key_bytes = self._get_encryption_key()
        encrypted_bytes = base64.b64decode(encrypted)

        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key_bytes[i % len(key_bytes)])

        return decrypted.decode()

    def _load_secrets(self) -> None:
        """Load secrets from storage"""
        storage_file = Path(self.storage_path)

        if not storage_file.exists():
            return

        try:
            with open(storage_file, "r") as f:
                data = json.load(f)

            for name, secret_data in data.items():
                # Decrypt value
                encrypted_value = secret_data.get("value", "")
                decrypted_value = self._decrypt(encrypted_value)

                # Parse dates
                created_at = datetime.fromisoformat(secret_data["created_at"])
                expires_at = None
                if secret_data.get("expires_at"):
                    expires_at = datetime.fromisoformat(secret_data["expires_at"])

                # Create secret
                secret = Secret(
                    name=name,
                    value=decrypted_value,
                    created_at=created_at,
                    expires_at=expires_at,
                    metadata=secret_data.get("metadata", {}),
                )

                self._secrets[name] = secret

        except Exception as e:
            print(f"Warning: Failed to load secrets: {e}")

    def _save_secrets(self) -> None:
        """Save secrets to storage"""
        storage_file = Path(self.storage_path)
        storage_file.parent.mkdir(parents=True, exist_ok=True)

        data = {}
        for name, secret in self._secrets.items():
            # Encrypt value
            encrypted_value = self._encrypt(secret.value)

            data[name] = {
                "value": encrypted_value,
                "created_at": secret.created_at.isoformat(),
                "expires_at": secret.expires_at.isoformat() if secret.expires_at else None,
                "metadata": secret.metadata,
            }

        with open(storage_file, "w") as f:
            json.dump(data, f, indent=2)

    def set_secret(
        self,
        name: str,
        value: str,
        expires_in_days: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Store a secret

        Args:
            name: Secret name
            value: Secret value
            expires_in_days: Days until expiration
            metadata: Additional metadata
        """
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)

        secret = Secret(
            name=name,
            value=value,
            expires_at=expires_at,
            metadata=metadata or {},
        )

        self._secrets[name] = secret
        self._save_secrets()

    def get_secret(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a secret

        Args:
            name: Secret name
            default: Default value if not found

        Returns:
            Secret value or default
        """
        secret = self._secrets.get(name)

        if secret is None:
            return default

        # Check expiration
        if secret.is_expired():
            self.delete_secret(name)
            return default

        # Track access
        self.access_count[name] = self.access_count.get(name, 0) + 1

        return secret.value

    def delete_secret(self, name: str) -> None:
        """
        Delete a secret

        Args:
            name: Secret name
        """
        if name in self._secrets:
            del self._secrets[name]
            self._save_secrets()

    def list_secrets(self) -> list:
        """
        List all secret names

        Returns:
            List of secret names
        """
        return list(self._secrets.keys())

    def rotate_secret(
        self,
        name: str,
        new_value: str,
        expires_in_days: Optional[int] = None,
    ) -> None:
        """
        Rotate a secret

        Args:
            name: Secret name
            new_value: New secret value
            expires_in_days: Days until expiration
        """
        if name in self._secrets:
            old_secret = self._secrets[name]
            # Keep metadata
            self.set_secret(
                name,
                new_value,
                expires_in_days,
                metadata=old_secret.metadata,
            )

    def get_secret_info(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get secret metadata (without value)

        Args:
            name: Secret name

        Returns:
            Secret info dict
        """
        secret = self._secrets.get(name)
        if not secret:
            return None

        return {
            "name": secret.name,
            "created_at": secret.created_at.isoformat(),
            "expires_at": secret.expires_at.isoformat() if secret.expires_at else None,
            "is_expired": secret.is_expired(),
            "access_count": self.access_count.get(name, 0),
            "metadata": secret.metadata,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get secrets manager statistics"""
        expired = sum(1 for s in self._secrets.values() if s.is_expired())
        active = len(self._secrets) - expired

        return {
            "total_secrets": len(self._secrets),
            "active_secrets": active,
            "expired_secrets": expired,
            "most_accessed": sorted(
                self.access_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5] if self.access_count else [],
        }


# Utility functions

def load_from_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Load secret from environment variable

    Args:
        key: Environment variable name
        default: Default value

    Returns:
        Secret value
    """
    return os.getenv(key, default)


def create_api_key_hash(api_key: str) -> str:
    """
    Create hash of API key for logging (never log full keys!)

    Args:
        api_key: API key

    Returns:
        Hashed key
    """
    hash_obj = hashlib.sha256(api_key.encode())
    return hash_obj.hexdigest()[:16]
