import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import PostCard from '../components/posts/PostCard';
import CreatePost from '../components/posts/CreatePost';
import AICompanion from '../components/ai/AICompanion';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { postsApi, subredditsApi, aiApi } from '../services/api';
import { Post, Subreddit as SubredditType } from '../types';

const Subreddit: React.FC = () => {
  const { subredditName } = useParams<{ subredditName: string }>();
  const [subreddit, setSubreddit] = useState<SubredditType | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreatePost, setShowCreatePost] = useState(false);
  const [faq, setFaq] = useState<any[]>([]);
  const [trendingTopics, setTrendingTopics] = useState<any[]>([]);

  const fetchSubreddit = useCallback(async () => {
    if (!subredditName) return;

    try {
      const response = await subredditsApi.getSubreddit(subredditName);
      setSubreddit(response);
    } catch (error) {
      console.error('Error fetching subreddit:', error);
    }
  }, [subredditName]);

  const fetchPosts = useCallback(async () => {
    if (!subredditName) return;

    try {
      setLoading(true);
      const response = await postsApi.getPosts(1, 20, subreddit?.id);
      setPosts(response.posts);
    } catch (error) {
      console.error('Error fetching posts:', error);
    } finally {
      setLoading(false);
    }
  }, [subredditName, subreddit?.id]);

  const fetchFAQ = useCallback(async () => {
    if (!subredditName) return;

    try {
      const response = await aiApi.getSubredditFAQ(subredditName);
      setFaq(response.faqs || []);
    } catch (error) {
      console.error('Error fetching FAQ:', error);
    }
  }, [subredditName]);

  const fetchTrendingTopics = useCallback(async () => {
    if (!subredditName) return;

    try {
      const response = await aiApi.getTrendingTopics(subredditName);
      setTrendingTopics(response.trending_topics || []);
    } catch (error) {
      console.error('Error fetching trending topics:', error);
    }
  }, [subredditName]);

  useEffect(() => {
    if (subredditName) {
      fetchSubreddit();
      fetchPosts();
      fetchFAQ();
      fetchTrendingTopics();
    }
  }, [subredditName, fetchSubreddit, fetchPosts, fetchFAQ, fetchTrendingTopics]);

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

  if (!subreddit) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Subreddit Not Found</h1>
        <p className="text-gray-500">The subreddit "r/{subredditName}" does not exist.</p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Subreddit Header */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  r/{subreddit.name}
                </h1>
                <p className="text-gray-600 mt-1">
                  {subreddit.display_name}
                </p>
              </div>
              <button
                onClick={() => setShowCreatePost(!showCreatePost)}
                className="btn-primary"
              >
                {showCreatePost ? 'Cancel' : 'Create Post'}
              </button>
            </div>

            {subreddit.description && (
              <p className="text-gray-700 mb-4">{subreddit.description}</p>
            )}

            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>{subreddit.post_count} posts</span>
              <span>{subreddit.subscriber_count} members</span>
            </div>
          </div>

          {/* Rules */}
          {subreddit.rules && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Rules</h3>
              <div className="text-sm text-gray-700 whitespace-pre-line">
                {subreddit.rules}
              </div>
            </div>
          )}

          {/* Create Post */}
          {showCreatePost && (
            <CreatePost subreddit={subreddit} onPostCreated={handlePostCreated} />
          )}

          {/* Posts */}
          <div className="space-y-4">
            {posts.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 text-lg">No posts in this subreddit yet</p>
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
        </div>

        {/* Right Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* AI Companion */}
          <AICompanion subredditId={subreddit.id} subredditName={subreddit.name} />

          {/* FAQ */}
          {faq.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                🤖 AI-Generated FAQ
              </h3>
              <div className="space-y-3">
                {faq.map((item, index) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-3">
                    <p className="font-medium text-gray-900 text-sm">
                      {item.question}
                    </p>
                    <p className="text-gray-600 text-xs mt-1">
                      {item.answer}
                    </p>
                    <span className="inline-block mt-1 px-2 py-1 bg-gray-100 text-xs text-gray-600 rounded-full">
                      {item.category}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Trending Topics */}
          {trendingTopics.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                🔥 Trending Topics
              </h3>
              <div className="space-y-2">
                {trendingTopics.map((topic, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900 text-sm">
                        {topic.topic}
                      </p>
                      <p className="text-gray-600 text-xs">
                        {topic.description}
                      </p>
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                      <span className="text-xs text-gray-500">
                        {topic.frequency}/10
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Subreddit;
