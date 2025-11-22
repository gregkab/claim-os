"""Artifact version model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ArtifactVersion(Base):
    """Artifact version model - tracks version history of artifacts."""
    
    __tablename__ = "artifact_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    artifact_id = Column(Integer, ForeignKey("artifacts.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)  # Artifact content (text, markdown, or JSON string)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable if created by agent
    version_metadata = Column(JSON, nullable=True)  # JSONB: model info, prompt, etc. (renamed from 'metadata' to avoid SQLAlchemy reserved name)
    
    # Relationships
    artifact = relationship("Artifact", back_populates="versions", foreign_keys=[artifact_id])
    created_by = relationship("User")

