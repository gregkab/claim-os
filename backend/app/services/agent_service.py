"""Agent service - processes natural language commands."""
from sqlalchemy.orm import Session
from typing import List, Optional
from openai import OpenAI
from app.models.claim import Claim
from app.models.file import File
from app.models.artifact import Artifact
from app.services.file_service import read_file_content, get_files_by_claim
from app.services.artifact_service import get_artifact_by_type, get_artifact_current_content
from app.services.diff_service import compute_unified_diff
from app.schemas.agent import Proposal
from app.core.config import settings


def generate_summary_proposal(db: Session, claim_id: int) -> List[Proposal]:
    """
    Generate a summary proposal from claim files.
    This is the dedicated function for the Generate Summary button.
    """
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise ValueError(f"Claim {claim_id} not found")
    
    # Load all claim files and their contents
    files = get_files_by_claim(db, claim_id)
    file_contents = {}
    for file in files:
        # Use stored extracted_text if available, otherwise try to read from storage
        content = None
        if file.extracted_text:
            content = file.extracted_text
        else:
            try:
                content = read_file_content(file)
            except Exception as e:
                # Skip files that can't be read
                print(f"Warning: Could not read file {file.id}: {e}")
                continue
        
        if content:
            file_contents[file.id] = {
                'file': file,
                'content': content
            }
    
    # Check if summary already exists
    existing_summary = get_artifact_by_type(db, claim_id, "summary")
    old_content = ""
    
    if existing_summary:
        old_content = get_artifact_current_content(db, existing_summary.id) or ""
    
    # Generate summary from file contents
    new_content = generate_summary_from_files(file_contents, old_content if old_content else None)
    
    # Compute diff
    diff = compute_unified_diff(old_content, new_content, "current_summary", "proposed_summary")
    
    return [Proposal(
        type="artifact",
        target_id=existing_summary.id if existing_summary else None,
        target_name="summary",
        old_content=old_content,
        new_content=new_content,
        diff=diff
    )]


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
        # Use stored extracted_text if available, otherwise try to read from storage
        content = None
        if file.extracted_text:
            content = file.extracted_text
        else:
            try:
                content = read_file_content(file)
            except Exception as e:
                # Skip files that can't be read
                print(f"Warning: Could not read file {file.id}: {e}")
                continue
        
        if content:
            file_contents[file.id] = {
                'file': file,
                'content': content
            }
    
    # Mock command: "create summary" or "create a summary"
    if 'create' in message_lower and 'summary' in message_lower:
        # Check if summary already exists
        existing_summary = get_artifact_by_type(db, claim_id, "summary")
        old_content = ""
        
        if existing_summary:
            old_content = get_artifact_current_content(db, existing_summary.id) or ""
        
        # Generate summary from file contents
        new_content = generate_summary_from_files(file_contents, old_content if old_content else None)
        
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


def generate_summary_from_files(file_contents: dict, existing_summary: Optional[str] = None) -> str:
    """
    Generate a summary from file contents using OpenAI.
    Falls back to simple preview if OpenAI is not available or fails.
    """
    if not file_contents:
        return "No files available to generate summary from."
    
    # Try OpenAI if API key is configured
    if settings.OPENAI_API_KEY:
        try:
            print(f"Using OpenAI API to generate summary (key present: {bool(settings.OPENAI_API_KEY)})")
            result = _generate_summary_with_openai(file_contents, existing_summary)
            print(f"OpenAI summary generated successfully, length: {len(result)}")
            return result
        except Exception as e:
            print(f"OpenAI API error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            # Fall through to simple summary
    else:
        print("OpenAI API key not configured, using simple summary")
    
    # Fallback: simple preview-based summary
    return _generate_simple_summary(file_contents)


def _generate_summary_with_openai(file_contents: dict, existing_summary: Optional[str] = None) -> str:
    """Generate summary using OpenAI API."""
    print(f"Initializing OpenAI client...")
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Build context from all files
    file_sections = []
    total_chars = 0
    max_chars = 100000  # Rough limit to stay within token budget
    
    print(f"Processing {len(file_contents)} files for summary generation...")
    for file_id, file_data in file_contents.items():
        file = file_data['file']
        content = file_data['content']
        
        # Truncate if needed, but try to include full content
        if total_chars + len(content) > max_chars:
            remaining = max_chars - total_chars
            if remaining > 1000:  # Only include if we have meaningful space
                content = content[:remaining] + "\n\n[Content truncated due to length...]"
            else:
                break
        
        file_sections.append(f"=== File: {file.filename} ===\n{content}\n")
        total_chars += len(content)
    
    files_text = "\n\n".join(file_sections)
    print(f"Total content length: {len(files_text)} characters")
    
    # Build prompt
    system_prompt = """You are an expert at analyzing claim documents and creating comprehensive summaries.
Your task is to create a clear, well-structured summary that captures:
- Key facts and details from the documents
- Important dates, amounts, parties, and other relevant information
- The nature and context of the claim
- Any notable patterns or important points

Format your response as a markdown document with clear sections and headings.
Be thorough but concise. Focus on actionable information."""
    
    user_prompt = f"""Please analyze the following claim documents and create a comprehensive summary.

Documents:
{files_text}

"""
    
    if existing_summary:
        user_prompt += f"""Previous summary (update this if creating a new version):
{existing_summary}

Please create an updated summary that incorporates any new information from the documents above."""
    else:
        user_prompt += "Please create a new summary based on the documents above."
    
    print(f"Calling OpenAI API with model gpt-4o-mini...")
    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using cost-effective model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent, factual summaries
            max_tokens=2000  # Reasonable limit for summaries
        )
        
        print(f"OpenAI API response received")
        summary = response.choices[0].message.content.strip()
        print(f"Summary length: {len(summary)} characters")
        
        # Ensure it starts with a heading
        if not summary.startswith("#"):
            summary = "# Claim Summary\n\n" + summary
        
        return summary
    except Exception as e:
        print(f"Error in OpenAI API call: {type(e).__name__}: {e}")
        raise


def _generate_simple_summary(file_contents: dict) -> str:
    """Fallback: Generate a simple preview-based summary."""
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

