import axios from 'axios';
import {
  PostsResponse,
  Post,
  SubredditsResponse,
  Subreddit,
  Comment,
  SearchResponse,
  AIQueryRequest,
  AIQueryResponse,
  ContentModerationRequest,
  ContentModerationResponse,
  AutoConfigRequest,
  AutoConfigResponse,
  ContentDetectionRequest,
  ContentDetectionResponse
} from '../types';

const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000/api/v1'
  : 'https://your-production-api.com/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Posts API
export const postsApi = {
  getPosts: async (page = 1, limit = 20, subredditId?: number, sort = 'hot') => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      sort,
    });
    if (subredditId) params.append('subreddit_id', subredditId.toString());

    const response = await api.get(`/posts/?${params}`);
    return response.data as PostsResponse;
  },

  getPost: async (id: number) => {
    const response = await api.get(`/posts/${id}`);
    return response.data as Post;
  },

  createPost: async (postData: {
    title: string;
    content: string;
    subreddit_id: number;
    post_type?: string;
  }) => {
    const response = await api.post('/posts/', postData);
    return response.data as Post;
  },

  updatePost: async (id: number, postData: {
    title?: string;
    content?: string;
  }) => {
    const response = await api.put(`/posts/${id}`, postData);
    return response.data as Post;
  },

  deletePost: async (id: number) => {
    const response = await api.delete(`/posts/${id}`);
    return response.data;
  },

  upvotePost: async (id: number) => {
    const response = await api.post(`/posts/${id}/upvote`);
    return response.data;
  },

  downvotePost: async (id: number) => {
    const response = await api.post(`/posts/${id}/downvote`);
    return response.data;
  },
};

// Comments API
export const commentsApi = {
  getComments: async (postId: number, page = 1, limit = 50) => {
    const response = await api.get(`/posts/${postId}/comments?page=${page}&limit=${limit}`);
    return response.data as Comment[];
  },

  createComment: async (postId: number, commentData: {
    content: string;
    parent_id?: number;
  }) => {
    const response = await api.post(`/posts/${postId}/comments/`, commentData);
    return response.data as Comment;
  },

  updateComment: async (id: number, content: string) => {
    const response = await api.put(`/comments/${id}`, { content });
    return response.data as Comment;
  },

  deleteComment: async (id: number) => {
    const response = await api.delete(`/comments/${id}`);
    return response.data;
  },

  upvoteComment: async (id: number) => {
    const response = await api.post(`/comments/${id}/upvote`);
    return response.data;
  },

  downvoteComment: async (id: number) => {
    const response = await api.post(`/comments/${id}/downvote`);
    return response.data;
  },
};

// Subreddits API
export const subredditsApi = {
  getSubreddits: async (page = 1, limit = 20, search?: string) => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    if (search) params.append('search', search);

    const response = await api.get(`/subreddits/?${params}`);
    return response.data as SubredditsResponse;
  },

  getSubreddit: async (name: string) => {
    const response = await api.get(`/subreddits/${name}`);
    return response.data as Subreddit;
  },

  createSubreddit: async (subredditData: {
    name: string;
    display_name: string;
    description?: string;
    rules?: string;
    auto_configure?: boolean;
  }) => {
    const response = await api.post('/subreddits/', subredditData);
    return response.data as Subreddit;
  },

  updateSubreddit: async (name: string, subredditData: {
    display_name?: string;
    description?: string;
    rules?: string;
  }) => {
    const response = await api.put(`/subreddits/${name}`, subredditData);
    return response.data as Subreddit;
  },
};

// Search API
export const searchApi = {
  searchPosts: async (query: string, subreddit?: string, sort = 'relevance', page = 1, limit = 20) => {
    const params = new URLSearchParams({
      q: query,
      sort,
      page: page.toString(),
      limit: limit.toString(),
    });
    if (subreddit) params.append('subreddit', subreddit);

    const response = await api.get(`/search/posts?${params}`);
    return response.data as SearchResponse;
  },

  searchSubreddits: async (query: string, page = 1, limit = 20) => {
    const params = new URLSearchParams({
      q: query,
      page: page.toString(),
      limit: limit.toString(),
    });

    const response = await api.get(`/search/subreddits?${params}`);
    return response.data as SearchResponse;
  },

  advancedSearch: async (query: string, filters: {
    subreddit?: string;
    author?: string;
    date_from?: string;
    date_to?: string;
  }, page = 1, limit = 20) => {
    const params = new URLSearchParams({
      q: query,
      page: page.toString(),
      limit: limit.toString(),
    });

    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.append(key, value);
    });

    const response = await api.get(`/search/advanced?${params}`);
    return response.data as SearchResponse;
  },
};

// AI API
export const aiApi = {
  queryCompanion: async (request: AIQueryRequest) => {
    const response = await api.post('/ai/companion/query', request);
    return response.data as AIQueryResponse;
  },

  moderateContent: async (request: ContentModerationRequest) => {
    const response = await api.post('/ai/moderate', request);
    return response.data as ContentModerationResponse;
  },

  autoConfigSubreddit: async (request: AutoConfigRequest) => {
    const response = await api.post('/ai/auto-config', request);
    return response.data as AutoConfigResponse;
  },

  detectContent: async (request: ContentDetectionRequest) => {
    const response = await api.post('/ai/detect-content', request);
    return response.data as ContentDetectionResponse;
  },

  getSubredditFAQ: async (subredditName: string) => {
    const response = await api.get(`/ai/faq/${subredditName}`);
    return response.data;
  },

  getTrendingTopics: async (subredditName: string) => {
    const response = await api.get(`/ai/trending-topics/${subredditName}`);
    return response.data;
  },
};

export default api;
