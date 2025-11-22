/** TypeScript types matching backend Pydantic schemas */

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface Claim {
  id: number;
  owner_user_id: number;
  title: string;
  reference_number: string | null;
  created_at: string;
  updated_at: string;
}

export interface File {
  id: number;
  claim_id: number;
  filename: string;
  storage_path: string;
  mime_type: string | null;
  size_bytes: number | null;
  created_at: string;
}

export interface ArtifactVersion {
  id: number;
  artifact_id: number;
  content: string;
  created_at: string;
  created_by_user_id: number | null;
  version_metadata: Record<string, any> | null;
}

export interface Artifact {
  id: number;
  claim_id: number;
  type: string;
  title: string;
  current_version_id: number | null;
  created_at: string;
  updated_at: string;
  current_version: ArtifactVersion | null;
}

export interface Proposal {
  type: "file" | "artifact";
  target_id: number | null;
  target_name: string;
  old_content: string;
  new_content: string;
  diff: string;
}

export interface AgentChatRequest {
  message: string;
}

export interface AgentChatResponse {
  proposals: Proposal[];
}

export interface AgentAcceptRequest {
  proposal: Proposal;
}

