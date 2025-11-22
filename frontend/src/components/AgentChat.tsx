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
    } catch (error) {
      console.error('Failed to accept proposal:', error);
      alert('Failed to accept proposal');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <h3>Agent Chat</h3>
      <div
        style={{
          flex: 1,
          border: '1px solid #ddd',
          borderRadius: '4px',
          padding: '15px',
          marginBottom: '15px',
          overflowY: 'auto',
          minHeight: '300px',
          maxHeight: '500px',
          backgroundColor: '#fafafa',
        }}
      >
        {messages.length === 0 && (
          <p style={{ color: '#666', fontStyle: 'italic' }}>
            Type a command like "create a summary" or "update file" to get started.
          </p>
        )}
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              marginBottom: '15px',
              padding: '10px',
              backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#f5f5f5',
              borderRadius: '4px',
              textAlign: msg.role === 'user' ? 'right' : 'left',
            }}
          >
            <strong>{msg.role === 'user' ? 'You' : 'Agent'}:</strong>
            <p style={{ margin: '5px 0' }}>{msg.content}</p>
            {msg.proposals && msg.proposals.length > 0 && (
              <div style={{ marginTop: '10px' }}>
                {msg.proposals.map((proposal, pIdx) => (
                  <div key={pIdx} style={{ marginBottom: '15px' }}>
                    <DiffView proposal={proposal} />
                    <button
                      onClick={() => handleAccept(proposal)}
                      style={{
                        padding: '8px 16px',
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
          <div style={{ color: '#666', fontStyle: 'italic' }}>Agent is thinking...</div>
        )}
      </div>
      <div style={{ display: 'flex', gap: '10px' }}>
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
          style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          style={{
            padding: '8px 16px',
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

