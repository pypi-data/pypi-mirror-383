from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
from typing import Optional
import base64
import re

ALGORITHM = "AES-256-GCM"

def get_utc_now(extra_seconds: Optional[int] = 0) -> str:
    """
    Get the current date and time in UTC format as an ISO string.

    Returns:
        str: Current UTC datetime in ISO format with 'Z' suffix (e.g., '2024-01-15T10:30:45.123Z')
    """
    # return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    now = datetime.now(timezone.utc) + timedelta(seconds=extra_seconds)
    return now.isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def decrypt(ciphertext: str, encryption_key: str) -> str:
    """Decrypts a Base64-encoded ciphertext string using AES-256-GCM.

    Args:
        ciphertext (str): The Base64-encoded string containing IV, authentication tag, and ciphertext.

    Returns:
        str: The decrypted plaintext string.
    """
    key: bytes = bytes.fromhex(encryption_key)
    data: bytes = base64.b64decode(ciphertext)

    iv: bytes = data[:12]
    auth_tag: bytes = data[12:28]
    encrypted: bytes = data[28:]

    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, auth_tag),
        backend=default_backend()
    ).decryptor()

    decrypted: bytes = decryptor.update(encrypted) + decryptor.finalize()
    return decrypted.decode("utf-8")

def validate_id_format(value: str):
    if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', value):
        raise ValueError('ID deve ser um UUID válido')
    version = int(value[14], 16)
    if version != 7:
        raise ValueError('ID deve ser um UUID7 válido')
    return value

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
    except ValueError:
        return False

    return all([result.scheme in ("http", "https"), result.netloc])