import React, { useState } from 'react';
import { postsApi, aiApi } from '../../services/api';
import { Subreddit } from '../../types';
import LoadingSpinner from '../common/LoadingSpinner';

interface CreatePostProps {
  subreddit?: Subreddit;
  onPostCreated?: () => void;
}

const CreatePost: React.FC<CreatePostProps> = ({ subreddit, onPostCreated }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [postType, setPostType] = useState('text');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [moderationResult, setModerationResult] = useState<any>(null);
  const [showModeration, setShowModeration] = useState(false);
  const [aiDetectionResult, setAiDetectionResult] = useState<any>(null);
  const [showAiDetection, setShowAiDetection] = useState(false);
  const [isDetectingAI, setIsDetectingAI] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;

    setIsSubmitting(true);
    try {
      const postData = {
        title: title.trim(),
        content: content.trim(),
        subreddit_id: subreddit?.id || 1, // Default to first subreddit
        post_type: postType,
      };

      await postsApi.createPost(postData);

      // Reset form
      setTitle('');
      setContent('');
      setModerationResult(null);
      setShowModeration(false);

      if (onPostCreated) {
        onPostCreated();
      }
    } catch (error) {
      console.error('Error creating post:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleModerateContent = async () => {
    if (!content.trim()) return;

    try {
      const result = await aiApi.moderateContent({
        content: content.trim(),
        content_type: 'post',
        subreddit_id: subreddit?.id,
      });
      setModerationResult(result);
      setShowModeration(true);
    } catch (error) {
      console.error('Error moderating content:', error);
    }
  };

  const handleDetectAI = async () => {
    if (!content.trim()) return;

    setIsDetectingAI(true);
    try {
      const result = await aiApi.detectContent({
        content: content.trim(),
        content_type: 'post',
      });

      setAiDetectionResult(result);
      setShowAiDetection(true);
    } catch (error) {
      console.error('Error detecting AI content:', error);
      setAiDetectionResult({
        is_ai_generated: false,
        confidence: 0,
        recommendations: [{ action: 'error', reason: 'AI detection failed' }]
      });
      setShowAiDetection(true);
    } finally {
      setIsDetectingAI(false);
    }
  };

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-4">Create a Post</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Post Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Post Type
          </label>
          <select
            value={postType}
            onChange={(e) => setPostType(e.target.value)}
            className="input"
          >
            <option value="text">Text</option>
            <option value="link">Link</option>
            <option value="image">Image</option>
          </select>
        </div>

        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Title *
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="An interesting title"
            className="input"
            required
          />
        </div>

        {/* Content */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Content *
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="What would you like to say?"
            rows={6}
            className="textarea"
            required
          />
        </div>

        {/* AI Tools */}
        <div className="flex space-x-2">
          <button
            type="button"
            onClick={handleModerateContent}
            className="btn-secondary text-sm"
            disabled={!content.trim()}
          >
            🤖 Moderate Content
          </button>
          <button
            type="button"
            onClick={handleDetectAI}
            className="btn-secondary text-sm"
            disabled={!content.trim() || isDetectingAI}
          >
            {isDetectingAI ? '🔍 Detecting...' : '🔍 Detect AI'}
          </button>
        </div>

        {/* Moderation Results */}
        {showModeration && moderationResult && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <h4 className="font-medium text-blue-900 mb-2">Content Moderation Results</h4>
            <div className="text-sm text-blue-800">
              <p className="mb-2">
                <strong>Approved:</strong> {moderationResult.approved ? '✅ Yes' : '❌ No'}
              </p>

              {moderationResult.suggestions && moderationResult.suggestions.length > 0 && (
                <div className="mb-2">
                  <strong>Suggestions:</strong>
                  <ul className="list-disc list-inside ml-2">
                    {moderationResult.suggestions.map((suggestion: any, index: number) => (
                      <li key={index} className="text-xs">
                        {suggestion.suggestion}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {moderationResult.rule_violations && moderationResult.rule_violations.length > 0 && (
                <div>
                  <strong>Rule Violations:</strong>
                  <ul className="list-disc list-inside ml-2">
                    {moderationResult.rule_violations.map((violation: any, index: number) => (
                      <li key={index} className="text-xs text-red-600">
                        {violation.description}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* AI Detection Results */}
        {showAiDetection && aiDetectionResult && (
          <div className={`border rounded-md p-4 ${
            aiDetectionResult.is_ai_generated
              ? 'bg-yellow-50 border-yellow-200'
              : 'bg-green-50 border-green-200'
          }`}>
            <h4 className={`font-medium mb-2 ${
              aiDetectionResult.is_ai_generated
                ? 'text-yellow-900'
                : 'text-green-900'
            }`}>
              {aiDetectionResult.is_ai_generated ? '⚠️ AI Content Detected' : '✅ Human Content Detected'}
            </h4>
            <div className={`text-sm ${
              aiDetectionResult.is_ai_generated
                ? 'text-yellow-800'
                : 'text-green-800'
            }`}>
              <p className="mb-2">
                <strong>Confidence:</strong> {Math.round(aiDetectionResult.confidence * 100)}%
              </p>

              {aiDetectionResult.detection_methods && aiDetectionResult.detection_methods.length > 0 && (
                <div className="mb-2">
                  <strong>Detection Methods:</strong>
                  <ul className="list-disc list-inside ml-2">
                    {aiDetectionResult.detection_methods.map((method: any, index: number) => (
                      <li key={index} className="text-xs">
                        {method.indicator}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {aiDetectionResult.recommendations && aiDetectionResult.recommendations.length > 0 && (
                <div>
                  <strong>Recommendations:</strong>
                  <ul className="list-disc list-inside ml-2">
                    {aiDetectionResult.recommendations.map((rec: any, index: number) => (
                      <li key={index} className="text-xs">
                        <strong>{rec.action}:</strong> {rec.reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end space-x-2">
          <button
            type="button"
            onClick={() => {
              setTitle('');
              setContent('');
              setModerationResult(null);
              setShowModeration(false);
            }}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting || !title.trim() || !content.trim()}
            className="btn-primary flex items-center space-x-2"
          >
            {isSubmitting && <LoadingSpinner size="sm" />}
            <span>{isSubmitting ? 'Creating...' : 'Create Post'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreatePost;
