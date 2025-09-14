export interface User {
  id: number;
  username: string;
  display_name?: string;
  email: string;
  bio?: string;
  created_at: string;
  updated_at?: string;
}

export interface Subreddit {
  id: number;
  name: string;
  display_name: string;
  description?: string;
  rules?: string;
  created_by: number;
  created_at: string;
  updated_at?: string;
  post_count: number;
  subscriber_count: number;
}

export interface Post {
  id: number;
  title: string;
  content: string;
  post_type: string;
  author: User;
  subreddit: Subreddit;
  upvotes: number;
  downvotes: number;
  score: number;
  comment_count: number;
  is_ai_generated: boolean;
  ai_confidence?: number;
  created_at: string;
  updated_at?: string;
}

export interface Comment {
  id: number;
  content: string;
  author: User;
  post_id: number;
  parent_id?: number;
  upvotes: number;
  downvotes: number;
  score: number;
  is_ai_generated: boolean;
  ai_confidence?: number;
  created_at: string;
  updated_at?: string;
  replies: Comment[];
}

export interface Pagination {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface PostsResponse {
  posts: Post[];
  pagination: Pagination;
}

export interface SubredditsResponse {
  subreddits: Subreddit[];
  pagination: Pagination;
}

export interface SearchResponse {
  query: string;
  results: Post[];
  pagination: Pagination;
}

export interface AIQueryRequest {
  query: string;
  subreddit_id?: number;
  context?: string;
}

export interface AIQueryResponse {
  response: string;
  citations: Array<{
    post_id: number;
    post_title: string;
    relevance_score: number;
    excerpt: string;
  }>;
  sources: Array<{
    type: string;
    id: number;
    title: string;
    url: string;
  }>;
}

export interface ContentModerationRequest {
  content: string;
  content_type: string;
  subreddit_id?: number;
}

export interface ContentModerationResponse {
  approved: boolean;
  suggestions: Array<{
    type: string;
    message: string;
    suggestion: string;
    severity: string;
  }>;
  rule_violations: Array<{
    rule: string;
    description: string;
    severity: string;
  }>;
}

export interface AutoConfigRequest {
  name: string;
  description: string;
  topics: string[];
  moderation_style: string;
  // Enhanced fields for better configuration
  brief_description?: string; // User's initial brief description
  target_audience?: string; // Who the subreddit is for
  content_types?: string[]; // Allowed content types (text, image, link, video, etc.)
  community_goals?: string; // What the community aims to achieve
  moderation_philosophy?: string; // User's preferred approach to moderation
  language?: string; // Primary language of the community
  age_restriction?: string; // "all", "13+", "18+", "21+"
  content_rating?: string; // "general", "mature", "adult"
}

export interface RuleItem {
  title: string;
  description: string;
  severity: string; // "low", "medium", "high", "critical"
  category: string; // "behavior", "content", "spam", "safety", "community"
  enforcement_level: string; // "warning", "removal", "ban", "mute"
  examples?: string[];
  exceptions?: string;
  rationale?: string;
}

export interface ModerationGuidelines {
  general_approach: string;
  content_standards: string;
  user_behavior_expectations: string;
  enforcement_strategy: string;
  appeal_process: string;
}

export interface AutoModerationSettings {
  auto_remove_spam: boolean;
  require_approval: boolean;
  content_filters: string[];
  min_account_age_hours: number;
  min_karma_required: number;
  max_posts_per_hour: number;
  keyword_filters: string[];
  image_moderation: boolean;
  link_validation: boolean;
  duplicate_detection: boolean;
}

export interface CommunitySettings {
  allow_images: boolean;
  allow_videos: boolean;
  allow_links: boolean;
  allow_polls: boolean;
  allow_live_chat: boolean;
  post_approval_required: boolean;
  comment_approval_required: boolean;
  user_flair_enabled: boolean;
  post_flair_enabled: boolean;
  wiki_enabled: boolean;
  events_enabled: boolean;
}

export interface AutoConfigResponse {
  display_name: string;
  description: string;
  rules: RuleItem[];
  moderation_guidelines: ModerationGuidelines;
  auto_moderation_settings: AutoModerationSettings;
  community_settings: CommunitySettings;
  suggested_tags: string[];
  community_type: string; // "discussion", "support", "hobby", "professional", "entertainment"
  estimated_activity_level: string; // "low", "medium", "high", "very_high"
  configuration_notes?: string;
}

export interface ContentDetectionRequest {
  content: string;
  content_type: string;
}

export interface ContentDetectionResponse {
  is_ai_generated: boolean;
  confidence: number;
  detection_methods: Array<{
    provider: string;
    confidence: number;
    details: string;
  }>;
  recommendations: Array<{
    action: string;
    reason: string;
  }>;
}
