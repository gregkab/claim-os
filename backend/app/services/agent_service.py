"""Agent service - processes natural language commands."""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.claim import Claim
from app.models.file import File
from app.models.artifact import Artifact
from app.services.file_service import read_file_content, get_files_by_claim
from app.services.artifact_service import get_artifact_by_type, get_artifact_current_content
from app.services.diff_service import compute_unified_diff
from app.schemas.agent import Proposal


def process_command(db: Session, claim_id: int, user_message: str) -> List[Proposal]:
    """
    Process a natural language command and return proposals.
    
    This is a mock implementation that uses simple keyword matching.
    TODO: Replace with LLM-based command parsing and execution.
    """
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise ValueError(f"Claim {claim_id} not found")
    
    message_lower = user_message.lower()
    proposals = []
    
    # Load all claim files and their contents
    files = get_files_by_claim(db, claim_id)
    file_contents = {}
    for file in files:
        try:
            file_contents[file.id] = {
                'file': file,
                'content': read_file_content(file)
            }
        except Exception as e:
            # Skip files that can't be read
            print(f"Warning: Could not read file {file.id}: {e}")
            continue
    
    # Mock command: "create summary" or "create a summary"
    if 'create' in message_lower and 'summary' in message_lower:
        # Check if summary already exists
        existing_summary = get_artifact_by_type(db, claim_id, "summary")
        old_content = ""
        
        if existing_summary:
            old_content = get_artifact_current_content(db, existing_summary.id) or ""
        
        # Generate summary from file contents
        new_content = generate_summary_from_files(file_contents)
        
        # Compute diff
        diff = compute_unified_diff(old_content, new_content, "current_summary", "proposed_summary")
        
        proposals.append(Proposal(
            type="artifact",
            target_id=existing_summary.id if existing_summary else None,
            target_name="summary",
            old_content=old_content,
            new_content=new_content,
            diff=diff
        ))
    
    # Mock command: "update file" or "modify file"
    elif ('update' in message_lower or 'modify' in message_lower) and 'file' in message_lower:
        # For MVP, update the first text file found
        # TODO: Parse which file to update from the message
        # Note: PDFs can be read for summaries, but only text files can be updated
        # (we can't write text back to PDFs or other binary files)
        for file_id, file_data in file_contents.items():
            file = file_data['file']
            # Only text files can be updated (PDFs and images are read-only for updates)
            if file.mime_type and file.mime_type.startswith('text/'):
                old_content = file_data['content']
                # Mock: add a note at the end
                new_content = old_content + "\n\n[Agent Note: File updated based on claim analysis]"
                
                diff = compute_unified_diff(old_content, new_content, file.filename, file.filename)
                
                proposals.append(Proposal(
                    type="file",
                    target_id=file.id,
                    target_name=file.filename,
                    old_content=old_content,
                    new_content=new_content,
                    diff=diff
                ))
                break  # Only update first file for MVP
    
    # Default: if no specific command matched, try to create summary
    elif not proposals:
        existing_summary = get_artifact_by_type(db, claim_id, "summary")
        old_content = get_artifact_current_content(db, existing_summary.id) if existing_summary else ""
        new_content = generate_summary_from_files(file_contents)
        diff = compute_unified_diff(old_content, new_content, "current_summary", "proposed_summary")
        
        proposals.append(Proposal(
            type="artifact",
            target_id=existing_summary.id if existing_summary else None,
            target_name="summary",
            old_content=old_content,
            new_content=new_content,
            diff=diff
        ))
    
    return proposals


def generate_summary_from_files(file_contents: dict) -> str:
    """
    Generate a summary from file contents.
    This is a mock implementation.
    TODO: Replace with LLM-based summary generation.
    """
    if not file_contents:
        return "No files available to generate summary from."
    
    summary_parts = ["# Claim Summary\n\n"]
    summary_parts.append("Generated from the following files:\n\n")
    
    for file_id, file_data in file_contents.items():
        file = file_data['file']
        content = file_data['content']
        summary_parts.append(f"## {file.filename}\n\n")
        # Take first 500 characters as preview
        preview = content[:500] + "..." if len(content) > 500 else content
        summary_parts.append(f"{preview}\n\n")
    
    summary_parts.append("\n---\n")
    summary_parts.append("*This summary was generated automatically. Review and edit as needed.*")
    
    return ''.join(summary_parts)

