from cryptography.fernet import Fernet
from app.core.config import settings

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
