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

  // Enhanced configuration fields
  const [briefDescription, setBriefDescription] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [contentTypes, setContentTypes] = useState<string[]>([]);
  const [communityGoals, setCommunityGoals] = useState('');
  const [moderationPhilosophy, setModerationPhilosophy] = useState('');
  const [language, setLanguage] = useState('en');
  const [ageRestriction, setAgeRestriction] = useState('all');
  const [contentRating, setContentRating] = useState('general');

  const contentTypeOptions = [
    'text', 'image', 'link', 'video', 'poll', 'discussion', 'question', 'announcement'
  ];

  const handleAddTopic = () => {
    if (newTopic.trim() && !topics.includes(newTopic.trim())) {
      setTopics([...topics, newTopic.trim()]);
      setNewTopic('');
    }
  };

  const handleRemoveTopic = (topicToRemove: string) => {
    setTopics(topics.filter(topic => topic !== topicToRemove));
  };

  const handleContentTypeToggle = (contentType: string) => {
    if (contentTypes.includes(contentType)) {
      setContentTypes(contentTypes.filter(type => type !== contentType));
    } else {
      setContentTypes([...contentTypes, contentType]);
    }
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
        brief_description: briefDescription || undefined,
        target_audience: targetAudience || undefined,
        content_types: contentTypes.length > 0 ? contentTypes : undefined,
        community_goals: communityGoals || undefined,
        moderation_philosophy: moderationPhilosophy || undefined,
        language: language,
        age_restriction: ageRestriction,
        content_rating: contentRating,
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

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getEnforcementColor = (level: string) => {
    switch (level) {
      case 'ban':
        return 'bg-red-100 text-red-800';
      case 'removal':
        return 'bg-orange-100 text-orange-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'mute':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white border border-gray-200 rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Create a Subreddit</h1>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information Section */}
          <div className="bg-gray-50 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Basic Information</h2>
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
                  <option value="lenient">Lenient - Light moderation, focus on harmful content</option>
                  <option value="moderate">Moderate - Balanced approach to content quality</option>
                  <option value="strict">Strict - High standards, strict rule enforcement</option>
                </select>
              </div>
            </div>

            <div className="mt-6">
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
          </div>

          {/* Enhanced Configuration Section */}
          <div className="bg-blue-50 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Enhanced Configuration (Optional)</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Brief Description
                </label>
                <input
                  type="text"
                  value={briefDescription}
                  onChange={(e) => setBriefDescription(e.target.value)}
                  placeholder="One-line description for better AI configuration"
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Audience
                </label>
                <input
                  type="text"
                  value={targetAudience}
                  onChange={(e) => setTargetAudience(e.target.value)}
                  placeholder="e.g., developers, students, professionals"
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Community Goals
                </label>
                <input
                  type="text"
                  value={communityGoals}
                  onChange={(e) => setCommunityGoals(e.target.value)}
                  placeholder="e.g., learning, networking, support"
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Moderation Philosophy
                </label>
                <input
                  type="text"
                  value={moderationPhilosophy}
                  onChange={(e) => setModerationPhilosophy(e.target.value)}
                  placeholder="e.g., community-driven, hands-off, educational"
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="input"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="zh">Chinese</option>
                  <option value="ja">Japanese</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Age Restriction
                </label>
                <select
                  value={ageRestriction}
                  onChange={(e) => setAgeRestriction(e.target.value)}
                  className="input"
                >
                  <option value="all">All Ages</option>
                  <option value="13+">13+</option>
                  <option value="18+">18+</option>
                  <option value="21+">21+</option>
                </select>
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Content Types
              </label>
              <div className="flex flex-wrap gap-2">
                {contentTypeOptions.map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => handleContentTypeToggle(type)}
                    className={`px-3 py-1 rounded-full text-sm border ${
                      contentTypes.includes(type)
                        ? 'bg-blue-100 text-blue-800 border-blue-300'
                        : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Topics Section */}
          <div className="bg-green-50 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Topics & Tags</h2>
            <div className="flex space-x-2 mb-4">
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
                Add Topic
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {topics.map((topic, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800 border border-green-200"
                >
                  {topic}
                  <button
                    type="button"
                    onClick={() => handleRemoveTopic(topic)}
                    className="ml-2 text-green-600 hover:text-green-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* AI Auto-Configuration Section */}
          <div className="bg-purple-50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                🤖 AI Auto-Configuration
              </h2>
              <button
                type="button"
                onClick={handleAutoConfigure}
                disabled={isAutoConfiguring || !name.trim() || !description.trim()}
                className="btn-primary flex items-center space-x-2"
              >
                {isAutoConfiguring && <LoadingSpinner size="sm" />}
                <span>
                  {isAutoConfiguring ? 'Configuring...' : 'Generate Configuration'}
                </span>
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-6">
              Let AI generate comprehensive rules, guidelines, and settings for your subreddit based on your description, topics, and preferences.
            </p>

            {autoConfig && (
              <div className="space-y-6">
                {/* Generated Display Name and Description */}
                <div className="bg-white border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900 mb-3">Generated Configuration</h3>
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium text-purple-800 mb-1">Display Name:</h4>
                      <p className="text-purple-700">{autoConfig.display_name}</p>
                    </div>
                    <div>
                      <h4 className="font-medium text-purple-800 mb-1">Enhanced Description:</h4>
                      <p className="text-purple-700">{autoConfig.description}</p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-sm">
                        {autoConfig.community_type}
                      </span>
                      <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-sm">
                        {autoConfig.estimated_activity_level} activity
                      </span>
                    </div>
                  </div>
                </div>

                {/* Rules Section */}
                <div className="bg-white border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900 mb-4">Generated Rules</h3>
                  <div className="space-y-4">
                    {autoConfig.rules.map((rule, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{rule.title}</h4>
                          <div className="flex space-x-2">
                            <span className={`px-2 py-1 text-xs rounded-full border ${getSeverityColor(rule.severity)}`}>
                              {rule.severity}
                            </span>
                            <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-700">
                              {rule.category}
                            </span>
                            <span className={`px-2 py-1 text-xs rounded-full ${getEnforcementColor(rule.enforcement_level)}`}>
                              {rule.enforcement_level}
                            </span>
                          </div>
                        </div>
                        <p className="text-gray-700 text-sm mb-3">{rule.description}</p>

                        {rule.examples && rule.examples.length > 0 && (
                          <div className="mb-2">
                            <h5 className="text-xs font-medium text-gray-600 mb-1">Examples:</h5>
                            <ul className="text-xs text-gray-600 list-disc list-inside">
                              {rule.examples.map((example, idx) => (
                                <li key={idx}>{example}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {rule.exceptions && (
                          <div className="mb-2">
                            <h5 className="text-xs font-medium text-gray-600 mb-1">Exceptions:</h5>
                            <p className="text-xs text-gray-600">{rule.exceptions}</p>
                          </div>
                        )}

                        {rule.rationale && (
                          <div>
                            <h5 className="text-xs font-medium text-gray-600 mb-1">Rationale:</h5>
                            <p className="text-xs text-gray-600">{rule.rationale}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Moderation Guidelines */}
                <div className="bg-white border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900 mb-4">Moderation Guidelines</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium text-purple-800 mb-2">General Approach</h4>
                      <p className="text-sm text-purple-700">{autoConfig.moderation_guidelines.general_approach}</p>
                    </div>
                    <div>
                      <h4 className="font-medium text-purple-800 mb-2">Content Standards</h4>
                      <p className="text-sm text-purple-700">{autoConfig.moderation_guidelines.content_standards}</p>
                    </div>
                    <div>
                      <h4 className="font-medium text-purple-800 mb-2">User Expectations</h4>
                      <p className="text-sm text-purple-700">{autoConfig.moderation_guidelines.user_behavior_expectations}</p>
                    </div>
                    <div>
                      <h4 className="font-medium text-purple-800 mb-2">Enforcement Strategy</h4>
                      <p className="text-sm text-purple-700">{autoConfig.moderation_guidelines.enforcement_strategy}</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <h4 className="font-medium text-purple-800 mb-2">Appeal Process</h4>
                    <p className="text-sm text-purple-700">{autoConfig.moderation_guidelines.appeal_process}</p>
                  </div>
                </div>

                {/* Auto-Moderation Settings */}
                <div className="bg-white border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900 mb-4">Auto-Moderation Settings</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(autoConfig.auto_moderation_settings).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="text-sm capitalize text-gray-700">
                          {key.replace(/_/g, ' ')}:
                        </span>
                        <span className="text-sm font-medium text-gray-900">
                          {typeof value === 'boolean' ? (value ? 'Yes' : 'No') :
                           Array.isArray(value) ? value.join(', ') : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Community Settings */}
                <div className="bg-white border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900 mb-4">Community Settings</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(autoConfig.community_settings).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="text-sm capitalize text-gray-700">
                          {key.replace(/_/g, ' ')}:
                        </span>
                        <span className="text-sm font-medium text-gray-900">
                          {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Additional Information */}
                <div className="bg-white border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900 mb-4">Additional Information</h3>
                  <div className="space-y-3">
                    {autoConfig.suggested_tags.length > 0 && (
                      <div>
                        <h4 className="font-medium text-purple-800 mb-2">Suggested Tags</h4>
                        <div className="flex flex-wrap gap-2">
                          {autoConfig.suggested_tags.map((tag, index) => (
                            <span key={index} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-sm">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {autoConfig.configuration_notes && (
                      <div>
                        <h4 className="font-medium text-purple-800 mb-2">Configuration Notes</h4>
                        <p className="text-sm text-purple-700">{autoConfig.configuration_notes}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4 pt-6 border-t">
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
