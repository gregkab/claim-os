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
    <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '4px' }}>
      <h3>Upload File</h3>
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <input
          id="file-input"
          type="file"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <button onClick={handleUpload} disabled={!selectedFile || uploading}>
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>
      {selectedFile && (
        <p style={{ marginTop: '10px', fontSize: '0.9em', color: '#666' }}>
          Selected: {selectedFile.name}
        </p>
      )}
    </div>
  );
}

