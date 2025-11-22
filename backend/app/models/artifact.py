"""Artifact model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Artifact(Base):
    """Artifact model - represents generated artifacts (summary, letters, etc.)."""
    
    __tablename__ = "artifacts"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # e.g., "summary", "letter", "note"
    title = Column(String, nullable=False)
    current_version_id = Column(Integer, ForeignKey("artifact_versions.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    claim = relationship("Claim", back_populates="artifacts")
    versions = relationship("ArtifactVersion", back_populates="artifact", foreign_keys="ArtifactVersion.artifact_id", cascade="all, delete-orphan")
    current_version = relationship("ArtifactVersion", foreign_keys=[current_version_id], post_update=True)

