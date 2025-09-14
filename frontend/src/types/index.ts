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
}

export interface AutoConfigResponse {
  display_name: string;
  description: string;
  rules: Array<{
    title: string;
    description: string;
    severity: string;
  }>;
  moderation_guidelines: string;
  auto_moderation_settings: Record<string, any>;
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
