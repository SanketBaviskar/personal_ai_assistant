from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Document(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    status = Column(String, default="pending") # pending, processing, completed, failed
    error_message = Column(String, nullable=True)
    
    # New columns from checklist
    provider = Column(String, nullable=True) # google_drive, notion, jira
    external_id = Column(String, nullable=True) # File ID in source system
    source_url = Column(String, nullable=True)
    content_hash = Column(String, nullable=True) # For duplicate detection
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    
    owner = relationship("User", back_populates="documents")
