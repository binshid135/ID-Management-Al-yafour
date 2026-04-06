import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

const UploadForm = ({ onUploadSuccess }) => {
  const [files, setFiles] = useState({ id1: null, id2: null });
  const [uploading, setUploading] = useState(false);

  const onDrop = (documentType, acceptedFiles) => {
    setFiles(prev => ({ ...prev, [documentType]: acceptedFiles[0] }));
  };

  const removeFile = (documentType) => {
    setFiles(prev => ({ ...prev, [documentType]: null }));
  };

  const handleUpload = async () => {
    if (!files.id1 && !files.id2) {
      alert('Please select at least one ID document');
      return;
    }

    setUploading(true);

    for (const [docType, file] of Object.entries(files)) {
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', docType);

        try {
          await axios.post('http://localhost:5000/api/upload', formData);
          onUploadSuccess();
        } catch (error) {
          console.error(`Error uploading ${docType}:`, error);
          alert(`Failed to upload ${docType}`);
        }
      }
    }

    setFiles({ id1: null, id2: null });
    setUploading(false);
  };

  const DropzoneComponent = ({ documentType, label }) => {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop: (files) => onDrop(documentType, files),
      accept: {
        'image/*': ['.jpeg', '.jpg', '.png']
      },
      maxFiles: 1
    });

    return (
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-white">
        {files[documentType] ? (
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-800">{files[documentType].name}</p>
              <p className="text-sm text-gray-500">
                {(files[documentType].size / 1024).toFixed(2)} KB
              </p>
            </div>
            <button
              onClick={() => removeFile(documentType)}
              className="text-red-500 hover:text-red-700 px-3 py-1 rounded"
            >
              Remove
            </button>
          </div>
        ) : (
          <div {...getRootProps()} className="cursor-pointer text-center">
            <input {...getInputProps()} />
            <div className="text-4xl mb-2">📄</div>
            {isDragActive ? (
              <p className="text-blue-500">Drop the {label} here...</p>
            ) : (
              <div>
                <p className="font-medium text-gray-700">{label}</p>
                <p className="text-sm text-gray-500 mt-1">
                  Drag & drop or click to select
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Upload ID Documents</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <DropzoneComponent documentType="id1" label="First ID Document" />
        <DropzoneComponent documentType="id2" label="Second ID Document" />
      </div>
      <button
        onClick={handleUpload}
        disabled={uploading || (!files.id1 && !files.id2)}
        className={`w-full py-2 px-4 rounded-lg font-semibold transition-colors ${
          uploading || (!files.id1 && !files.id2)
            ? 'bg-gray-300 cursor-not-allowed'
            : 'bg-blue-500 text-white hover:bg-blue-600'
        }`}
      >
        {uploading ? 'Uploading...' : 'Upload Documents'}
      </button>
    </div>
  );
};

export default UploadForm;