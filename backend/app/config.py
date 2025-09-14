import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    DATABASE_URL: str = "sqlite:///./reddit_mvp.db"

    # Claude API
    CLAUDE_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = "claude-3-5-haiku-20241022"

    # Winston AI API
    WINSTON_AI_API_KEY: str = os.getenv("WINSTON_AI_API_KEY", "")
    WINSTON_AI_BASE_URL: str = "https://api.gowinston.ai/mcp/v1"
    WINSTON_AI_ENABLED: bool = os.getenv("WINSTON_AI_ENABLED", "true").lower() == "true"

    # App settings
    APP_NAME: str = "AI-Native Reddit MVP"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # CORS settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

settings = Settings()
