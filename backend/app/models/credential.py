from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UserCredential(Base):
    __tablename__ = "user_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False) # notion, jira, email
    encrypted_data = Column(String, nullable=False) # JSON string encrypted
    
    user = relationship("User", back_populates="credentials")

# Update User model to include relationship
from app.models.user import User
User.credentials = relationship("UserCredential", back_populates="user")
