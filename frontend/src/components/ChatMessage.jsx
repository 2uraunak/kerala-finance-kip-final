import React from 'react';

const ChatMessage = ({ role, content }) => {
  const isUser = role === 'user';
  
  return (
    <div className={`flex w-full mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
        isUser 
          ? 'bg-blue-600 text-white rounded-tr-none shadow-sm' 
          : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none shadow-sm'
      }`}>
        <div className="text-sm font-medium mb-1 opacity-70">
          {isUser ? 'You' : 'Assistant'}
        </div>
        <div className="text-sm whitespace-pre-wrap leading-relaxed">
          {content}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
