"""
Service for user management.
Handles user creation, retrieval, and authentication.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models import user as models
from app.schemas import user as schemas
from app.core import security

class UserService:
    """
    Service class for User operations.
    """
    def get_by_email(self, db: Session, email: str) -> Optional[models.User]:
        """
        Retrieves a user by email.

        Args:
            db (Session): Database session.
            email (str): Email address to search for.

        Returns:
            Optional[models.User]: The user object if found, else None.
        """
        return db.query(models.User).filter(models.User.email == email).first()

    def create(self, db: Session, obj_in: schemas.UserCreate) -> models.User:
        """
        Creates a new user.

        Args:
            db (Session): Database session.
            obj_in (schemas.UserCreate): User creation data.

        Returns:
            models.User: The created user object.
        """
        db_obj = models.User(
            email=obj_in.email,
            hashed_password=security.get_password_hash(obj_in.password),
            is_active=True,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, email: str, password: str) -> Optional[models.User]:
        """
        Authenticates a user by email and password.

        Args:
            db (Session): Database session.
            email (str): User's email.
            password (str): User's password.

        Returns:
            Optional[models.User]: The authenticated user object if successful, else None.
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not security.verify_password(password, user.hashed_password):
            return None
        return user

user_service = UserService()
