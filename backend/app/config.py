import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    DATABASE_URL: str = "sqlite:///./reddit_mvp.db"

    # Claude API
    CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")
    CLAUDE_MODEL: str = "claude-3-sonnet-20240229"

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
