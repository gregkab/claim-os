"""Artifact service."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.artifact import Artifact
from app.models.artifact_version import ArtifactVersion
from app.schemas.artifact import ArtifactCreate


def create_artifact(db: Session, artifact_data: ArtifactCreate, claim_id: int) -> Artifact:
    """Create a new artifact."""
    artifact = Artifact(
        claim_id=claim_id,
        type=artifact_data.type,
        title=artifact_data.title
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


def get_artifact(db: Session, artifact_id: int) -> Optional[Artifact]:
    """Get an artifact by ID."""
    from sqlalchemy.orm import joinedload
    return db.query(Artifact).options(
        joinedload(Artifact.current_version)
    ).filter(Artifact.id == artifact_id).first()


def get_artifacts_by_claim(db: Session, claim_id: int) -> List[Artifact]:
    """Get all artifacts for a claim."""
    from sqlalchemy.orm import joinedload
    return db.query(Artifact).options(
        joinedload(Artifact.current_version)
    ).filter(Artifact.claim_id == claim_id).all()


def get_artifact_by_type(db: Session, claim_id: int, artifact_type: str) -> Optional[Artifact]:
    """Get an artifact by claim ID and type."""
    return db.query(Artifact).filter(
        Artifact.claim_id == claim_id,
        Artifact.type == artifact_type
    ).first()


def create_artifact_version(
    db: Session,
    artifact_id: int,
    content: str,
    created_by_user_id: Optional[int] = None,
    version_metadata: Optional[dict] = None
) -> ArtifactVersion:
    """Create a new artifact version and update artifact's current_version_id."""
    version = ArtifactVersion(
        artifact_id=artifact_id,
        content=content,
        created_by_user_id=created_by_user_id,
        version_metadata=version_metadata
    )
    db.add(version)
    db.flush()  # Flush to get version.id
    
    # Update artifact's current_version_id
    artifact = get_artifact(db, artifact_id)
    if artifact:
        artifact.current_version_id = version.id
        db.commit()
        db.refresh(version)
        db.refresh(artifact)
    
    return version


def get_artifact_current_content(db: Session, artifact_id: int) -> Optional[str]:
    """Get the current content of an artifact."""
    artifact = get_artifact(db, artifact_id)
    if artifact and artifact.current_version:
        return artifact.current_version.content
    return None

