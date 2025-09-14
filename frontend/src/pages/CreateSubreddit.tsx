import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { subredditsApi, aiApi } from '../services/api';
import { AutoConfigResponse } from '../types';
import LoadingSpinner from '../components/common/LoadingSpinner';

const CreateSubreddit: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [topics, setTopics] = useState<string[]>([]);
  const [moderationStyle, setModerationStyle] = useState('moderate');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAutoConfiguring, setIsAutoConfiguring] = useState(false);
  const [autoConfig, setAutoConfig] = useState<AutoConfigResponse | null>(null);
  const [newTopic, setNewTopic] = useState('');

  const handleAddTopic = () => {
    if (newTopic.trim() && !topics.includes(newTopic.trim())) {
      setTopics([...topics, newTopic.trim()]);
      setNewTopic('');
    }
  };

  const handleRemoveTopic = (topicToRemove: string) => {
    setTopics(topics.filter(topic => topic !== topicToRemove));
  };

  const handleAutoConfigure = async () => {
    if (!name.trim() || !description.trim()) {
      alert('Please enter a name and description first');
      return;
    }

    setIsAutoConfiguring(true);
    try {
      const result = await aiApi.autoConfigSubreddit({
        name: name.trim(),
        description: description.trim(),
        topics: topics,
        moderation_style: moderationStyle,
      });
      setAutoConfig(result);
    } catch (error) {
      console.error('Error auto-configuring subreddit:', error);
      alert('Error auto-configuring subreddit. Please try again.');
    } finally {
      setIsAutoConfiguring(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !description.trim()) return;

    setIsSubmitting(true);
    try {
      const subredditData = {
        name: name.trim().toLowerCase().replace(/[^a-z0-9_]/g, ''),
        display_name: autoConfig?.display_name || name.trim(),
        description: autoConfig?.description || description.trim(),
        rules: autoConfig?.rules ? JSON.stringify(autoConfig.rules) : undefined,
        auto_configure: false,
      };

      const response = await subredditsApi.createSubreddit(subredditData);
      navigate(`/r/${response.name}`);
    } catch (error) {
      console.error('Error creating subreddit:', error);
      alert('Error creating subreddit. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Create a Subreddit</h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Name *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="subreddit_name"
                className="input"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Only letters, numbers, and underscores allowed
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Moderation Style
              </label>
              <select
                value={moderationStyle}
                onChange={(e) => setModerationStyle(e.target.value)}
                className="input"
              >
                <option value="lenient">Lenient</option>
                <option value="moderate">Moderate</option>
                <option value="strict">Strict</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what this subreddit is about..."
              rows={4}
              className="textarea"
              required
            />
          </div>

          {/* Topics */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Topics
            </label>
            <div className="flex space-x-2 mb-2">
              <input
                type="text"
                value={newTopic}
                onChange={(e) => setNewTopic(e.target.value)}
                placeholder="Add a topic..."
                className="flex-1 input"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTopic())}
              />
              <button
                type="button"
                onClick={handleAddTopic}
                className="btn-secondary"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {topics.map((topic, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                >
                  {topic}
                  <button
                    type="button"
                    onClick={() => handleRemoveTopic(topic)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* AI Auto-Configuration */}
          <div className="border-t pt-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                🤖 AI Auto-Configuration
              </h3>
              <button
                type="button"
                onClick={handleAutoConfigure}
                disabled={isAutoConfiguring || !name.trim() || !description.trim()}
                className="btn-primary flex items-center space-x-2"
              >
                {isAutoConfiguring && <LoadingSpinner size="sm" />}
                <span>
                  {isAutoConfiguring ? 'Configuring...' : 'Auto-Configure'}
                </span>
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Let AI generate rules, guidelines, and settings for your subreddit based on your description and topics.
            </p>

            {autoConfig && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-4">
                <div>
                  <h4 className="font-medium text-blue-900 mb-2">Generated Display Name:</h4>
                  <p className="text-blue-800">{autoConfig.display_name}</p>
                </div>

                <div>
                  <h4 className="font-medium text-blue-900 mb-2">Enhanced Description:</h4>
                  <p className="text-blue-800">{autoConfig.description}</p>
                </div>

                <div>
                  <h4 className="font-medium text-blue-900 mb-2">Generated Rules:</h4>
                  <ul className="list-disc list-inside space-y-2 text-blue-800">
                    {autoConfig.rules.map((rule, index) => (
                      <li key={index} className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <strong>{rule.title}:</strong>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            rule.severity === 'critical' ? 'bg-red-100 text-red-800' :
                            rule.severity === 'high' ? 'bg-red-100 text-red-800' :
                            rule.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {rule.severity}
                          </span>
                          <span className={`px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-700`}>
                            {rule.category}
                          </span>
                        </div>
                        <p className="text-sm ml-4">{rule.description}</p>
                        {rule.examples && rule.examples.length > 0 && (
                          <div className="ml-4 text-xs text-gray-600">
                            <strong>Examples:</strong> {rule.examples.join(', ')}
                          </div>
                        )}
                        {rule.rationale && (
                          <div className="ml-4 text-xs text-gray-600">
                            <strong>Rationale:</strong> {rule.rationale}
                          </div>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="font-medium text-blue-900 mb-2">Moderation Guidelines:</h4>
                  <div className="space-y-3 text-blue-800 text-sm">
                    <div>
                      <strong>General Approach:</strong>
                      <p className="ml-2">{autoConfig.moderation_guidelines.general_approach}</p>
                    </div>
                    <div>
                      <strong>Content Standards:</strong>
                      <p className="ml-2">{autoConfig.moderation_guidelines.content_standards}</p>
                    </div>
                    <div>
                      <strong>User Behavior Expectations:</strong>
                      <p className="ml-2">{autoConfig.moderation_guidelines.user_behavior_expectations}</p>
                    </div>
                    <div>
                      <strong>Enforcement Strategy:</strong>
                      <p className="ml-2">{autoConfig.moderation_guidelines.enforcement_strategy}</p>
                    </div>
                    <div>
                      <strong>Appeal Process:</strong>
                      <p className="ml-2">{autoConfig.moderation_guidelines.appeal_process}</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-blue-900 mb-2">Auto-Moderation Settings:</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm text-blue-800">
                    {Object.entries(autoConfig.auto_moderation_settings).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                        <span className="font-medium">
                          {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-blue-900 mb-2">Community Settings:</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm text-blue-800">
                    {Object.entries(autoConfig.community_settings).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                        <span className="font-medium">
                          {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-blue-900 mb-2">Additional Information:</h4>
                  <div className="space-y-2 text-sm text-blue-800">
                    <div>
                      <strong>Community Type:</strong> {autoConfig.community_type}
                    </div>
                    <div>
                      <strong>Estimated Activity Level:</strong> {autoConfig.estimated_activity_level}
                    </div>
                    {autoConfig.suggested_tags.length > 0 && (
                      <div>
                        <strong>Suggested Tags:</strong>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {autoConfig.suggested_tags.map((tag, index) => (
                            <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {autoConfig.configuration_notes && (
                      <div>
                        <strong>Configuration Notes:</strong>
                        <p className="ml-2 text-gray-600">{autoConfig.configuration_notes}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !name.trim() || !description.trim()}
              className="btn-primary flex items-center space-x-2"
            >
              {isSubmitting && <LoadingSpinner size="sm" />}
              <span>{isSubmitting ? 'Creating...' : 'Create Subreddit'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateSubreddit;
