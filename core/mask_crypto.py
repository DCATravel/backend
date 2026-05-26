# Used to conceal LLM access
import base64
import hashlib
import os

from cryptography.fernet import Fernet

key_prefix = "mgxkey-"
secret_key = os.environ.get("MASK_KEY")

if not secret_key:
    raise ValueError("MASK_KEY environment variable is required")


def _derive_fernet_key(key_material: str) -> bytes:
    """Derive a valid Fernet key from arbitrary string using SHA-256 and urlsafe base64."""
    digest = hashlib.sha256(key_material.encode("utf-8")).digest()  # 32 bytes
    return base64.urlsafe_b64encode(digest)


def _get_fernet(key_str: str) -> Fernet:
    key = _derive_fernet_key(key_str)
    return Fernet(key)


def encrypt_text(plain: str) -> str:
    # Usa directamente secret_key ya que fue validado al inicio del módulo
    f = _get_fernet(secret_key)
    return key_prefix + f.encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_text(token: str) -> str:
    f = _get_fernet(secret_key)
    token = token.removeprefix(key_prefix)
    return f.decrypt(token.encode("utf-8")).decode("utf-8")
