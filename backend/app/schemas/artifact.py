"""Artifact schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Import here to avoid circular import, but needed for runtime
from app.schemas.artifact_version import ArtifactVersion


class ArtifactBase(BaseModel):
    """Base artifact schema."""
    type: str
    title: str


class ArtifactCreate(ArtifactBase):
    """Schema for creating an artifact."""
    pass


class Artifact(ArtifactBase):
    """Artifact response schema."""
    id: int
    claim_id: int
    current_version_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    current_version: Optional[ArtifactVersion] = None

    class Config:
        from_attributes = True

