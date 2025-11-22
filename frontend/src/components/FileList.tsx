import { useState, useEffect } from 'react';
import { filesApi } from '../services/api';
import type { File } from '../types';

interface FileListProps {
  claimId: number;
  onDelete?: () => void;
}

export function FileList({ claimId, onDelete }: FileListProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<number | null>(null);

  useEffect(() => {
    loadFiles();
  }, [claimId]);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const data = await filesApi.list(claimId);
      setFiles(data);
    } catch (error) {
      console.error('Failed to load files:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (fileId: number) => {
    if (!confirm('Are you sure you want to delete this file?')) {
      return;
    }

    try {
      setDeleting(fileId);
      await filesApi.delete(claimId, fileId);
      await loadFiles();
      if (onDelete) {
        onDelete();
      }
    } catch (error: any) {
      console.error('Failed to delete file:', error);
      const errorMessage = error?.response?.data?.detail || error?.message || 'Failed to delete file';
      alert(errorMessage);
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return <div style={{ color: '#666' }}>Loading files...</div>;
  }

  if (files.length === 0) {
    return <div><h3 style={{ marginBottom: '1rem' }}>Files (0)</h3><p style={{ color: '#666' }}>No files uploaded yet.</p></div>;
  }

  return (
    <div>
      <h3 style={{ marginBottom: '1rem' }}>Files ({files.length})</h3>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {files.map((file) => (
          <li
            key={file.id}
            style={{
              padding: '0.75rem',
              marginBottom: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '6px',
              backgroundColor: '#fff',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div style={{ flex: 1 }}>
              <a
                href={filesApi.getDownloadUrl(claimId, file.id)}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  fontWeight: '500',
                  color: '#2196f3',
                  textDecoration: 'none',
                  marginBottom: '0.25rem',
                  display: 'inline-block',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.textDecoration = 'underline';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.textDecoration = 'none';
                }}
              >
                {file.filename}
              </a>
              <div style={{ fontSize: '0.85em', color: '#666' }}>
                {file.size_bytes && (
                  <span>{(file.size_bytes / 1024).toFixed(2)} KB</span>
                )}
                {file.size_bytes && file.mime_type && <span> • </span>}
                {file.mime_type && <span>{file.mime_type}</span>}
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <button
                onClick={() => {
                  window.open(filesApi.getDownloadUrl(claimId, file.id), '_blank');
                }}
                style={{
                  padding: '0.4rem 0.8rem',
                  fontSize: '0.85em',
                  backgroundColor: '#2196f3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Open
              </button>
              <button
                onClick={() => handleDelete(file.id)}
                disabled={deleting === file.id}
                style={{
                  padding: '0.4rem 0.8rem',
                  fontSize: '0.85em',
                  backgroundColor: '#ff4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: deleting === file.id ? 'not-allowed' : 'pointer',
                  opacity: deleting === file.id ? 0.6 : 1,
                }}
              >
                {deleting === file.id ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

