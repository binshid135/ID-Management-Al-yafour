import React, { useState } from 'react';
import axios from 'axios';

const DocumentList = ({ documents, onUpdate, onDelete }) => {
  const [editingDoc, setEditingDoc] = useState(null);
  const [viewingDoc, setViewingDoc] = useState(null);

  const handleEdit = (doc) => {
    setEditingDoc(doc);
  };

  const handleUpdate = async () => {
    try {
      await axios.put(`http://localhost:5000/api/documents/${editingDoc.id}`, editingDoc);
      onUpdate();
      setEditingDoc(null);
      alert('Document updated successfully!');
    } catch (error) {
      console.error('Error updating document:', error);
      alert('Error updating document');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await axios.delete(`http://localhost:5000/api/documents/${id}`);
        onDelete();
        alert('Document deleted successfully!');
      } catch (error) {
        console.error('Error deleting document:', error);
        alert('Error deleting document');
      }
    }
  };

  const getDocumentTypeLabel = (type) => {
    return type === 'id1' ? 'First ID' : 'Second ID';
  };

  const getDocumentTypeColor = (type) => {
    return type === 'id1' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Uploaded Documents</h2>
      
      {documents.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No documents uploaded yet</p>
      ) : (
        <div className="space-y-4">
          {documents.map((doc) => (
            <div key={doc.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${getDocumentTypeColor(doc.document_type)}`}>
                      {getDocumentTypeLabel(doc.document_type)}
                    </span>
                    {doc.id_type && doc.id_type !== 'UNKNOWN' && (
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                        {doc.id_type.replace('_', ' ')}
                      </span>
                    )}
                  </div>
                  <p className="text-gray-700"><strong>Name:</strong> {doc.full_name || 'N/A'}</p>
                  <p className="text-gray-700"><strong>Document Number:</strong> {doc.document_number || 'N/A'}</p>
                  {doc.date_of_birth && <p className="text-gray-700"><strong>Date of Birth:</strong> {doc.date_of_birth}</p>}
                  {doc.nationality && <p className="text-gray-700"><strong>Nationality:</strong> {doc.nationality}</p>}
                  {doc.expiry_date && <p className="text-gray-700"><strong>Expiry Date:</strong> {doc.expiry_date}</p>}
                  <p className="text-sm text-gray-500 mt-2">
                    Uploaded: {new Date(doc.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex space-x-2 ml-4">
                  <button
                    onClick={() => setViewingDoc(doc)}
                    className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                  >
                    View
                  </button>
                  <button
                    onClick={() => handleEdit(doc)}
                    className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit Modal */}
      {editingDoc && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setEditingDoc(null)}>
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-xl font-bold mb-4">Edit Document</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={editingDoc.full_name || ''}
                  onChange={(e) => setEditingDoc({...editingDoc, full_name: e.target.value})}
                  className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Document Number</label>
                <input
                  type="text"
                  value={editingDoc.document_number || ''}
                  onChange={(e) => setEditingDoc({...editingDoc, document_number: e.target.value})}
                  className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                <input
                  type="text"
                  value={editingDoc.date_of_birth || ''}
                  onChange={(e) => setEditingDoc({...editingDoc, date_of_birth: e.target.value})}
                  placeholder="DD/MM/YYYY"
                  className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Nationality</label>
                <input
                  type="text"
                  value={editingDoc.nationality || ''}
                  onChange={(e) => setEditingDoc({...editingDoc, nationality: e.target.value})}
                  className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
                <input
                  type="text"
                  value={editingDoc.expiry_date || ''}
                  onChange={(e) => setEditingDoc({...editingDoc, expiry_date: e.target.value})}
                  placeholder="DD/MM/YYYY"
                  className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => setEditingDoc(null)}
                className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdate}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* View Modal */}
      {viewingDoc && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setViewingDoc(null)}>
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-xl font-bold mb-4">Document Details</h3>
            <div className="space-y-2">
              <p><strong>Document Type:</strong> {getDocumentTypeLabel(viewingDoc.document_type)}</p>
              <p><strong>ID Type:</strong> {viewingDoc.id_type?.replace('_', ' ') || 'N/A'}</p>
              <p><strong>Full Name:</strong> {viewingDoc.full_name || 'N/A'}</p>
              <p><strong>Document Number:</strong> {viewingDoc.document_number || 'N/A'}</p>
              <p><strong>Date of Birth:</strong> {viewingDoc.date_of_birth || 'N/A'}</p>
              <p><strong>Nationality:</strong> {viewingDoc.nationality || 'N/A'}</p>
              <p><strong>Expiry Date:</strong> {viewingDoc.expiry_date || 'N/A'}</p>
              <p><strong>Created:</strong> {new Date(viewingDoc.created_at).toLocaleString()}</p>
              <p><strong>Last Updated:</strong> {new Date(viewingDoc.updated_at).toLocaleString()}</p>
              {/* {viewingDoc.extracted_text && (
                <div className="mt-4">
                  <strong>Extracted Text:</strong>
                  <pre className="mt-2 p-3 bg-gray-100 rounded text-sm overflow-x-auto">
                    {viewingDoc.extracted_text}
                  </pre>
                </div>
              )} */}
            </div>
            <div className="flex justify-end mt-6">
              <button
                onClick={() => setViewingDoc(null)}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentList;