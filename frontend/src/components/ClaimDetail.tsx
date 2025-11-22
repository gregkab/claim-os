import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { claimsApi } from '../services/api';
import type { Claim } from '../types';
import { FileList } from './FileList';
import { FileUpload } from './FileUpload';
import { AgentChat } from './AgentChat';

export function ClaimDetail() {
  const { claimId } = useParams<{ claimId: string }>();
  const navigate = useNavigate();
  const [claim, setClaim] = useState<Claim | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (claimId) {
      loadClaim();
    }
  }, [claimId]);

  const loadClaim = async () => {
    if (!claimId) return;
    try {
      setLoading(true);
      const data = await claimsApi.get(parseInt(claimId));
      setClaim(data);
    } catch (error) {
      console.error('Failed to load claim:', error);
      alert('Failed to load claim');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
    loadClaim();
  };

  if (loading) {
    return <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>Loading claim...</div>;
  }

  if (!claim) {
    return <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>Claim not found</div>;
  }

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <button onClick={() => navigate('/')} style={{ marginBottom: '1rem' }}>
          ← Back to Claims
        </button>
        <h1 style={{ margin: '0 0 0.5rem 0', color: '#213547' }}>{claim.title}</h1>
        {claim.reference_number && (
          <p style={{ margin: 0, color: '#666', fontSize: '0.95em' }}>Reference: {claim.reference_number}</p>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', alignItems: 'start' }}>
        <div>
          <FileUpload claimId={claim.id} onUploadSuccess={handleRefresh} />
          <FileList key={refreshKey} claimId={claim.id} onDelete={handleRefresh} />
        </div>
        <div>
          <AgentChat claimId={claim.id} onAccept={handleRefresh} />
        </div>
      </div>
    </div>
  );
}

