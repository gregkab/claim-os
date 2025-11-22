import { useState } from 'react';
import { filesApi } from '../services/api';

interface FileUploadProps {
  claimId: number;
  onUploadSuccess?: () => void;
}

export function FileUpload({ claimId, onUploadSuccess }: FileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    try {
      setUploading(true);
      await filesApi.upload(claimId, selectedFile);
      setSelectedFile(null);
      if (onUploadSuccess) {
        onUploadSuccess();
      }
      // Reset file input
      const fileInput = document.getElementById('file-input') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }
    } catch (error) {
      console.error('Failed to upload file:', error);
      alert('Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ marginBottom: '1.5rem', padding: '1.5rem', border: '1px solid #ddd', borderRadius: '6px', backgroundColor: '#fafafa' }}>
      <h3 style={{ marginBottom: '1rem' }}>Upload File</h3>
      <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
        <input
          id="file-input"
          type="file"
          onChange={handleFileChange}
          disabled={uploading}
          style={{ flex: '1 1 auto', minWidth: '200px' }}
        />
        <button onClick={handleUpload} disabled={!selectedFile || uploading}>
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
      {selectedFile && (
        <p style={{ marginTop: '0.75rem', fontSize: '0.9em', color: '#666' }}>
          Selected: {selectedFile.name}
        </p>
      )}
    </div>
  );
}

