import { useState, useEffect } from 'react';
import { artifactsApi } from '../services/api';
import type { Artifact } from '../types';

interface SummaryViewProps {
  claimId: number;
}

export function SummaryView({ claimId }: SummaryViewProps) {
  const [summary, setSummary] = useState<Artifact | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSummary();
  }, [claimId]);

  const loadSummary = async () => {
    try {
      setLoading(true);
      setError(null);
      const artifacts = await artifactsApi.list(claimId);
      const summaryArtifact = artifacts.find(a => a.type === 'summary');
      setSummary(summaryArtifact || null);
    } catch (err: any) {
      console.error('Failed to load summary:', err);
      setError(err?.response?.data?.detail || 'Failed to load summary');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '1rem', color: '#666', fontStyle: 'italic' }}>
        Loading summary...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '1rem', color: '#d32f2f' }}>
        Error: {error}
      </div>
    );
  }

  if (!summary || !summary.current_version) {
    return (
      <div style={{ padding: '1rem', color: '#666', fontStyle: 'italic' }}>
        No summary available yet. Generate one using the "Generate or Update Summary" button.
      </div>
    );
  }

  return (
    <div style={{ 
      border: '1px solid #ddd', 
      borderRadius: '6px', 
      padding: '1.5rem',
      backgroundColor: '#fff',
    }}>
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '1rem',
        borderBottom: '1px solid #eee',
        paddingBottom: '0.75rem',
      }}>
        <h3 style={{ margin: 0, color: '#213547' }}>{summary.title}</h3>
        <span style={{ 
          fontSize: '0.85em', 
          color: '#666',
        }}>
          Updated: {new Date(summary.updated_at).toLocaleDateString()}
        </span>
      </div>
      <div 
        style={{
          lineHeight: '1.6',
          color: '#213547',
          whiteSpace: 'pre-wrap',
          fontFamily: 'system-ui, -apple-system, sans-serif',
        }}
      >
        {summary.current_version.content.split('\n').map((line, idx) => {
          // Simple markdown rendering
          if (line.startsWith('# ')) {
            return <h1 key={idx} style={{ marginTop: '1.5em', marginBottom: '0.5em', fontWeight: 600, fontSize: '1.5em' }}>{line.substring(2)}</h1>;
          } else if (line.startsWith('## ')) {
            return <h2 key={idx} style={{ marginTop: '1.2em', marginBottom: '0.5em', fontWeight: 600, fontSize: '1.3em' }}>{line.substring(3)}</h2>;
          } else if (line.startsWith('### ')) {
            return <h3 key={idx} style={{ marginTop: '1em', marginBottom: '0.5em', fontWeight: 600, fontSize: '1.1em' }}>{line.substring(4)}</h3>;
          } else if (line.trim() === '') {
            return <br key={idx} />;
          } else {
            // Basic markdown inline
            let content = line;
            content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
            content = content.replace(/\*(.+?)\*/g, '<em>$1</em>');
            return <p key={idx} style={{ margin: '0.5em 0' }} dangerouslySetInnerHTML={{ __html: content }} />;
          }
        })}
      </div>
    </div>
  );
}

