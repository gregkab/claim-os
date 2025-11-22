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
    return <div>Loading claims...</div>;
  }

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Claims</h1>
        <button onClick={() => setShowCreateForm(!showCreateForm)}>
          {showCreateForm ? 'Cancel' : 'Create New Claim'}
        </button>
      </div>

      {showCreateForm && (
        <form onSubmit={handleCreate} style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ccc', borderRadius: '4px' }}>
          <div style={{ marginBottom: '10px' }}>
            <label>
              Title: <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                style={{ width: '100%', padding: '5px' }}
              />
            </label>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>
              Reference Number (optional): <input
                type="text"
                value={referenceNumber}
                onChange={(e) => setReferenceNumber(e.target.value)}
                style={{ width: '100%', padding: '5px' }}
              />
            </label>
          </div>
          <button type="submit">Create</button>
        </form>
      )}

      {claims.length === 0 ? (
        <p>No claims yet. Create one to get started!</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {claims.map((claim) => (
            <li
              key={claim.id}
              onClick={() => navigate(`/claims/${claim.id}`)}
              style={{
                padding: '15px',
                marginBottom: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                cursor: 'pointer',
                backgroundColor: '#f9f9f9',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f0f0f0';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#f9f9f9';
              }}
            >
              <h3 style={{ margin: 0 }}>{claim.title}</h3>
              {claim.reference_number && (
                <p style={{ margin: '5px 0', color: '#666' }}>Ref: {claim.reference_number}</p>
              )}
              <p style={{ margin: '5px 0', fontSize: '0.9em', color: '#999' }}>
                Created: {new Date(claim.created_at).toLocaleDateString()}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

