import { useState, useEffect } from 'react';
import { filesApi } from '../services/api';
import type { File } from '../types';

interface FileListProps {
  claimId: number;
}

export function FileList({ claimId }: FileListProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(true);

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

  if (loading) {
    return <div>Loading files...</div>;
  }

  if (files.length === 0) {
    return <p>No files uploaded yet.</p>;
  }

  return (
    <div>
      <h3>Files ({files.length})</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {files.map((file) => (
          <li
            key={file.id}
            style={{
              padding: '10px',
              marginBottom: '5px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              backgroundColor: '#f9f9f9',
            }}
          >
            <strong>{file.filename}</strong>
            {file.size_bytes && (
              <span style={{ marginLeft: '10px', color: '#666' }}>
                ({(file.size_bytes / 1024).toFixed(2)} KB)
              </span>
            )}
            {file.mime_type && (
              <span style={{ marginLeft: '10px', color: '#999', fontSize: '0.9em' }}>
                {file.mime_type}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

