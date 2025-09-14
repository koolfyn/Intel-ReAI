proc# AI-Native Reddit MVP - Engineering Document

## Project Overview
A mock-off Reddit platform with AI-native features including an AI companion, content moderation, and automated subreddit configuration.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python) - High performance, automatic API documentation
- **Database**: SQLite for simplicity (can upgrade to PostgreSQL later)
- **Authentication**: None (MVP with fake users)
- **AI Integration**: Claude API (Anthropic) for companion and moderation
- **Content Detection**: Claude API for content analysis
- **Search**: SQLite full-text search with FTS5
- **Caching**: In-memory caching for AI responses
- **File Storage**: Local storage for images/attachments

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS + Headless UI components
- **State Management**: Zustand for global state
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors
- **UI Components**: Custom components with Radix UI primitives
- **Real-time**: Socket.io for live updates

### AI Companion
- **LLM**: Claude API (Anthropic) with function calling
- **Vector Database**: Simple in-memory vector storage with sentence-transformers
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (local)
- **Citation System**: Custom implementation with post/comment linking

### DevOps & Testing
- **Testing**: Jest + React Testing Library (frontend), Pytest (backend)
- **API Testing**: Postman/Newman for integration tests
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Basic logging with Python logging module
- **Package management: use uv for python package management

## Project Structure

```
Intel-ReAI/
├── AGENT/
│   ├── ENGINEERING_DOCUMENT.md
│   ├── API_SPECIFICATION.md
│   └── TESTING_STRATEGY.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── subreddit.py
│   │   │   ├── post.py
│   │   │   └── comment.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── posts.py
│   │   │   ├── comments.py
│   │   │   ├── subreddits.py
│   │   │   └── search.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── claude_service.py
│   │   │   ├── ai_companion.py
│   │   │   ├── content_moderation.py
│   │   │   ├── auto_config.py
│   │   │   └── content_detection.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── embeddings.py
│   │   │   └── helpers.py
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── seed_data.py
│   │   │   └── fake_data.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_posts.py
│   │       ├── test_comments.py
│   │       └── test_ai_features.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── SearchBar.tsx
│   │   │   │   └── LoadingSpinner.tsx
│   │   │   ├── layout/
│   │   │   │   ├── Layout.tsx
│   │   │   │   └── Sidebar.tsx
│   │   │   ├── posts/
│   │   │   │   ├── PostCard.tsx
│   │   │   │   ├── PostDetail.tsx
│   │   │   │   └── CreatePost.tsx
│   │   │   ├── subreddits/
│   │   │   │   ├── SubredditCard.tsx
│   │   │   │   ├── SubredditDetail.tsx
│   │   │   │   └── CreateSubreddit.tsx
│   │   │   ├── comments/
│   │   │   │   ├── Comment.tsx
│   │   │   │   └── CommentForm.tsx
│   │   │   └── ai/
│   │   │       ├── AICompanion.tsx
│   │   │       ├── ModerationSuggestions.tsx
│   │   │       └── ContentDetection.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Subreddit.tsx
│   │   │   ├── Post.tsx
│   │   │   └── CreateSubreddit.tsx
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── usePosts.ts
│   │   │   └── useAI.ts
│   │   ├── store/
│   │   │   ├── authStore.ts
│   │   │   ├── postStore.ts
│   │   │   └── aiStore.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── aiService.ts
│   │   ├── types/
│   │   │   ├── auth.ts
│   │   │   ├── post.ts
│   │   │   └── ai.ts
│   │   └── utils/
│   │       ├── constants.ts
│   │       └── helpers.ts
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Feature Matrix

| Feature | Priority | Complexity | Phase | Dependencies |
|---------|----------|------------|-------|--------------|
| **Core Reddit Features** |
| User Authentication | High | Medium | 1 | Database setup |
| Post Creation/Viewing | High | Low | 1 | Auth, Database |
| Comment System | High | Medium | 1 | Posts, Auth |
| Subreddit Pages | High | Medium | 1 | Posts, Auth |
| Search Functionality | High | Medium | 1 | Posts, Database |
| **AI-Native Features** |
| AI Companion Window | High | High | 2 | Posts, Vector DB |
| Content Moderation | High | High | 2 | AI API, Posts |
| Auto Subreddit Config | Medium | High | 3 | AI API, Subreddits |
| Content Detection | Medium | Medium | 3 | External APIs |
| **Advanced Features** |
| Real-time Updates | Low | Medium | 4 | WebSockets |
| Advanced Search | Low | High | 4 | Elasticsearch |
| Mobile Responsive | Medium | Low | 2 | UI Components |

## Implementation Phases

### Phase 1: Core Foundation (Week 1) ✅ COMPLETED
**Goal**: Basic Reddit functionality without AI features

#### Tasks:
1. **Backend Setup** ✅
   - [x] Initialize FastAPI project structure
   - [x] Set up SQLite database with SQLAlchemy (simplified for MVP)
   - [x] Create fake user system (no authentication for MVP)
   - [x] Implement basic CRUD for posts and comments
   - [x] Add subreddit management
   - [x] Set up basic search functionality with SQLite FTS5

2. **Frontend Setup** ✅i
   - [x] Initialize React project with TypeScript
   - [x] Set up Tailwind CSS and component library
   - [x] Create basic routing structure
   - [x] Create type definitions
   - [x] Build home page with post listing
   - [x] Create subreddit and post detail pages
   - [x] Create AI companion components

3. **Testing** 🔄 IN PROGRESS
   - [x] Write unit tests for posts API endpoints
   - [ ] Write component tests for frontend
   - [ ] Set up integration tests

### Phase 2: AI Integration (Week 2) ✅ COMPLETED
**Goal**: Add AI companion and content moderation

#### Tasks:
1. **AI Companion** ✅
   - [x] Set up Claude API integration
   - [x] Implement basic AI companion service
   - [x] Create AI companion API endpoints
   - [x] Implement simplified post search for AI context
   - [x] Create AI companion UI component
   - [x] Build semantic search over posts
   - [x] Add citation system for AI responses

2. **Content Moderation** ✅
   - [x] Integrate Claude API for content analysis
   - [x] Create content moderation service
   - [x] Create moderation API endpoints
   - [x] Create moderation suggestions UI
   - [x] Implement pre-publish content checking
   - [x] Add rule-based filtering

3. **Testing** 🔄 IN PROGRESS
   - [x] Test AI companion functionality
   - [x] Test content moderation accuracy
   - [ ] Performance testing for AI features

### Phase 3: Advanced AI Features (Week 3) ✅ COMPLETED
**Goal**: Auto-configuration and content detection

#### Tasks:
1. **Auto Subreddit Configuration** ✅
   - [x] Build AI-powered subreddit setup service
   - [x] Generate mod rules and descriptions using Claude
   - [x] Create auto-configuration API endpoints
   - [x] Create configuration UI components
   - [x] Create configuration templates

2. **Content Detection** ✅
   - [x] Integrate Claude API for content detection
   - [x] Create content detection service
   - [x] Create content detection API endpoints
   - [x] Create content flagging system UI
   - [x] Build detection dashboard

3. **Testing** 🔄 IN PROGRESS
   - [x] Test auto-configuration accuracy
   - [x] Test content detection reliability
   - [ ] End-to-end testing

### Phase 4: Polish & Optimization (Week 4)
**Goal**: Performance optimization and additional features

#### Tasks:
1. **Performance**
   - [ ] Implement caching strategies
   - [ ] Optimize database queries
   - [ ] Add real-time updates
   - [ ] Mobile responsiveness

2. **Additional Features**
   - [ ] Advanced search with filters
   - [ ] User profiles and preferences
   - [ ] Notification system

3. **Testing & Deployment**xw
   - [ ] Comprehensive testing suite
   - [ ] Load testing
   - [ ] Docker containerization
   - [ ] Deployment setup

## Testing Strategy

### Unit Tests
- **Backend**: Pytest with coverage > 90%
- **Frontend**: Jest + React Testing Library
- **AI Services**: Mock external APIs for consistent testing

### Integration Tests
- **API Endpoints**: Test complete request/response cycles
- **Database**: Test data persistence and retrieval
- **AI Integration**: Test with actual API calls (limited)

### End-to-End Tests
- **User Flows**: Complete user journeys
- **AI Features**: Test AI companion and moderation
- **Cross-browser**: Chrome, Firefox, Safari

## API Specifications

### Authentication
```
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
```

### Posts
```
GET /posts/ - List posts with pagination
POST /posts/ - Create new post
GET /posts/{id} - Get post details
PUT /posts/{id} - Update post
DELETE /posts/{id} - Delete post
```

### Comments
```
GET /posts/{post_id}/comments - Get post comments
POST /posts/{post_id}/comments - Add comment
PUT /comments/{id} - Update comment
DELETE /comments/{id} - Delete comment
```

### Subreddits
```
GET /subreddits/ - List subreddits
POST /subreddits/ - Create subreddit
GET /subreddits/{name} - Get subreddit details
PUT /subreddits/{name} - Update subreddit
```

### Search
```
GET /search/posts?q={query} - Search posts
GET /search/subreddits?q={query} - Search subreddits
```

### AI Features
```
POST /ai/companion/query - Query AI companion
POST /ai/moderate - Check content for moderation
POST /ai/auto-config - Auto-configure subreddit
POST /ai/detect-content - Detect AI-generated content
```

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/reddit_mvp
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
OPENAI_API_KEY=your-openai-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=your-pinecone-env

# Content Detection
GPTZERO_API_KEY=your-gptzero-key
WINSTON_AI_API_KEY=your-winston-key

# File Storage
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=your-bucket-name
```

## Success Metrics

### Technical Metrics
- API response time < 200ms
- Frontend load time < 2s
- Test coverage > 90%
- Zero critical security vulnerabilities

### Feature Metrics
- AI companion response accuracy > 85%
- Content moderation precision > 90%
- Auto-configuration user satisfaction > 80%
- Content detection accuracy > 95%

## Risk Mitigation

### Technical Risks
- **AI API Rate Limits**: Implement caching and request queuing
- **Database Performance**: Use connection pooling and query optimization
- **External API Failures**: Implement fallback mechanisms

### Feature Risks
- **AI Accuracy**: Continuous testing and model fine-tuning
- **Content Detection False Positives**: User feedback loop and threshold tuning
- **Scalability**: Load testing and horizontal scaling preparation

## Next Steps

1. Set up development environment
2. Initialize project structure
3. Implement Phase 1 features
4. Begin testing framework setup
5. Start AI integration planning

---

*This document will be updated as the project evolves and new requirements emerge.*
