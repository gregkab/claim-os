import type { Proposal } from '../types';

interface DiffViewProps {
  proposal: Proposal;
}

export function DiffView({ proposal }: DiffViewProps) {
  return (
    <div style={{ marginTop: '20px' }}>
      <h4>Proposed Changes to: {proposal.target_name}</h4>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px' }}>
        <div>
          <h5 style={{ marginBottom: '10px' }}>Current</h5>
          <pre
            style={{
              padding: '10px',
              backgroundColor: '#f5f5f5',
              border: '1px solid #ddd',
              borderRadius: '4px',
              overflow: 'auto',
              maxHeight: '400px',
              fontSize: '0.9em',
            }}
          >
            {proposal.old_content || '(empty)'}
          </pre>
        </div>
        <div>
          <h5 style={{ marginBottom: '10px' }}>Proposed</h5>
          <pre
            style={{
              padding: '10px',
              backgroundColor: '#f0f8ff',
              border: '1px solid #ddd',
              borderRadius: '4px',
              overflow: 'auto',
              maxHeight: '400px',
              fontSize: '0.9em',
            }}
          >
            {proposal.new_content}
          </pre>
        </div>
      </div>
      <div>
        <h5 style={{ marginBottom: '10px' }}>Diff</h5>
        <pre
          style={{
            padding: '10px',
            backgroundColor: '#f9f9f9',
            border: '1px solid #ddd',
            borderRadius: '4px',
            overflow: 'auto',
            maxHeight: '300px',
            fontSize: '0.85em',
            fontFamily: 'monospace',
          }}
        >
          {proposal.diff || 'No differences'}
        </pre>
      </div>
    </div>
  );
}

