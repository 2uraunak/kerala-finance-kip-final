import React from 'react';

const DocumentCard = ({ document, onClick }) => {
  return (
    <div 
      className="bg-white rounded-lg shadow-sm p-4 border border-gray-100 hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onClick && onClick(document)}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-gray-800 line-clamp-2" title={document.title || 'Untitled Document'}>
          {document.title || 'Untitled Document'}
        </h3>
        <span className="text-xs px-2 py-1 bg-blue-50 text-blue-600 rounded-full shrink-0">
          {document.doc_type || 'Unknown'}
        </span>
      </div>
      <p className="text-sm text-gray-500 mb-3 truncate">
        {document.doc_number || 'No number'}
      </p>
      
      <div className="flex justify-between items-center text-xs text-gray-400">
        <span>{document.issue_date || 'No Date'}</span>
        <span className={`px-2 py-0.5 rounded-full ${
          document.status === 'active' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'
        }`}>
          {document.status || 'Active'}
        </span>
      </div>
    </div>
  );
};

export default DocumentCard;
