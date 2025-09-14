import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { MagnifyingGlassIcon, PlusIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import SearchBar from '../common/SearchBar';

interface HeaderProps {
  onToggleAICompanion: () => void;
  isAICompanionOpen: boolean;
}

const Header: React.FC<HeaderProps> = ({ onToggleAICompanion, isAICompanionOpen }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (query: string) => {
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query)}`);
    }
  };

  return (
    <header className="bg-white border-b border-reddit-border sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-reddit-orange rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-sm">AI</span>
            </div>
            <span className="text-xl font-bold text-reddit-dark">AI Reddit</span>
          </Link>

          {/* Search Bar */}
          <div className="flex-1 max-w-2xl mx-8">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              onSearch={handleSearch}
              placeholder="Search posts, subreddits, and more..."
            />
          </div>

          {/* Navigation */}
          <div className="flex items-center space-x-4">
            <Link
              to="/create-subreddit"
              className="flex items-center space-x-1 text-gray-600 hover:text-reddit-blue transition-colors"
            >
              <PlusIcon className="w-5 h-5" />
              <span className="hidden sm:inline">Create Subreddit</span>
            </Link>

            {/* AI Companion Toggle */}
            <button
              onClick={onToggleAICompanion}
              className={`flex items-center space-x-1 px-3 py-2 rounded-lg transition-colors ${
                isAICompanionOpen
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50'
              }`}
            >
              <ChatBubbleLeftRightIcon className="w-5 h-5" />
              <span className="hidden sm:inline">AI Companion</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
