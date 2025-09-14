#!/bin/bash

echo "🚀 Setting up AI-Native Reddit MVP..."

# Create .env file for backend
echo "📝 Creating environment file..."
cat > backend/.env << EOF
# Claude API Configuration
CLAUDE_API_KEY=your_claude_api_key_here

# App Configuration
DEBUG=True

# Database Configuration (SQLite - no additional config needed)
# DATABASE_URL=sqlite:///./reddit_mvp.db
EOF

echo "✅ Environment file created!"
echo ""
echo "🔧 Next steps:"
echo "1. Add your Claude API key to backend/.env"
echo "2. Install uv (if not already installed): curl -LsSf https://astral.sh/uv/install.sh | sh"
echo "3. Install backend dependencies: cd backend && uv sync"
echo "4. Install frontend dependencies: cd frontend && npm install"
echo "5. Seed the database: cd backend && uv run python seed_db.py"
echo "6. Start the backend: cd backend && uv run python run_server.py"
echo "7. Start the frontend: cd frontend && npm start"
echo ""
echo "🌐 The app will be available at http://localhost:3000"
echo "📚 API documentation at http://localhost:8000/docs"
