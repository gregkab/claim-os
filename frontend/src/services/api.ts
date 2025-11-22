/** API client service */
import axios from 'axios';
import type {
  Claim,
  File,
  Artifact,
  AgentChatRequest,
  AgentChatResponse,
  AgentAcceptRequest,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Claims API
export const claimsApi = {
  list: async (): Promise<Claim[]> => {
    const response = await api.get<Claim[]>('/claims');
    return response.data;
  },

  get: async (claimId: number): Promise<Claim> => {
    const response = await api.get<Claim>(`/claims/${claimId}`);
    return response.data;
  },

  create: async (data: { title: string; reference_number?: string }): Promise<Claim> => {
    const response = await api.post<Claim>('/claims', data);
    return response.data;
  },
};

// Files API
export const filesApi = {
  list: async (claimId: number): Promise<File[]> => {
    const response = await api.get<File[]>(`/claims/${claimId}/files`);
    return response.data;
  },

  upload: async (claimId: number, file: File): Promise<File> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<File>(`/claims/${claimId}/files`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// Agent API
export const agentApi = {
  chat: async (claimId: number, request: AgentChatRequest): Promise<AgentChatResponse> => {
    const response = await api.post<AgentChatResponse>(
      `/claims/${claimId}/agent/chat`,
      request
    );
    return response.data;
  },

  accept: async (claimId: number, request: AgentAcceptRequest): Promise<any> => {
    const response = await api.post(`/claims/${claimId}/agent/accept`, request);
    return response.data;
  },
};

