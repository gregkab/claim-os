"""Agent chat schemas."""
from pydantic import BaseModel
from typing import List, Literal, Optional


class AgentChatRequest(BaseModel):
    """Request schema for agent chat."""
    message: str


class Proposal(BaseModel):
    """A proposal for a file or artifact change."""
    type: Literal["file", "artifact"]
    target_id: Optional[int] = None  # file_id or artifact_id (None if creating new artifact)
    target_name: str  # filename or artifact title
    old_content: str
    new_content: str
    diff: str  # Unified diff string


class AgentChatResponse(BaseModel):
    """Response schema for agent chat."""
    proposals: List[Proposal]


class AgentAcceptRequest(BaseModel):
    """Request schema for accepting a proposal."""
    proposal: Proposal

