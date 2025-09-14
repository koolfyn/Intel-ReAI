import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import PostCard from '../components/posts/PostCard';
import CreatePost from '../components/posts/CreatePost';
import AICompanion from '../components/ai/AICompanion';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { postsApi, subredditsApi } from '../services/api';
import { Post, Subreddit } from '../types';

const Home: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [posts, setPosts] = useState<Post[]>([]);
  const [subreddits, setSubreddits] = useState<Subreddit[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [sort, setSort] = useState(searchParams.get('sort') || 'hot');
  const [showCreatePost, setShowCreatePost] = useState(false);

  useEffect(() => {
    fetchPosts();
    fetchSubreddits();
  }, [sort]);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const response = await postsApi.getPosts(page, 20, undefined, sort);
      setPosts(response.posts);
      setHasMore(response.pagination.page < response.pagination.pages);
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSubreddits = async () => {
    try {
      const response = await subredditsApi.getSubreddits(1, 10);
      setSubreddits(response.subreddits);
    } catch (error) {
      console.error('Error fetching subreddits:', error);
    }
  };

  const handleVote = (postId: number, type: 'upvote' | 'downvote') => {
    setPosts(prevPosts =>
      prevPosts.map(post =>
        post.id === postId
          ? {
              ...post,
              upvotes: type === 'upvote' ? post.upvotes + 1 : post.upvotes,
              downvotes: type === 'downvote' ? post.downvotes + 1 : post.downvotes,
              score: type === 'upvote' ? post.score + 1 : post.score - 1,
            }
          : post
      )
    );
  };

  const handlePostCreated = () => {
    setShowCreatePost(false);
    fetchPosts(); // Refresh posts
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">Home</h1>
              <div className="flex space-x-2">
                <button
                  onClick={() => setSort('hot')}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    sort === 'hot'
                      ? 'bg-reddit-orange text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  🔥 Hot
                </button>
                <button
                  onClick={() => setSort('new')}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    sort === 'new'
                      ? 'bg-reddit-orange text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  🆕 New
                </button>
                <button
                  onClick={() => setSort('top')}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    sort === 'top'
                      ? 'bg-reddit-orange text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  ⬆️ Top
                </button>
              </div>
            </div>
            <button
              onClick={() => setShowCreatePost(!showCreatePost)}
              className="btn-primary"
            >
              {showCreatePost ? 'Cancel' : 'Create Post'}
            </button>
          </div>

          {/* Create Post */}
          {showCreatePost && (
            <CreatePost onPostCreated={handlePostCreated} />
          )}

          {/* Posts */}
          <div className="space-y-4">
            {posts.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No posts found</p>
                <p className="text-gray-400 text-sm mt-2">
                  Be the first to create a post!
                </p>
              </div>
            ) : (
              posts.map((post) => (
                <PostCard
                  key={post.id}
                  post={post}
                  onVote={handleVote}
                />
              ))
            )}
          </div>

          {/* Load More */}
          {hasMore && (
            <div className="text-center">
              <button
                onClick={() => {
                  setPage(prev => prev + 1);
                  // TODO: Implement load more functionality
                }}
                className="btn-secondary"
              >
                Load More
              </button>
            </div>
          )}
        </div>

        {/* Right Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* AI Companion */}
          <AICompanion />

          {/* Popular Subreddits */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Popular Subreddits
            </h3>
            <div className="space-y-2">
              {subreddits.map((subreddit) => (
                <div
                  key={subreddit.id}
                  className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-md transition-colors"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      r/{subreddit.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      {subreddit.post_count} posts
                    </p>
                  </div>
                  <button className="text-sm text-blue-600 hover:text-blue-800">
                    Join
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* AI Features Info */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              🤖 AI Features
            </h3>
            <div className="space-y-2 text-sm text-gray-700">
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span>Content Moderation</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                <span>AI Companion</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                <span>Content Detection</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                <span>Auto Configuration</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
