# AI-Native Reddit MVP - Deployment Guide

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Claude API key

### 1. Install uv (Python Package Manager)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart your terminal or run: source ~/.bashrc
```

### 2. Setup Environment
```bash
# Run the setup script
./setup.sh

# Add your Claude API key
echo "CLAUDE_API_KEY=your_actual_api_key_here" > backend/.env
```

### 3. Install Dependencies
```bash
# Backend (using uv - much faster!)
cd backend
uv sync

# Frontend
cd ../frontend
npm install
```

### 4. Initialize Database
```bash
cd ../backend
uv run python seed_db.py
```

### 5. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
uv run python run_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 6. Access the Application
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

## Features Available

### ✅ Core Reddit Features
- Browse posts and comments
- Create posts and comments
- Vote on posts and comments
- Search posts and subreddits
- View subreddit pages

### ✅ AI Features
- **AI Companion**: Chat with AI about posts and topics
- **Content Moderation**: Get suggestions for better posts
- **Content Detection**: Detect AI-generated content
- **Auto Configuration**: AI-generated subreddit rules and settings
- **FAQ Generation**: AI-generated FAQs for subreddits
- **Trending Topics**: AI-analyzed trending topics

### ✅ UI Features
- Modern, responsive design
- Real-time voting
- AI companion sidebar
- Content moderation suggestions
- Auto-configuration forms

## Testing the AI Features

### 1. AI Companion
- Go to any subreddit page
- Use the AI Companion sidebar to ask questions
- Try: "What are the most popular topics here?"

### 2. Content Moderation
- Create a new post
- Click "Moderate Content" to get AI suggestions
- Try posting something with poor grammar or rude language

### 3. Content Detection
- Create a post with AI-generated content
- Click "Detect AI" to see if it's flagged
- Try posting something obviously written by ChatGPT

### 4. Auto Configuration
- Go to "Create Subreddit"
- Fill in name and description
- Click "Auto-Configure" to see AI-generated rules

## Troubleshooting

### Backend Issues
```bash
# Check if backend is running
curl http://localhost:8000/health

# View logs
cd backend
uv run python run_server.py
```

### Frontend Issues
```bash
# Check if frontend is running
curl http://localhost:3000

# Restart frontend
cd frontend
npm start
```

### Database Issues
```bash
# Reset database
cd backend
rm reddit_mvp.db
uv run python seed_db.py
```

## Development

### Running Tests
```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
npm test
```

### Adding New Features
1. Backend: Add endpoints in `backend/app/api/`
2. Frontend: Add components in `frontend/src/components/`
3. AI: Add services in `backend/app/services/`

## Production Deployment

### Backend (FastAPI)
- Use `uvicorn` with production settings
- Set up reverse proxy (nginx)
- Use PostgreSQL instead of SQLite
- Set up proper logging

### Frontend (React)
- Build for production: `npm run build`
- Serve with nginx or CDN
- Set up proper caching

## API Endpoints

### Posts
- `GET /api/v1/posts/` - List posts
- `POST /api/v1/posts/` - Create post
- `GET /api/v1/posts/{id}` - Get post
- `PUT /api/v1/posts/{id}` - Update post
- `DELETE /api/v1/posts/{id}` - Delete post

### AI Features
- `POST /api/v1/ai/companion/query` - Query AI companion
- `POST /api/v1/ai/moderate` - Moderate content
- `POST /api/v1/ai/auto-config` - Auto-configure subreddit
- `POST /api/v1/ai/detect-content` - Detect AI content

See full API documentation at http://localhost:8000/docs
