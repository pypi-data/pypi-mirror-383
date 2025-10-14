from zsynctech_studio_sdk.utils import validate_id_format, is_valid_url
from contextvars import ContextVar
from appdirs import AppDirs
from httpx import Client
import os

APPS_DIR = AppDirs()
INSTANCE_ID: ContextVar[str] = ContextVar("instance_id", default=None)
SERVER: ContextVar[str] = ContextVar("server", default=None)
ENCRYPTION_KEY: ContextVar[str] = ContextVar("encryption_key", default=None)
SECRET_KEY: ContextVar[str] = ContextVar("secret_key", default=None)
CLIENT: ContextVar[object] = ContextVar("client", default=None)
SDK_DIR = os.path.join(APPS_DIR.user_data_dir, "zsynctech")


def config_client(server: str, secret_key: str, instance_id: str, encryption_key: str) -> Client:
    """Sets the credentials for the SDK.

    Args:
        server (str): The server URL.
        secret_key (str): The secret key.
        instance_id (str): The instance ID.
        encryption_key (str): The encryption key.

    Returns:
        Client: The HTTP client configured with the provided credentials.
    """
    try:
        validate_id_format(instance_id)
    except Exception:
        raise RuntimeError("Invalid instance ID")

    try:
        validate_id_format(secret_key)
    except Exception:
        raise RuntimeError("Invalid secret key")

    if not is_valid_url(server):
        raise RuntimeError("Invalid server url")

    INSTANCE_ID.set(instance_id)
    ENCRYPTION_KEY.set(encryption_key)
    SERVER.set(server.rstrip('/'))
    SECRET_KEY.set(secret_key)

    base_url = f"{SERVER.get()}/automation-gateway"

    if CLIENT.get() is None:
        client = Client(
            base_url=base_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {secret_key}::{instance_id}"
            }
        )
        CLIENT.set(client)
    
    return CLIENT.get()

def get_client() -> Client:
    """Gets the HTTP client.

    Raises:
        RuntimeError: If the client is not initialized.

    Returns:
        Client: The HTTP client.
    """
    if CLIENT.get() is None:
        raise RuntimeError("HTTP client not initialized. Call set_credentials() first.")
    return CLIENT.get()