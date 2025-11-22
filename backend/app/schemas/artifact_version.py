"""Artifact version schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ArtifactVersionBase(BaseModel):
    """Base artifact version schema."""
    content: str
    version_metadata: Optional[dict] = None


class ArtifactVersionCreate(ArtifactVersionBase):
    """Schema for creating an artifact version."""
    pass


class ArtifactVersion(ArtifactVersionBase):
    """Artifact version response schema."""
    id: int
    artifact_id: int
    created_at: datetime
    created_by_user_id: Optional[int] = None

    class Config:
        from_attributes = True

