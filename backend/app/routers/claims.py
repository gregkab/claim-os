"""Claims router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.claim import Claim, ClaimCreate
from app.services import claim_service

router = APIRouter(prefix="/claims", tags=["claims"])


@router.post("", response_model=Claim, status_code=201)
def create_claim(
    claim_data: ClaimCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new claim."""
    claim = claim_service.create_claim(db, claim_data, current_user.id)
    return claim


@router.get("", response_model=List[Claim])
def list_claims(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all claims for the current user."""
    claims = claim_service.get_claims_by_owner(db, current_user.id)
    return claims


@router.get("/{claim_id}", response_model=Claim)
def get_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a claim by ID."""
    claim = claim_service.get_claim_with_owner_check(db, claim_id, current_user.id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim

