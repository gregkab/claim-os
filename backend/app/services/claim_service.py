"""Claim service."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.claim import Claim
from app.models.user import User
from app.schemas.claim import ClaimCreate


def create_claim(db: Session, claim_data: ClaimCreate, owner_user_id: int) -> Claim:
    """Create a new claim."""
    claim = Claim(
        title=claim_data.title,
        reference_number=claim_data.reference_number,
        owner_user_id=owner_user_id
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def get_claim(db: Session, claim_id: int) -> Optional[Claim]:
    """Get a claim by ID."""
    return db.query(Claim).filter(Claim.id == claim_id).first()


def get_claims_by_owner(db: Session, owner_user_id: int) -> List[Claim]:
    """Get all claims for a user."""
    return db.query(Claim).filter(Claim.owner_user_id == owner_user_id).all()


def get_claim_with_owner_check(db: Session, claim_id: int, owner_user_id: int) -> Optional[Claim]:
    """Get a claim by ID and verify ownership."""
    claim = get_claim(db, claim_id)
    if claim and claim.owner_user_id == owner_user_id:
        return claim
    return None

