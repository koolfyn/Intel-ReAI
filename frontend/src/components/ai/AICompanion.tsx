import React, { useState } from 'react';
import { aiApi } from '../../services/api';
import { AIQueryResponse } from '../../types';
import LoadingSpinner from '../common/LoadingSpinner';
import { XMarkIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';

interface AICompanionProps {
  isOpen: boolean;
  onClose: () => void;
  subredditId?: number;
  subredditName?: string;
}

const AICompanion: React.FC<AICompanionProps> = ({
  isOpen,
  onClose,
  subredditId,
  subredditName
}) => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<AIQueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<Array<{query: string, response: AIQueryResponse}>>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const currentQuery = query.trim();
    setIsLoading(true);
    setResponse(null); // Clear current response

    try {
      const result = await aiApi.queryCompanion({
        query: currentQuery,
        subreddit_id: subredditId,
      });

      // Add to chat history immediately
      setChatHistory(prev => [...prev, { query: currentQuery, response: result }]);
      setQuery('');
    } catch (error) {
      console.error('Error querying AI companion:', error);
      // Add error to chat history
      const errorResponse: AIQueryResponse = {
        response: "I'm sorry, I encountered an error processing your request. Please try again.",
        citations: [],
        sources: []
      };
      setChatHistory(prev => [...prev, { query: currentQuery, response: errorResponse }]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setResponse(null);
    setChatHistory([]);
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-25 z-40"
        onClick={onClose}
      />

      {/* Side Window */}
      <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-2xl z-50 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <ChatBubbleLeftRightIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">AI Companion</h3>
              {subredditName && (
                <p className="text-xs text-gray-500">for r/{subredditName}</p>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={clearChat}
              className="text-sm text-gray-500 hover:text-gray-700 px-2 py-1 rounded hover:bg-gray-200"
            >
              Clear
            </button>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-200"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {chatHistory.length === 0 && !response && !isLoading && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <ChatBubbleLeftRightIcon className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="text-lg font-medium text-gray-900 mb-2">AI Companion</h4>
              <p className="text-gray-500 text-sm max-w-xs">
                Ask me anything about posts, topics, or get help with your questions.
              </p>
            </div>
          )}

          {/* Chat History */}
          {chatHistory.map((chat, index) => (
            <div key={index} className="space-y-3">
              {/* User Message */}
              <div className="flex justify-end">
                <div className="bg-blue-600 text-white rounded-lg px-4 py-2 max-w-xs">
                  <p className="text-sm">{chat.query}</p>
                </div>
              </div>

              {/* AI Response */}
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-900 rounded-lg px-4 py-2 max-w-sm">
                  <div className="text-sm mb-2 whitespace-pre-wrap">
                    {chat.response.response}
                  </div>

                  {/* Citations */}
                  {chat.response.citations && chat.response.citations.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs font-medium text-gray-600 border-b border-gray-300 pb-1">
                        📚 Sources ({chat.response.citations.length})
                      </p>
                      {chat.response.citations.map((citation, idx) => (
                        <div key={idx} className="text-xs bg-white p-2 rounded border border-gray-200">
                          <p className="font-medium text-gray-800 mb-1">{citation.post_title}</p>
                          <p className="text-gray-600 text-xs leading-relaxed mb-1">
                            "{citation.excerpt}"
                          </p>
                          <div className="flex justify-between items-center">
                            <span className="text-gray-400 text-xs">
                              Relevance: {Math.round(citation.relevance_score * 100)}%
                            </span>
                            <span className="text-blue-500 text-xs hover:underline cursor-pointer">
                              View Post →
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Sources */}
                  {chat.response.sources && chat.response.sources.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs font-medium text-gray-600 mb-1">🔗 Quick Links:</p>
                      <div className="space-y-1">
                        {chat.response.sources.map((source, idx) => (
                          <a
                            key={idx}
                            href={source.url}
                            className="text-xs text-blue-600 hover:text-blue-800 hover:underline block"
                          >
                            {source.title}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}


          {/* Loading State */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-900 rounded-lg px-4 py-2">
                <div className="flex items-center space-x-2">
                  <LoadingSpinner size="sm" />
                  <span className="text-sm text-gray-500">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter prompt here"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </form>
          <p className="text-xs text-gray-500 mt-2 text-center">
            AI Companion's answers may not be entirely accurate, please verify.
          </p>
        </div>
      </div>
    </>
  );
};

export default AICompanion;
