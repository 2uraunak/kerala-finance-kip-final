import React, { useState } from 'react';

const UploadModal = ({ isOpen, onClose, onUpload }) => {
  const [file, setFile] = useState(null);

  if (!isOpen) return null;

  const handleUpload = () => {
    if (file && onUpload) {
      onUpload(file);
      setFile(null);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex justify-center items-center backdrop-blur-sm">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 transform transition-all">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-xl font-bold text-gray-800">Upload Document</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
        
        <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center hover:border-blue-500 hover:bg-blue-50 transition-colors mb-6 cursor-pointer"
             onClick={() => document.getElementById('fileUpload').click()}>
          <input 
            type="file" 
            id="fileUpload" 
            className="hidden" 
            onChange={(e) => setFile(e.target.files[0])}
            accept=".pdf,.doc,.docx"
          />
          <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
          <p className="text-sm font-medium text-gray-600 mb-1">
            {file ? file.name : "Click to select a file"}
          </p>
          <p className="text-xs text-gray-400">PDF, DOC, DOCX up to 10MB</p>
        </div>

        <div className="flex justify-end gap-3">
          <button 
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none"
          >
            Cancel
          </button>
          <button 
            onClick={handleUpload}
            disabled={!file}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Upload
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadModal;
