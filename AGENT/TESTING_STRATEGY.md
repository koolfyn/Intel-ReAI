# Testing Strategy - AI-Native Reddit MVP

## Overview
This document outlines the comprehensive testing strategy for the AI-native Reddit MVP, ensuring reliability, performance, and quality across all features.

## Testing Pyramid

### Unit Tests (70%)
- **Backend**: Individual functions, methods, and classes
- **Frontend**: Individual components and utility functions
- **AI Services**: Mocked external API calls

### Integration Tests (20%)
- **API Endpoints**: Complete request/response cycles
- **Database Operations**: Data persistence and retrieval
- **Component Integration**: Frontend component interactions

### End-to-End Tests (10%)
- **User Flows**: Complete user journeys
- **Cross-browser**: Chrome, Firefox, Safari
- **AI Features**: End-to-end AI functionality

## Backend Testing (Python/Pytest)

### Test Structure
```
backend/tests/
├── unit/
│   ├── test_auth.py
│   ├── test_posts.py
│   ├── test_comments.py
│   ├── test_subreddits.py
│   ├── test_search.py
│   └── test_ai_services.py
├── integration/
│   ├── test_api_auth.py
│   ├── test_api_posts.py
│   ├── test_api_comments.py
│   └── test_api_ai.py
├── fixtures/
│   ├── conftest.py
│   ├── test_data.py
│   └── mock_ai_responses.py
└── e2e/
    ├── test_user_flows.py
    └── test_ai_workflows.py
```

### Unit Test Examples

#### Authentication Tests
```python
# test_auth.py
import pytest
from app.services.auth import AuthService
from app.models.user import User

class TestAuthService:
    def test_create_user_success(self, db_session):
        auth_service = AuthService(db_session)
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123"
        }

        user = auth_service.create_user(user_data)

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("securepassword123")

    def test_create_user_duplicate_username(self, db_session):
        auth_service = AuthService(db_session)
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123"
        }

        # Create first user
        auth_service.create_user(user_data)

        # Try to create duplicate
        with pytest.raises(ValueError, match="Username already exists"):
            auth_service.create_user(user_data)

    def test_authenticate_user_valid_credentials(self, db_session, test_user):
        auth_service = AuthService(db_session)

        user = auth_service.authenticate_user("testuser", "password123")

        assert user is not None
        assert user.username == "testuser"

    def test_authenticate_user_invalid_credentials(self, db_session):
        auth_service = AuthService(db_session)

        user = auth_service.authenticate_user("testuser", "wrongpassword")

        assert user is None
```

#### Post Management Tests
```python
# test_posts.py
import pytest
from app.services.posts import PostService
from app.models.post import Post

class TestPostService:
    def test_create_post_success(self, db_session, test_user, test_subreddit):
        post_service = PostService(db_session)
        post_data = {
            "title": "Test Post",
            "content": "This is a test post",
            "subreddit_id": test_subreddit.id,
            "author_id": test_user.id
        }

        post = post_service.create_post(post_data)

        assert post.title == "Test Post"
        assert post.content == "This is a test post"
        assert post.author_id == test_user.id
        assert post.subreddit_id == test_subreddit.id

    def test_get_posts_with_pagination(self, db_session, test_posts):
        post_service = PostService(db_session)

        posts, pagination = post_service.get_posts(page=1, limit=10)

        assert len(posts) <= 10
        assert pagination["page"] == 1
        assert pagination["limit"] == 10
        assert pagination["total"] >= 0

    def test_search_posts_by_keyword(self, db_session, test_posts):
        post_service = PostService(db_session)

        posts = post_service.search_posts("test keyword")

        assert all("test keyword" in post.title.lower() or
                  "test keyword" in post.content.lower()
                  for post in posts)
```

#### AI Service Tests
```python
# test_ai_services.py
import pytest
from unittest.mock import Mock, patch
from app.services.ai_companion import AICompanionService

class TestAICompanionService:
    @patch('app.services.ai_companion.openai.ChatCompletion.create')
    def test_query_ai_companion_success(self, mock_openai, db_session, test_posts):
        # Mock OpenAI response
        mock_openai.return_value = Mock(
            choices=[Mock(message=Mock(content="AI response"))]
        )

        ai_service = AICompanionService(db_session)
        result = ai_service.query_companion("What are the top posts?", "subreddit_id")

        assert result["response"] == "AI response"
        assert "citations" in result
        assert "sources" in result

    @patch('app.services.ai_companion.openai.ChatCompletion.create')
    def test_query_ai_companion_with_citations(self, mock_openai, db_session, test_posts):
        mock_openai.return_value = Mock(
            choices=[Mock(message=Mock(content="Based on [1] and [2], here's the answer"))]
        )

        ai_service = AICompanionService(db_session)
        result = ai_service.query_companion("What are the top posts?", "subreddit_id")

        assert len(result["citations"]) > 0
        assert all("post_id" in citation for citation in result["citations"])
```

### Integration Test Examples

#### API Endpoint Tests
```python
# test_api_posts.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestPostAPI:
    def test_create_post_authenticated(self, auth_headers, test_subreddit):
        post_data = {
            "title": "Test Post",
            "content": "This is a test post",
            "subreddit_id": str(test_subreddit.id),
            "post_type": "text"
        }

        response = client.post(
            "/api/v1/posts/",
            json=post_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Post"
        assert data["content"] == "This is a test post"

    def test_create_post_unauthenticated(self, test_subreddit):
        post_data = {
            "title": "Test Post",
            "content": "This is a test post",
            "subreddit_id": str(test_subreddit.id),
            "post_type": "text"
        }

        response = client.post("/api/v1/posts/", json=post_data)

        assert response.status_code == 401

    def test_get_posts_with_pagination(self):
        response = client.get("/api/v1/posts/?page=1&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "pagination" in data
        assert len(data["posts"]) <= 10
```

## Frontend Testing (React/Jest)

### Test Structure
```
frontend/src/
├── __tests__/
│   ├── components/
│   │   ├── PostCard.test.tsx
│   │   ├── Comment.test.tsx
│   │   ├── AICompanion.test.tsx
│   │   └── SearchBar.test.tsx
│   ├── pages/
│   │   ├── Home.test.tsx
│   │   ├── Subreddit.test.tsx
│   │   └── Post.test.tsx
│   ├── hooks/
│   │   ├── useAuth.test.ts
│   │   ├── usePosts.test.ts
│   │   └── useAI.test.ts
│   └── utils/
│       ├── helpers.test.ts
│       └── api.test.ts
├── __mocks__/
│   ├── api.ts
│   └── aiService.ts
└── test-utils/
    ├── render.tsx
    └── fixtures.ts
```

### Component Test Examples

#### PostCard Component Test
```typescript
// PostCard.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { PostCard } from '../components/posts/PostCard';
import { mockPost } from '../test-utils/fixtures';

describe('PostCard', () => {
  it('renders post title and content', () => {
    render(<PostCard post={mockPost} />);

    expect(screen.getByText(mockPost.title)).toBeInTheDocument();
    expect(screen.getByText(mockPost.content)).toBeInTheDocument();
  });

  it('displays upvote and downvote buttons', () => {
    render(<PostCard post={mockPost} />);

    expect(screen.getByLabelText('Upvote')).toBeInTheDocument();
    expect(screen.getByLabelText('Downvote')).toBeInTheDocument();
  });

  it('shows comment count', () => {
    render(<PostCard post={mockPost} />);

    expect(screen.getByText(`${mockPost.comment_count} comments`)).toBeInTheDocument();
  });

  it('handles upvote click', () => {
    const onUpvote = jest.fn();
    render(<PostCard post={mockPost} onUpvote={onUpvote} />);

    fireEvent.click(screen.getByLabelText('Upvote'));

    expect(onUpvote).toHaveBeenCalledWith(mockPost.id);
  });
});
```

#### AI Companion Test
```typescript
// AICompanion.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AICompanion } from '../components/ai/AICompanion';
import { mockAIResponse } from '../test-utils/fixtures';

// Mock the AI service
jest.mock('../services/aiService', () => ({
  queryCompanion: jest.fn()
}));

describe('AICompanion', () => {
  it('renders query input and submit button', () => {
    render(<AICompanion subredditId="test-subreddit" />);

    expect(screen.getByPlaceholderText('Ask the AI companion...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Ask' })).toBeInTheDocument();
  });

  it('submits query and displays response', async () => {
    const mockQueryCompanion = require('../services/aiService').queryCompanion;
    mockQueryCompanion.mockResolvedValue(mockAIResponse);

    render(<AICompanion subredditId="test-subreddit" />);

    const input = screen.getByPlaceholderText('Ask the AI companion...');
    const button = screen.getByRole('button', { name: 'Ask' });

    fireEvent.change(input, { target: { value: 'What are the top posts?' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(mockAIResponse.response)).toBeInTheDocument();
    });

    expect(mockQueryCompanion).toHaveBeenCalledWith('What are the top posts?', 'test-subreddit');
  });

  it('displays citations when available', async () => {
    const mockQueryCompanion = require('../services/aiService').queryCompanion;
    mockQueryCompanion.mockResolvedValue(mockAIResponse);

    render(<AICompanion subredditId="test-subreddit" />);

    const input = screen.getByPlaceholderText('Ask the AI companion...');
    const button = screen.getByRole('button', { name: 'Ask' });

    fireEvent.change(input, { target: { value: 'What are the top posts?' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Sources:')).toBeInTheDocument();
      expect(screen.getByText(mockAIResponse.citations[0].post_title)).toBeInTheDocument();
    });
  });
});
```

### Hook Test Examples

#### useAuth Hook Test
```typescript
// useAuth.test.ts
import { renderHook, act } from '@testing-library/react';
import { useAuth } from '../hooks/useAuth';
import { mockUser } from '../test-utils/fixtures';

// Mock the API service
jest.mock('../services/api', () => ({
  auth: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn()
  }
}));

describe('useAuth', () => {
  it('initializes with no user', () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('handles successful login', async () => {
    const mockLogin = require('../services/api').auth.login;
    mockLogin.mockResolvedValue({ user: mockUser, token: 'test-token' });

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login('testuser', 'password');
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('handles login failure', async () => {
    const mockLogin = require('../services/api').auth.login;
    mockLogin.mockRejectedValue(new Error('Invalid credentials'));

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.login('testuser', 'wrongpassword');
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });
});
```

## End-to-End Testing (Playwright)

### Test Structure
```
e2e/
├── tests/
│   ├── auth.spec.ts
│   ├── posts.spec.ts
│   ├── comments.spec.ts
│   ├── subreddits.spec.ts
│   ├── search.spec.ts
│   └── ai-features.spec.ts
├── fixtures/
│   ├── test-data.ts
│   └── page-objects.ts
└── playwright.config.ts
```

### E2E Test Examples

#### User Authentication Flow
```typescript
// auth.spec.ts
import { test, expect } from '@playwright/test';
import { HomePage } from '../fixtures/page-objects';

test.describe('Authentication', () => {
  test('user can register and login', async ({ page }) => {
    const homePage = new HomePage(page);

    // Navigate to home page
    await homePage.goto();

    // Click register button
    await homePage.clickRegister();

    // Fill registration form
    await homePage.fillRegistrationForm({
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123'
    });

    // Submit registration
    await homePage.submitRegistration();

    // Verify successful registration
    await expect(page.getByText('Registration successful')).toBeVisible();

    // Login with new credentials
    await homePage.clickLogin();
    await homePage.fillLoginForm('testuser', 'password123');
    await homePage.submitLogin();

    // Verify login success
    await expect(page.getByText('Welcome, testuser')).toBeVisible();
  });

  test('user can logout', async ({ page }) => {
    const homePage = new HomePage(page);

    // Login first
    await homePage.goto();
    await homePage.login('testuser', 'password123');

    // Logout
    await homePage.logout();

    // Verify logout
    await expect(page.getByText('Login')).toBeVisible();
  });
});
```

#### AI Companion Flow
```typescript
// ai-features.spec.ts
import { test, expect } from '@playwright/test';
import { SubredditPage } from '../fixtures/page-objects';

test.describe('AI Features', () => {
  test('AI companion can answer questions about subreddit', async ({ page }) => {
    const subredditPage = new SubredditPage(page);

    // Navigate to a subreddit with posts
    await subredditPage.goto('programming');

    // Open AI companion
    await subredditPage.openAICompanion();

    // Ask a question
    await subredditPage.askAICompanion('What are the most popular programming languages discussed here?');

    // Wait for response
    await expect(subredditPage.getAIResponse()).toBeVisible();

    // Verify response contains citations
    await expect(subredditPage.getAICitations()).toBeVisible();

    // Click on a citation
    await subredditPage.clickCitation(0);

    // Verify navigation to source post
    await expect(page.url()).toContain('/posts/');
  });

  test('content moderation suggests improvements', async ({ page }) => {
    const subredditPage = new SubredditPage(page);

    // Login and navigate to subreddit
    await subredditPage.goto('programming');
    await subredditPage.login('testuser', 'password123');

    // Start creating a post
    await subredditPage.clickCreatePost();

    // Enter content that might need moderation
    await subredditPage.fillPostContent('This is a really bad post with poor grammar and rude language!');

    // Check for moderation suggestions
    await expect(subredditPage.getModerationSuggestions()).toBeVisible();

    // Verify suggestions are helpful
    const suggestions = await subredditPage.getModerationSuggestions();
    expect(suggestions).toContain('Consider improving clarity');
    expect(suggestions).toContain('Use more friendly language');
  });
});
```

## Test Data Management

### Fixtures and Factories
```python
# backend/tests/fixtures/test_data.py
import factory
from app.models.user import User
from app.models.subreddit import Subreddit
from app.models.post import Post

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password_hash = factory.LazyFunction(lambda: hash_password("password123"))

class SubredditFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Subreddit
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"subreddit{n}")
    display_name = factory.LazyAttribute(lambda obj: obj.name.title())
    description = factory.Faker('text', max_nb_chars=200)

class PostFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Post
        sqlalchemy_session_persistence = "commit"

    title = factory.Faker('sentence', nb_words=6)
    content = factory.Faker('text', max_nb_chars=1000)
    author = factory.SubFactory(UserFactory)
    subreddit = factory.SubFactory(SubredditFactory)
```

## Performance Testing

### Load Testing with Locust
```python
# performance/locustfile.py
from locust import HttpUser, task, between

class RedditUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login user
        response = self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "password123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def view_posts(self):
        self.client.get("/api/v1/posts/", headers=self.headers)

    @task(2)
    def view_post_detail(self):
        self.client.get("/api/v1/posts/1", headers=self.headers)

    @task(1)
    def create_post(self):
        self.client.post("/api/v1/posts/", json={
            "title": "Load test post",
            "content": "This is a load test post",
            "subreddit_id": "1",
            "post_type": "text"
        }, headers=self.headers)

    @task(1)
    def query_ai_companion(self):
        self.client.post("/api/v1/ai/companion/query", json={
            "query": "What are the top posts?",
            "subreddit_id": "1"
        }, headers=self.headers)
```

## Test Configuration

### Pytest Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=90
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    ai: AI-related tests
```

### Jest Configuration
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/test-utils/setup.ts'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/test-utils/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: frontend/coverage/lcov.info

  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci
          npx playwright install

      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
```

## Test Metrics and Reporting

### Coverage Targets
- **Backend**: 90%+ line coverage
- **Frontend**: 80%+ line coverage
- **AI Services**: 85%+ line coverage (with mocked external APIs)

### Performance Targets
- **API Response Time**: < 200ms (95th percentile)
- **Frontend Load Time**: < 2s
- **AI Response Time**: < 5s
- **Database Query Time**: < 100ms

### Quality Gates
- All tests must pass
- Coverage targets must be met
- No critical security vulnerabilities
- Performance targets must be met
- Code review approval required

## Test Maintenance

### Regular Tasks
- Update test data fixtures monthly
- Review and update mock responses quarterly
- Performance test with realistic data volumes
- Update E2E tests when UI changes
- Monitor test execution time and optimize

### Test Data Cleanup
- Automated cleanup of test data after each test run
- Separate test database for isolation
- Regular cleanup of uploaded test files
- Mock external API calls to avoid rate limits

This comprehensive testing strategy ensures the AI-native Reddit MVP is reliable, performant, and maintainable while providing confidence in the AI features and overall system quality.
