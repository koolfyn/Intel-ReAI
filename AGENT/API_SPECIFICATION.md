# API Specification - AI-Native Reddit MVP

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "created_at": "datetime"
  }
}
```

### Login User
```http
POST /auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

### Refresh Token
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

## Posts

### List Posts
```http
GET /posts/?page=1&limit=20&subreddit=string&sort=hot|new|top
```

**Response:**
```json
{
  "posts": [
    {
      "id": "uuid",
      "title": "string",
      "content": "string",
      "author": {
        "id": "uuid",
        "username": "string"
      },
      "subreddit": {
        "id": "uuid",
        "name": "string",
        "display_name": "string"
      },
      "upvotes": 0,
      "downvotes": 0,
      "comment_count": 0,
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

### Create Post
```http
POST /posts/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "string",
  "content": "string",
  "subreddit_id": "uuid",
  "post_type": "text|link|image"
}
```

### Get Post Details
```http
GET /posts/{post_id}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "string",
  "content": "string",
  "author": {
    "id": "uuid",
    "username": "string"
  },
  "subreddit": {
    "id": "uuid",
    "name": "string",
    "display_name": "string",
    "description": "string"
  },
  "upvotes": 0,
  "downvotes": 0,
  "comment_count": 0,
  "created_at": "datetime",
  "updated_at": "datetime",
  "comments": [
    {
      "id": "uuid",
      "content": "string",
      "author": {
        "id": "uuid",
        "username": "string"
      },
      "upvotes": 0,
      "downvotes": 0,
      "created_at": "datetime",
      "replies": []
    }
  ]
}
```

### Update Post
```http
PUT /posts/{post_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "string",
  "content": "string"
}
```

### Delete Post
```http
DELETE /posts/{post_id}
Authorization: Bearer <token>
```

## Comments

### Get Post Comments
```http
GET /posts/{post_id}/comments/?page=1&limit=50
```

### Create Comment
```http
POST /posts/{post_id}/comments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "string",
  "parent_id": "uuid" // Optional, for replies
}
```

### Update Comment
```http
PUT /comments/{comment_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "string"
}
```

### Delete Comment
```http
DELETE /comments/{comment_id}
Authorization: Bearer <token>
```

## Subreddits

### List Subreddits
```http
GET /subreddits/?page=1&limit=20&search=string
```

### Create Subreddit
```http
POST /subreddits/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "string",
  "display_name": "string",
  "description": "string",
  "rules": ["string"],
  "auto_configure": true
}
```

### Get Subreddit Details
```http
GET /subreddits/{subreddit_name}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "string",
  "display_name": "string",
  "description": "string",
  "rules": ["string"],
  "moderators": [
    {
      "id": "uuid",
      "username": "string"
    }
  ],
  "subscriber_count": 0,
  "post_count": 0,
  "created_at": "datetime"
}
```

### Update Subreddit
```http
PUT /subreddits/{subreddit_name}
Authorization: Bearer <token>
Content-Type: application/json

{
  "display_name": "string",
  "description": "string",
  "rules": ["string"]
}
```

## Search

### Search Posts
```http
GET /search/posts/?q={query}&subreddit={name}&sort=relevance|date|score
```

### Search Subreddits
```http
GET /search/subreddits/?q={query}
```

### Advanced Search
```http
GET /search/advanced/?q={query}&subreddit={name}&author={username}&date_from={date}&date_to={date}
```

## AI Features

### AI Companion Query
```http
POST /ai/companion/query
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "string",
  "subreddit_id": "uuid", // Optional, for subreddit-specific queries
  "context": "string" // Optional, for additional context
}
```

**Response:**
```json
{
  "response": "string",
  "citations": [
    {
      "post_id": "uuid",
      "post_title": "string",
      "comment_id": "uuid", // Optional
      "relevance_score": 0.95,
      "excerpt": "string"
    }
  ],
  "sources": [
    {
      "type": "post|comment",
      "id": "uuid",
      "title": "string",
      "url": "string"
    }
  ]
}
```

### Content Moderation
```http
POST /ai/moderate
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "string",
  "content_type": "post|comment",
  "subreddit_id": "uuid"
}
```

**Response:**
```json
{
  "approved": false,
  "suggestions": [
    {
      "type": "clarity|friendliness|rule_violation",
      "message": "string",
      "suggestion": "string",
      "severity": "low|medium|high"
    }
  ],
  "rule_violations": [
    {
      "rule": "string",
      "description": "string",
      "severity": "low|medium|high"
    }
  ]
}
```

### Auto-Configure Subreddit
```http
POST /ai/auto-config
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "string",
  "description": "string",
  "topics": ["string"],
  "moderation_style": "strict|moderate|lenient"
}
```

**Response:**
```json
{
  "display_name": "string",
  "description": "string",
  "rules": [
    {
      "title": "string",
      "description": "string",
      "severity": "low|medium|high"
    }
  ],
  "moderation_guidelines": "string",
  "auto_moderation_settings": {
    "auto_remove_spam": true,
    "require_approval": false,
    "content_filters": ["string"]
  }
}
```

### Content Detection
```http
POST /ai/detect-content
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "string",
  "content_type": "post|comment"
}
```

**Response:**
```json
{
  "is_ai_generated": true,
  "confidence": 0.85,
  "detection_methods": [
    {
      "provider": "gptzero|winston",
      "confidence": 0.82,
      "details": "string"
    }
  ],
  "recommendations": [
    {
      "action": "flag|review|approve",
      "reason": "string"
    }
  ]
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR|AUTHENTICATION_ERROR|NOT_FOUND|INTERNAL_ERROR",
    "message": "string",
    "details": {} // Optional additional error details
  }
}
```

### Common Error Codes

- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `409` - Conflict (duplicate resource)
- `422` - Unprocessable Entity (validation failed)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## Rate Limiting

- **General API**: 1000 requests per hour per user
- **AI Endpoints**: 100 requests per hour per user
- **Search**: 500 requests per hour per user
- **Content Detection**: 50 requests per hour per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## WebSocket Events

### Real-time Updates
```
ws://localhost:8000/ws?token=<jwt_token>
```

**Events:**
- `new_post` - New post created
- `new_comment` - New comment added
- `post_updated` - Post content updated
- `comment_updated` - Comment content updated
- `ai_response` - AI companion response ready

**Example Event:**
```json
{
  "event": "new_post",
  "data": {
    "post_id": "uuid",
    "title": "string",
    "subreddit": "string",
    "author": "string"
  }
}
```
