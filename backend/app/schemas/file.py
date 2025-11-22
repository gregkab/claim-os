"""File schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FileBase(BaseModel):
    """Base file schema."""
    filename: str
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None


class FileCreate(FileBase):
    """Schema for creating a file."""
    storage_path: str


class File(FileBase):
    """File response schema."""
    id: int
    claim_id: int
    storage_path: str
    created_at: datetime

    class Config:
        from_attributes = True

