"""Claim schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ClaimBase(BaseModel):
    """Base claim schema."""
    title: str
    reference_number: Optional[str] = None


class ClaimCreate(ClaimBase):
    """Schema for creating a claim."""
    pass


class Claim(ClaimBase):
    """Claim response schema."""
    id: int
    owner_user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

