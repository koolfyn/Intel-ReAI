from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from .api import posts, comments, subreddits, search, ai

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Native Reddit MVP with Claude integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(posts.router, prefix="/api/v1", tags=["posts"])
app.include_router(comments.router, prefix="/api/v1", tags=["comments"])
app.include_router(subreddits.router, prefix="/api/v1", tags=["subreddits"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(ai.router, prefix="/api/v1", tags=["ai"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("Database initialized")

@app.get("/")
async def root():
    return {"message": "AI-Native Reddit MVP API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
