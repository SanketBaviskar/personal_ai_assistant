import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.credential import UserCredential
from app.core.encryption import encrypt_value, decrypt_value

class CredentialService:
    def store_credentials(self, db: Session, user_id: int, provider: str, data: Dict[str, Any]) -> UserCredential:
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
        credential = db.query(UserCredential).filter(
            UserCredential.user_id == user_id,
            UserCredential.provider == provider
        ).first()

        if not credential:
            return None
        
        decrypted = decrypt_value(credential.encrypted_data)
        return json.loads(decrypted)

credential_service = CredentialService()
