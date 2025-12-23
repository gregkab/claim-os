"""Artifacts router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.artifact import Artifact
from app.services import claim_service, artifact_service

router = APIRouter(prefix="/claims/{claim_id}/artifacts", tags=["artifacts"])


@router.get("", response_model=List[Artifact])
def list_artifacts(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all artifacts for a claim."""
    # Verify claim exists and user owns it
    claim = claim_service.get_claim_with_owner_check(db, claim_id, current_user.id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    artifacts = artifact_service.get_artifacts_by_claim(db, claim_id)
    return artifacts


@router.get("/{artifact_id}", response_model=Artifact)
def get_artifact(
    claim_id: int,
    artifact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get an artifact by ID."""
    # Verify claim exists and user owns it
    claim = claim_service.get_claim_with_owner_check(db, claim_id, current_user.id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    artifact = artifact_service.get_artifact(db, artifact_id)
    if not artifact or artifact.claim_id != claim_id:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return artifact

