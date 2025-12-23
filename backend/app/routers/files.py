"""Files router."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.file import File
from app.schemas.file import File as FileSchema
from app.services import claim_service, file_service
from app.storage.local_storage import storage

router = APIRouter(prefix="/claims/{claim_id}/files", tags=["files"])


@router.post("", response_model=FileSchema, status_code=201)
def upload_file(
    claim_id: int,
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a file to a claim."""
    # Verify claim exists and user owns it
    claim = claim_service.get_claim_with_owner_check(db, claim_id, current_user.id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Generate storage path
    file_id = uuid.uuid4().hex[:8]
    storage_path = f"claims/{claim_id}/{file_id}_{file.filename}"
    
    # Read file content
    file_content = file.file.read()
    
    # Save to storage
    storage.save_file(file_content, storage_path)
    
    # Create file record
    db_file = File(
        claim_id=claim_id,
        filename=file.filename,
        storage_path=storage_path,
        mime_type=file.content_type,
        size_bytes=len(file_content)
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    return db_file


@router.get("", response_model=List[FileSchema])
def list_files(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all files for a claim."""
    # Verify claim exists and user owns it
    claim = claim_service.get_claim_with_owner_check(db, claim_id, current_user.id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    files = file_service.get_files_by_claim(db, claim_id)
    return files


@router.get("/{file_id}", response_model=FileSchema)
def get_file(
    claim_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a file by ID."""
    # Verify claim exists and user owns it
    claim = claim_service.get_claim_with_owner_check(db, claim_id, current_user.id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    file = file_service.get_file_with_claim_check(db, file_id, claim_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file


@router.delete("/{file_id}")
def delete_file(
    claim_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a file from a claim."""
    # Verify claim exists and user owns it
    claim = claim_service.get_claim_with_owner_check(db, claim_id, current_user.id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    file = file_service.get_file_with_claim_check(db, file_id, claim_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        file_service.delete_file(db, file)
        return {"status": "deleted", "file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

