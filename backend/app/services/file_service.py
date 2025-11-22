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


def read_file_content(file: File) -> str:
    """
    Read and extract text content from a file.
    
    For text files: reads directly.
    For PDFs: extracts text using pdfplumber (with fallback to PyPDF2).
    TODO: Add support for more file types (Word docs, etc.)
    """
    file_bytes = storage.read_file(file.storage_path)
    
    # Handle text files
    if file.mime_type and file.mime_type.startswith('text/'):
        try:
            return file_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Try other encodings
            for encoding in ['latin-1', 'cp1252']:
                try:
                    return file_bytes.decode(encoding)
                except UnicodeDecodeError:
                    continue
            raise ValueError(f"Could not decode text file: {file.filename}")
    
    # Handle PDF files
    if file.mime_type == 'application/pdf' or file.filename.lower().endswith('.pdf'):
        try:
            # Try pdfplumber first (better text extraction)
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                return '\n\n'.join(text_parts)
        except Exception:
            # Fallback to PyPDF2
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
                text_parts = []
                for page in pdf_reader.pages:
                    text_parts.append(page.extract_text())
                return '\n\n'.join(text_parts)
            except Exception as e:
                raise ValueError(f"Could not extract text from PDF: {file.filename}. Error: {e}")
    
    # For other file types, try to decode as text
    try:
        return file_bytes.decode('utf-8', errors='replace')
    except Exception:
        raise ValueError(f"Unsupported file type for text extraction: {file.mime_type or 'unknown'}")


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

