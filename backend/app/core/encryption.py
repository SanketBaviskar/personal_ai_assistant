from cryptography.fernet import Fernet
from app.core.config import settings

# In a real app, this key should be loaded from a secure environment variable
# and NOT generated on the fly if persistence is needed across restarts.
# For this MVP, we'll assume settings.SECRET_KEY is used to derive or is the key.
# However, Fernet requires a 32 url-safe base64-encoded bytes. 
# We will generate one for now if not present, but for production, use a fixed key.

# For simplicity in this MVP, we'll generate a key if one isn't provided, 
# but this means data is lost on restart if we don't persist it.
# TODO: Move to config.
ENCRYPTION_KEY = Fernet.generate_key() 
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_value(value: str) -> str:
    if not value:
        return ""
    return cipher_suite.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    if not value:
        return ""
    return cipher_suite.decrypt(value.encode()).decode()
