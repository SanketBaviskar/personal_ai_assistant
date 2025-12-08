from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.db.base_class import Base

class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("document.id", ondelete="CASCADE"), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384)) # BGE-small-en-v1.5 dimension
    
    source_app = Column(String(50), nullable=False) # e.g. "google_drive"
    source_url = Column(Text, nullable=True)
    
    metadata_ = Column("metadata", JSONB, server_default='{}') # Rename to avoid conflict with Base.metadata? No, usually fine, but 'metadata' is reserved in SQLAlchemy. Mapped column name.
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships (Optional, but good for consistency)
    user = relationship("User")
    document = relationship("Document")

    __table_args__ = (
        Index(
            'document_embeddings_embedding_idx',
            'embedding',
            postgresql_using='ivfflat',
            postgresql_ops={'embedding': 'vector_cosine_ops'},
            postgresql_with={'lists': 100}
        ),
        Index('document_embeddings_source_idx', 'source_app', 'user_id'),
        Index('document_embeddings_user_id_idx', 'user_id'),
    )
