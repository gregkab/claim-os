"""Agent router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.agent import AgentChatRequest, AgentChatResponse, AgentAcceptRequest, Proposal
from app.services import claim_service, agent_service, file_service, artifact_service

router = APIRouter(prefix="/claims/{claim_id}/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(
    claim_id: int,
    request: AgentChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process an agent command and return proposals."""
    # Verify claim exists and user owns it
    claim = claim_service.get_claim_with_owner_check(db, claim_id, current_user.id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    try:
        proposals = agent_service.process_command(db, claim_id, request.message)
        return AgentChatResponse(proposals=proposals)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing command: {str(e)}")


@router.post("/accept")
def accept_proposal(
    claim_id: int,
    request: AgentAcceptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accept a proposal (file or artifact change)."""
    try:
        # Verify claim exists and user owns it
        claim = claim_service.get_claim_with_owner_check(db, claim_id, current_user.id)
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        proposal = request.proposal
        
        if proposal.type == "file":
            # Update file content
            if not proposal.target_id:
                raise HTTPException(status_code=400, detail="File ID is required for file proposals")
            
            file = file_service.get_file_with_claim_check(db, proposal.target_id, claim_id)
            if not file:
                raise HTTPException(status_code=404, detail="File not found")
            
            # Check if file is a text file (can't update binary files like PDFs or images)
            # Note: PDFs can be read for summaries, but can't be updated by writing text back
            if not file.mime_type or not file.mime_type.startswith('text/'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot update '{file.filename}'. Only text files can be updated. PDFs and images can be read but not modified."
                )
            
            try:
                file_service.update_file_content(file, proposal.new_content)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to update file: {str(e)}")
            
            return {"status": "accepted", "type": "file", "file_id": file.id}
        
        elif proposal.type == "artifact":
            # Create or update artifact
            if proposal.target_id:
                # Update existing artifact
                artifact = artifact_service.get_artifact(db, proposal.target_id)
                if not artifact or artifact.claim_id != claim_id:
                    raise HTTPException(status_code=404, detail="Artifact not found")
                
                artifact_service.create_artifact_version(
                    db,
                    artifact.id,
                    proposal.new_content,
                    created_by_user_id=current_user.id,
                    version_metadata={"source": "agent", "command": "user_request"}
                )
                return {"status": "accepted", "type": "artifact", "artifact_id": artifact.id}
            else:
                # Create new artifact (e.g., summary)
                from app.schemas.artifact import ArtifactCreate
                artifact_data = ArtifactCreate(type="summary", title="Summary")
                artifact = artifact_service.create_artifact(db, artifact_data, claim_id)
                
                artifact_service.create_artifact_version(
                    db,
                    artifact.id,
                    proposal.new_content,
                    created_by_user_id=current_user.id,
                    version_metadata={"source": "agent", "command": "user_request"}
                )
                return {"status": "accepted", "type": "artifact", "artifact_id": artifact.id}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown proposal type: {proposal.type}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accepting proposal: {str(e)}")

