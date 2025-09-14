import React, { useState } from 'react';
import { aiApi } from '../../services/api';
import { AIQueryResponse } from '../../types';
import LoadingSpinner from '../common/LoadingSpinner';

interface AICompanionProps {
  subredditId?: number;
  subredditName?: string;
}

const AICompanion: React.FC<AICompanionProps> = ({ subredditId, subredditName }) => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<AIQueryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<Array<{query: string, response: AIQueryResponse}>>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const result = await aiApi.queryCompanion({
        query: query.trim(),
        subreddit_id: subredditId,
      });

      setResponse(result);
      setChatHistory(prev => [...prev, { query: query.trim(), response: result }]);
      setQuery('');
    } catch (error) {
      console.error('Error querying AI companion:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setResponse(null);
    setChatHistory([]);
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 h-96 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          🤖 AI Companion
          {subredditName && (
            <span className="text-sm text-gray-500 ml-2">
              for r/{subredditName}
            </span>
          )}
        </h3>
        <button
          onClick={clearChat}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Clear
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-3">
        {chatHistory.map((chat, index) => (
          <div key={index} className="space-y-2">
            <div className="bg-blue-50 p-3 rounded-lg">
              <p className="text-sm font-medium text-blue-900">You:</p>
              <p className="text-sm text-blue-800">{chat.query}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-sm font-medium text-gray-900">AI:</p>
              <p className="text-sm text-gray-800 mb-2">{chat.response.response}</p>

              {/* Citations */}
              {chat.response.citations && chat.response.citations.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs font-medium text-gray-600 mb-1">Sources:</p>
                  <div className="space-y-1">
                    {chat.response.citations.map((citation, idx) => (
                      <div key={idx} className="text-xs text-gray-600 bg-white p-2 rounded border">
                        <p className="font-medium">{citation.post_title}</p>
                        <p className="text-gray-500">{citation.excerpt}</p>
                        <p className="text-gray-400">Relevance: {Math.round(citation.relevance_score * 100)}%</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Current Response */}
        {response && (
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-sm font-medium text-gray-900">AI:</p>
            <p className="text-sm text-gray-800 mb-2">{response.response}</p>

            {/* Citations */}
            {response.citations && response.citations.length > 0 && (
              <div className="mt-2">
                <p className="text-xs font-medium text-gray-600 mb-1">Sources:</p>
                <div className="space-y-1">
                  {response.citations.map((citation, idx) => (
                    <div key={idx} className="text-xs text-gray-600 bg-white p-2 rounded border">
                      <p className="font-medium">{citation.post_title}</p>
                      <p className="text-gray-500">{citation.excerpt}</p>
                      <p className="text-gray-400">Relevance: {Math.round(citation.relevance_score * 100)}%</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {isLoading && (
          <div className="flex items-center justify-center py-4">
            <LoadingSpinner size="sm" />
            <span className="ml-2 text-sm text-gray-500">AI is thinking...</span>
          </div>
        )}
      </div>

      {/* Query Form */}
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask the AI about posts, topics, or anything..."
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Ask
        </button>
      </form>
    </div>
  );
};

export default AICompanion;
