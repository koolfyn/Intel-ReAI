import React from 'react';
import { Link } from 'react-router-dom';
import { Post } from '../../types';
import { postsApi } from '../../services/api';

interface PostCardProps {
  post: Post;
  onVote?: (postId: number, type: 'upvote' | 'downvote') => void;
}

const PostCard: React.FC<PostCardProps> = ({ post, onVote }) => {
  const handleUpvote = async () => {
    try {
      await postsApi.upvotePost(post.id);
      if (onVote) onVote(post.id, 'upvote');
    } catch (error) {
      console.error('Error upvoting post:', error);
    }
  };

  const handleDownvote = async () => {
    try {
      await postsApi.downvotePost(post.id);
      if (onVote) onVote(post.id, 'downvote');
    } catch (error) {
      console.error('Error downvoting post:', error);
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

    if (diffInHours < 1) return 'now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex">
        {/* Voting */}
        <div className="flex flex-col items-center mr-4 space-y-1">
          <button
            onClick={handleUpvote}
            className="text-gray-400 hover:text-reddit-orange transition-colors"
            aria-label="Upvote"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
          </button>
          <span className="text-sm font-medium text-gray-900">{post.score}</span>
          <button
            onClick={handleDownvote}
            className="text-gray-400 hover:text-blue-600 transition-colors"
            aria-label="Downvote"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Post header */}
          <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
            <Link
              to={`/r/${post.subreddit.name}`}
              className="font-medium text-reddit-blue hover:underline"
            >
              r/{post.subreddit.name}
            </Link>
            <span>•</span>
            <span>Posted by u/{post.author.username}</span>
            <span>•</span>
            <span>{formatTimeAgo(post.created_at)}</span>
            {post.is_ai_generated && (
              <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full flex items-center space-x-1">
                <span>🤖</span>
                <span>AI Generated</span>
                {post.ai_confidence && (
                  <span className="text-yellow-600">
                    ({post.ai_confidence}%)
                  </span>
                )}
              </span>
            )}
          </div>

          {/* Post title */}
          <Link to={`/posts/${post.id}`} className="block">
            <h3 className="text-lg font-medium text-gray-900 hover:text-reddit-blue transition-colors mb-2">
              {post.title}
            </h3>
          </Link>

          {/* Post content preview */}
          <div className="text-gray-700 mb-3">
            {post.content.length > 200
              ? `${post.content.substring(0, 200)}...`
              : post.content
            }
            {post.is_ai_generated && (
              <div className="mt-2 p-2 bg-yellow-50 border-l-4 border-yellow-400 rounded-r">
                <p className="text-xs text-yellow-800 flex items-center space-x-1">
                  <span>⚠️</span>
                  <span>This content was detected as AI-generated with {post.ai_confidence || 'unknown'}% confidence</span>
                </p>
              </div>
            )}
          </div>

          {/* Post footer */}
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <Link
              to={`/posts/${post.id}`}
              className="flex items-center space-x-1 hover:text-reddit-blue transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <span>{post.comment_count} comments</span>
            </Link>
            <button className="flex items-center space-x-1 hover:text-reddit-blue transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
              </svg>
              <span>Share</span>
            </button>
            <button className="flex items-center space-x-1 hover:text-reddit-blue transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
              <span>Save</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostCard;
