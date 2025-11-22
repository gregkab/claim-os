"""User schemas."""
from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class User(UserBase):
    """User response schema."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

