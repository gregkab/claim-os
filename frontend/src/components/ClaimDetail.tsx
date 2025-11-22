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
    return <div>Loading claim...</div>;
  }

  if (!claim) {
    return <div>Claim not found</div>;
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => navigate('/')} style={{ marginBottom: '10px' }}>
          ← Back to Claims
        </button>
        <h1>{claim.title}</h1>
        {claim.reference_number && (
          <p style={{ color: '#666' }}>Reference: {claim.reference_number}</p>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div>
          <FileUpload claimId={claim.id} onUploadSuccess={handleRefresh} />
          <FileList key={refreshKey} claimId={claim.id} />
        </div>
        <div>
          <AgentChat claimId={claim.id} onAccept={handleRefresh} />
        </div>
      </div>
    </div>
  );
}

