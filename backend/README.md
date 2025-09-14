# AI-Native Reddit MVP - Backend

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
uv sync
```

### 2. Set Environment Variables
Create a `.env` file in the backend directory:
```env
CLAUDE_API_KEY=your_claude_api_key_here
DEBUG=True
```

### 3. Initialize and Seed Database
```bash
uv run python seed_db.py
```

### 4. Run the Server
```bash
uv run python run_server.py
```

The API will be available at `http://localhost:8000`

### 5. View API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Posts
- `GET /api/v1/posts/` - List posts with pagination
- `POST /api/v1/posts/` - Create new post
- `GET /api/v1/posts/{id}` - Get post details
- `PUT /api/v1/posts/{id}` - Update post
- `DELETE /api/v1/posts/{id}` - Delete post

### Comments
- `GET /api/v1/posts/{post_id}/comments` - Get post comments
- `POST /api/v1/posts/{post_id}/comments` - Create comment
- `PUT /api/v1/comments/{id}` - Update comment
- `DELETE /api/v1/comments/{id}` - Delete comment

### Subreddits
- `GET /api/v1/subreddits/` - List subreddits
- `POST /api/v1/subreddits/` - Create subreddit
- `GET /api/v1/subreddits/{name}` - Get subreddit details
- `PUT /api/v1/subreddits/{name}` - Update subreddit

### Search
- `GET /api/v1/search/posts` - Search posts
- `GET /api/v1/search/subreddits` - Search subreddits
- `GET /api/v1/search/advanced` - Advanced search

### AI Features
- `POST /api/v1/ai/companion/query` - Query AI companion
- `POST /api/v1/ai/moderate` - Moderate content
- `POST /api/v1/ai/auto-config` - Auto-configure subreddit
- `POST /api/v1/ai/detect-content` - Detect AI-generated content
- `GET /api/v1/ai/faq/{subreddit_name}` - Get subreddit FAQ
- `GET /api/v1/ai/trending-topics/{subreddit_name}` - Get trending topics

## Testing

Run tests with:
```bash
uv run pytest
```

## Database

The application uses SQLite for simplicity. The database file will be created at `./reddit_mvp.db` when you first run the application.

For production, you can easily switch to PostgreSQL by updating the `DATABASE_URL` in the configuration.
