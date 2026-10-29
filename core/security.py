import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def encrypt_secret(secret_text: str) -> str:
    """
    Encrypt sensitive string (e.g., database password) using Fernet symmetric encryption.
    Falls back to original string if no key is configured or cryptography is unavailable.
    """
    if not secret_text:
        return ""

    key = getattr(settings, "TENANT_DB_ENCRYPTION_KEY", None)
    if not key:
        return secret_text

    try:
        from cryptography.fernet import Fernet

        key_bytes = key.encode() if isinstance(key, str) else key
        f = Fernet(key_bytes)
        return f.encrypt(secret_text.encode("utf-8")).decode("utf-8")
    except Exception as exc:
        logger.warning("Encryption failed, falling back to plaintext: %s", exc)
        return secret_text


def decrypt_secret(cipher_text: str) -> str:
    """
    Decrypt sensitive string using Fernet.
    If decryption fails (e.g., legacy unencrypted passwords), returns cipher_text as-is.
    """
    if not cipher_text:
        return ""

    key = getattr(settings, "TENANT_DB_ENCRYPTION_KEY", None)
    if not key:
        return cipher_text

    try:
        from cryptography.fernet import Fernet, InvalidToken

        key_bytes = key.encode() if isinstance(key, str) else key
        f = Fernet(key_bytes)
        return f.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
    except Exception:
        # Expected fallback if password is still stored as plaintext
        return cipher_text

