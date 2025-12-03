"""
Service for managing user credentials.
Handles encryption, storage, and retrieval of sensitive user data.
"""
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.credential import UserCredential
from app.core.encryption import encrypt_value, decrypt_value

class CredentialService:
    """
    Service class for handling user credentials securely.
    """
    def store_credentials(self, db: Session, user_id: int, provider: str, data: Dict[str, Any]) -> UserCredential:
        """
        Encrypts and stores user credentials for a specific provider.

        Args:
            db (Session): Database session.
            user_id (int): ID of the user.
            provider (str): Name of the credential provider (e.g., 'google').
            data (Dict[str, Any]): Dictionary containing the credential data.

        Returns:
            UserCredential: The created or updated credential object.
        """
        json_data = json.dumps(data)
        encrypted = encrypt_value(json_data)
        
        credential = db.query(UserCredential).filter(
            UserCredential.user_id == user_id,
            UserCredential.provider == provider
        ).first()

        if credential:
            credential.encrypted_data = encrypted
        else:
            credential = UserCredential(
                user_id=user_id,
                provider=provider,
                encrypted_data=encrypted
            )
            db.add(credential)
        
        db.commit()
        db.refresh(credential)
        return credential

    def get_credentials(self, db: Session, user_id: int, provider: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves and decrypts user credentials for a specific provider.

        Args:
            db (Session): Database session.
            user_id (int): ID of the user.
            provider (str): Name of the credential provider.

        Returns:
            Optional[Dict[str, Any]]: Decrypted credential data as a dictionary, or None if not found.
        """
        credential = db.query(UserCredential).filter(
            UserCredential.user_id == user_id,
            UserCredential.provider == provider
        ).first()

        if not credential:
            return None
        
        decrypted = decrypt_value(credential.encrypted_data)
        return json.loads(decrypted)

credential_service = CredentialService()
