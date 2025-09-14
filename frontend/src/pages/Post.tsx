import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { postsApi, commentsApi } from '../services/api';
import { Post, Comment } from '../types';
import LoadingSpinner from '../components/common/LoadingSpinner';

const PostDetail: React.FC = () => {
  const { postId } = useParams<{ postId: string }>();
  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);

  useEffect(() => {
    if (postId) {
      fetchPost();
      fetchComments();
    }
  }, [postId]);

  const fetchPost = async () => {
    if (!postId) return;

    try {
      const response = await postsApi.getPost(parseInt(postId));
      setPost(response);
    } catch (error) {
      console.error('Error fetching post:', error);
    }
  };

  const fetchComments = async () => {
    if (!postId) return;

    try {
      setLoading(true);
      const response = await commentsApi.getComments(parseInt(postId));
      setComments(response);
    } catch (error) {
      console.error('Error fetching comments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim() || !postId) return;

    setSubmittingComment(true);
    try {
      await commentsApi.createComment(parseInt(postId), {
        content: newComment.trim(),
      });
      setNewComment('');
      fetchComments(); // Refresh comments
    } catch (error) {
      console.error('Error creating comment:', error);
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleVoteComment = async (commentId: number, type: 'upvote' | 'downvote') => {
    try {
      if (type === 'upvote') {
        await commentsApi.upvoteComment(commentId);
      } else {
        await commentsApi.downvoteComment(commentId);
      }

      // Update local state
      setComments(prevComments =>
        prevComments.map(comment =>
          comment.id === commentId
            ? {
                ...comment,
                upvotes: type === 'upvote' ? comment.upvotes + 1 : comment.upvotes,
                downvotes: type === 'downvote' ? comment.downvotes + 1 : comment.downvotes,
                score: type === 'upvote' ? comment.score + 1 : comment.score - 1,
              }
            : comment
        )
      );
    } catch (error) {
      console.error('Error voting on comment:', error);
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

  const renderComment = (comment: Comment, depth = 0) => (
    <div key={comment.id} className={`${depth > 0 ? 'ml-8' : ''}`}>
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
        <div className="flex">
          {/* Voting */}
          <div className="flex flex-col items-center mr-4 space-y-1">
            <button
              onClick={() => handleVoteComment(comment.id, 'upvote')}
              className="text-gray-400 hover:text-reddit-orange transition-colors"
              aria-label="Upvote"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
              </svg>
            </button>
            <span className="text-xs font-medium text-gray-900">{comment.score}</span>
            <button
              onClick={() => handleVoteComment(comment.id, 'downvote')}
              className="text-gray-400 hover:text-blue-600 transition-colors"
              aria-label="Downvote"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          {/* Comment content */}
          <div className="flex-1">
            <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
              <span>u/{comment.author.username}</span>
              <span>•</span>
              <span>{formatTimeAgo(comment.created_at)}</span>
              {comment.is_ai_generated && (
                <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
                  AI Generated
                </span>
              )}
            </div>
            <p className="text-gray-900">{comment.content}</p>
          </div>
        </div>
      </div>

      {/* Replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="space-y-2">
          {comment.replies.map((reply) => renderComment(reply, depth + 1))}
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!post) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Post Not Found</h1>
        <p className="text-gray-500">The post you're looking for doesn't exist.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Post */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
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
            <span className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
              AI Generated
            </span>
          )}
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-4">{post.title}</h1>

        <div className="text-gray-700 mb-6 whitespace-pre-wrap">
          {post.content}
        </div>

        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <button className="flex items-center space-x-1 hover:text-reddit-blue transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <span>{post.comment_count} comments</span>
          </button>
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

      {/* Comment Form */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Add a Comment</h3>
        <form onSubmit={handleSubmitComment}>
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="What are your thoughts?"
            rows={4}
            className="textarea w-full mb-4"
            required
          />
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={submittingComment || !newComment.trim()}
              className="btn-primary flex items-center space-x-2"
            >
              {submittingComment && <LoadingSpinner size="sm" />}
              <span>{submittingComment ? 'Posting...' : 'Post Comment'}</span>
            </button>
          </div>
        </form>
      </div>

      {/* Comments */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {comments.length} Comments
        </h3>
        {comments.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">No comments yet. Be the first to comment!</p>
          </div>
        ) : (
          comments.map((comment) => renderComment(comment))
        )}
      </div>
    </div>
  );
};

export default PostDetail;
