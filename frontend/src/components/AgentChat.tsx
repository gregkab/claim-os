import { useState } from 'react';
import { agentApi } from '../services/api';
import type { Proposal } from '../types';
import { DiffView } from './DiffView';

interface AgentChatProps {
  claimId: number;
  onAccept?: () => void;
}

interface Message {
  role: 'user' | 'agent';
  content: string;
  proposals?: Proposal[];
}

export function AgentChat({ claimId, onAccept }: AgentChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [pendingProposals, setPendingProposals] = useState<Proposal[]>([]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await agentApi.chat(claimId, { message: input });
      const agentMessage: Message = {
        role: 'agent',
        content: response.proposals.length > 0
          ? `I found ${response.proposals.length} proposal(s) for you to review.`
          : 'I couldn\'t understand that command. Try "create a summary" or "update file".',
        proposals: response.proposals,
      };
      setMessages((prev) => [...prev, agentMessage]);
      setPendingProposals(response.proposals);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        role: 'agent',
        content: 'Sorry, I encountered an error processing your request.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (proposal: Proposal) => {
    try {
      await agentApi.accept(claimId, { proposal });
      setPendingProposals((prev) => prev.filter((p) => p !== proposal));
      const acceptMessage: Message = {
        role: 'agent',
        content: `Accepted changes to ${proposal.target_name}.`,
      };
      setMessages((prev) => [...prev, acceptMessage]);
      if (onAccept) {
        onAccept();
      }
    } catch (error: any) {
      console.error('Failed to accept proposal:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to accept proposal';
      const errorMsg: Message = {
        role: 'agent',
        content: `Error: ${errorMessage}`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ marginBottom: '1rem' }}>Agent Chat</h3>
      <div
        style={{
          border: '1px solid #ddd',
          borderRadius: '6px',
          padding: '1rem',
          marginBottom: '1rem',
          overflowY: 'auto',
          minHeight: '300px',
          maxHeight: '500px',
          backgroundColor: '#fafafa',
        }}
      >
        {messages.length === 0 && (
          <p style={{ color: '#666', fontStyle: 'italic', margin: 0 }}>
            Type a command like "create a summary" or "update file" to get started.
          </p>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              marginBottom: '1rem',
              padding: '0.75rem',
              backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#fff',
              borderRadius: '6px',
              textAlign: msg.role === 'user' ? 'right' : 'left',
            }}
          >
            <div style={{ fontWeight: '500', color: '#213547', marginBottom: '0.5rem' }}>
              {msg.role === 'user' ? 'You' : 'Agent'}:
            </div>
            <p style={{ margin: 0, color: '#213547' }}>{msg.content}</p>
            {msg.proposals && msg.proposals.length > 0 && (
              <div style={{ marginTop: '1rem' }}>
                {msg.proposals.map((proposal, pIdx) => (
                  <div key={pIdx} style={{ marginBottom: '1rem' }}>
                    <DiffView proposal={proposal} />
                    <button
                      onClick={() => handleAccept(proposal)}
                      style={{
                        marginTop: '0.5rem',
                        padding: '0.5rem 1rem',
                        backgroundColor: '#4caf50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                      }}
                    >
                      Accept Changes
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div style={{ color: '#666', fontStyle: 'italic', margin: 0 }}>Agent is thinking...</div>
        )}
      </div>
      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Type a command..."
          style={{ flex: 1, padding: '0.5rem', borderRadius: '4px', border: '1px solid #ddd', fontSize: '0.95em' }}
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#2196f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}

