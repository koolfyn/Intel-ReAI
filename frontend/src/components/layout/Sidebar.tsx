import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { subredditsApi } from '../../services/api';
import { Subreddit } from '../../types';

const Sidebar: React.FC = () => {
  const [subreddits, setSubreddits] = useState<Subreddit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSubreddits = async () => {
      try {
        const response = await subredditsApi.getSubreddits(1, 10);
        setSubreddits(response.subreddits);
      } catch (error) {
        console.error('Error fetching subreddits:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSubreddits();
  }, []);

  return (
    <aside className="w-64 bg-white border-r border-reddit-border min-h-screen p-4">
      <div className="space-y-6">
        {/* Quick Links */}
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Quick Links
          </h3>
          <nav className="space-y-2">
            <Link
              to="/"
              className="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            >
              🏠 Home
            </Link>
            <Link
              to="/?sort=hot"
              className="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            >
              🔥 Hot
            </Link>
            <Link
              to="/?sort=new"
              className="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            >
              🆕 New
            </Link>
            <Link
              to="/?sort=top"
              className="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            >
              ⬆️ Top
            </Link>
          </nav>
        </div>

        {/* Subreddits */}
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Subreddits
          </h3>
          {loading ? (
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-8 bg-gray-200 rounded animate-pulse" />
              ))}
            </div>
          ) : (
            <nav className="space-y-1">
              {subreddits.map((subreddit) => (
                <Link
                  key={subreddit.id}
                  to={`/r/${subreddit.name}`}
                  className="block px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span>r/{subreddit.name}</span>
                    <span className="text-xs text-gray-500">
                      {subreddit.post_count}
                    </span>
                  </div>
                </Link>
              ))}
            </nav>
          )}
        </div>

        {/* AI Features */}
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
            AI Features
          </h3>
          <nav className="space-y-2">
            <div className="px-3 py-2 text-sm text-gray-700 bg-blue-50 rounded-md">
              🤖 AI Companion
            </div>
            <div className="px-3 py-2 text-sm text-gray-700 bg-green-50 rounded-md">
              ✅ Content Moderation
            </div>
            <div className="px-3 py-2 text-sm text-gray-700 bg-purple-50 rounded-md">
              🔍 Content Detection
            </div>
            <div className="px-3 py-2 text-sm text-gray-700 bg-orange-50 rounded-md">
              ⚙️ Auto Configuration
            </div>
          </nav>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
