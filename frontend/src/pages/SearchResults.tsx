import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import PostCard from '../components/posts/PostCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { searchApi } from '../services/api';
import { SearchResponse } from '../types';

const SearchResults: React.FC = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sort, setSort] = useState('relevance');
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (query) {
      performSearch();
    }
  }, [query, sort, page]); // eslint-disable-line react-hooks/exhaustive-deps

  const performSearch = async () => {
    if (!query.trim()) return;

    try {
      setLoading(true);
      setError(null);
      const response = await searchApi.searchPosts(query, undefined, sort, page, 20);
      setSearchResults(response);
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to perform search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSortChange = (newSort: string) => {
    setSort(newSort);
    setPage(1);
  };

  const handleLoadMore = () => {
    if (searchResults && page < searchResults.pagination.pages) {
      setPage(page + 1);
    }
  };

  if (!query) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Search</h1>
          <p className="text-gray-600">Enter a search term to find posts and subreddits.</p>
        </div>
      </div>
    );
  }

  if (loading && !searchResults) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex justify-center">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Search Error</h1>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={performSearch}
            className="bg-reddit-blue text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Search Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Search Results for "{query}"
        </h1>
        {searchResults && (
          <p className="text-gray-600">
            Found {searchResults.pagination.total} result{searchResults.pagination.total !== 1 ? 's' : ''}
          </p>
        )}
      </div>

      {/* Sort Options */}
      <div className="mb-6 flex items-center space-x-4">
        <span className="text-sm font-medium text-gray-700">Sort by:</span>
        <div className="flex space-x-2">
          {[
            { value: 'relevance', label: 'Relevance' },
            { value: 'date', label: 'Newest' },
            { value: 'score', label: 'Top' }
          ].map((option) => (
            <button
              key={option.value}
              onClick={() => handleSortChange(option.value)}
              className={`px-3 py-1 text-sm rounded-md transition-colors ${
                sort === option.value
                  ? 'bg-reddit-blue text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Search Results */}
      {searchResults && searchResults.results.length > 0 ? (
        <div className="space-y-4">
          {searchResults.results.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}

          {/* Load More Button */}
          {page < searchResults.pagination.pages && (
            <div className="text-center mt-8">
              <button
                onClick={handleLoadMore}
                disabled={loading}
                className="bg-gray-200 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-300 transition-colors disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Load More'}
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
          <p className="text-gray-600">
            Try searching with different keywords or check your spelling.
          </p>
        </div>
      )}
    </div>
  );
};

export default SearchResults;
