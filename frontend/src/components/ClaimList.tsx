import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { claimsApi } from '../services/api';
import type { Claim } from '../types';

export function ClaimList() {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [title, setTitle] = useState('');
  const [referenceNumber, setReferenceNumber] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadClaims();
  }, []);

  const loadClaims = async () => {
    try {
      setLoading(true);
      const data = await claimsApi.list();
      setClaims(data);
    } catch (error) {
      console.error('Failed to load claims:', error);
      alert('Failed to load claims');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newClaim = await claimsApi.create({
        title,
        reference_number: referenceNumber || undefined,
      });
      setTitle('');
      setReferenceNumber('');
      setShowCreateForm(false);
      navigate(`/claims/${newClaim.id}`);
    } catch (error) {
      console.error('Failed to create claim:', error);
      alert('Failed to create claim');
    }
  };

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>Loading claims...</div>;
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>Claims</h1>
        <button onClick={() => setShowCreateForm(!showCreateForm)}>
          {showCreateForm ? 'Cancel' : 'Create New Claim'}
        </button>
      </div>

      {showCreateForm && (
        <form onSubmit={handleCreate} style={{ marginBottom: '2rem', padding: '1.5rem', border: '1px solid #ddd', borderRadius: '6px', backgroundColor: '#fafafa' }}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px', fontSize: '0.95em' }}
            />
          </div>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
              Reference Number (optional)
            </label>
            <input
              type="text"
              value={referenceNumber}
              onChange={(e) => setReferenceNumber(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', border: '1px solid #ddd', borderRadius: '4px', fontSize: '0.95em' }}
            />
          </div>
          <button type="submit">Create</button>
        </form>
      )}

      {claims.length === 0 ? (
        <p style={{ color: '#666', textAlign: 'center', padding: '2rem' }}>No claims yet. Create one to get started!</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {claims.map((claim) => (
            <li
              key={claim.id}
              onClick={() => navigate(`/claims/${claim.id}`)}
              style={{
                padding: '1rem',
                marginBottom: '0.75rem',
                border: '1px solid #ddd',
                borderRadius: '6px',
                cursor: 'pointer',
                backgroundColor: '#fff',
                transition: 'background-color 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f5f5f5';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fff';
              }}
            >
              <h3 style={{ margin: '0 0 0.5rem 0', color: '#213547' }}>{claim.title}</h3>
              {claim.reference_number && (
                <p style={{ margin: '0.25rem 0', color: '#666', fontSize: '0.9em' }}>Ref: {claim.reference_number}</p>
              )}
              <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85em', color: '#999' }}>
                Created: {new Date(claim.created_at).toLocaleDateString()}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

