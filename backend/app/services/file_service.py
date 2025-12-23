"""File service."""
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import PyPDF2
import pdfplumber
from io import BytesIO
from app.models.file import File
from app.models.claim import Claim
from app.storage.local_storage import storage


def extract_text_from_bytes(file_bytes: bytes, mime_type: Optional[str], filename: str) -> Optional[str]:
    """
    Extract text content from file bytes.
    
    For text files: decodes directly.
    For PDFs: extracts text using pdfplumber (with fallback to PyPDF2).
    Returns None if extraction fails or file type is not supported.
    """
    # Handle text files
    if mime_type and mime_type.startswith('text/'):
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin-1', 'cp1252']:
                try:
                    return file_bytes.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return None
    
    # Handle PDF files
    if mime_type == 'application/pdf' or filename.lower().endswith('.pdf'):
        try:
            # Try pdfplumber first (better text extraction)
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                return '\n\n'.join(text_parts) if text_parts else None
        except Exception:
            # Fallback to PyPDF2
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
                text_parts = []
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                return '\n\n'.join(text_parts) if text_parts else None
            except Exception:
                return None
    
    # For other file types, try to decode as text
    try:
        return file_bytes.decode('utf-8', errors='replace')
    except Exception:
        return None


def read_file_content(file: File) -> str:
    """
    Read and extract text content from a file.
    
    First tries to use stored extracted_text if available.
    Otherwise, reads from storage and extracts text.
    """
    # If we have stored extracted text, use it
    if file.extracted_text:
        return file.extracted_text
    
    # Otherwise, extract from storage (for backward compatibility)
    file_bytes = storage.read_file(file.storage_path)
    extracted = extract_text_from_bytes(file_bytes, file.mime_type, file.filename)
    
    if extracted is None:
        raise ValueError(f"Could not extract text from file: {file.filename}")
    
    return extracted


def update_file_content(file: File, new_content: str) -> None:
    """
    Update file content in storage.
    For text files, writes the new content directly.
    TODO: Handle binary files and other formats.
    """
    # For now, assume we're updating text files
    storage.write_text_file(new_content, file.storage_path)


def get_files_by_claim(db: Session, claim_id: int) -> List[File]:
    """Get all files for a claim."""
    return db.query(File).filter(File.claim_id == claim_id).all()


def get_file(db: Session, file_id: int) -> Optional[File]:
    """Get a file by ID."""
    return db.query(File).filter(File.id == file_id).first()


def get_file_with_claim_check(db: Session, file_id: int, claim_id: int) -> Optional[File]:
    """Get a file by ID and verify it belongs to the claim."""
    file = get_file(db, file_id)
    if file and file.claim_id == claim_id:
        return file
    return None


def delete_file(db: Session, file: File) -> None:
    """Delete a file from storage and database."""
    # Delete from storage
    try:
        storage.delete_file(file.storage_path)
    except FileNotFoundError:
        # File doesn't exist in storage, continue with DB deletion
        pass
    
    # Delete from database
    db.delete(file)
    db.commit()

