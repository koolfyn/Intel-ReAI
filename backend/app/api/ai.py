from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import logging
import time
import hashlib
import json
from datetime import datetime, timedelta
from functools import wraps

from ..database import get_db
from ..models import Post, Subreddit
from ..services.claude_service import ClaudeService
from ..services.ai_companion import AICompanionService
from ..services.content_moderation import ContentModerationService
from ..services.auto_config import AutoConfigService
from ..services.content_detection import ContentDetectionService

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
claude_service = ClaudeService()
ai_companion_service = AICompanionService()
content_moderation_service = ContentModerationService()
auto_config_service = AutoConfigService()
content_detection_service = ContentDetectionService()

# Simple in-memory cache (in production, use Redis)
cache = {}
cache_ttl = 300  # 5 minutes

# Rate limiting storage (in production, use Redis)
rate_limit_storage = {}
rate_limit_window = 60  # 1 minute
rate_limit_max_requests = 10  # 10 requests per minute per IP

def rate_limit(func):
    """Rate limiting decorator"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract Request object from kwargs if present
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break

        if request is None:
            # If no Request object found, skip rate limiting
            return await func(*args, **kwargs)

        client_ip = request.client.host
        current_time = time.time()

        # Clean old entries
        rate_limit_storage[client_ip] = [
            req_time for req_time in rate_limit_storage.get(client_ip, [])
            if current_time - req_time < rate_limit_window
        ]

        # Check rate limit
        if len(rate_limit_storage.get(client_ip, [])) >= rate_limit_max_requests:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        # Add current request
        if client_ip not in rate_limit_storage:
            rate_limit_storage[client_ip] = []
        rate_limit_storage[client_ip].append(current_time)

        return await func(*args, **kwargs)
    return wrapper

def cache_response(ttl: int = 300):
    """Response caching decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"

            # Check cache
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    logger.info(f"Cache hit for {func.__name__}")
                    return cached_data

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            logger.info(f"Cached result for {func.__name__}")
            return result
        return wrapper
    return decorator

# Enhanced Pydantic models with validation
class AIQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="The query to ask the AI companion")
    subreddit_id: Optional[int] = Field(None, ge=1, description="Optional subreddit ID for context")
    context: Optional[str] = Field(None, max_length=2000, description="Additional context for the query")

    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class AIQueryResponse(BaseModel):
    response: str
    citations: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    query_time: float
    cached: bool = False

class ContentModerationRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Content to moderate")
    content_type: str = Field("post", pattern="^(post|comment)$", description="Type of content")
    subreddit_id: Optional[int] = Field(None, ge=1, description="Optional subreddit ID for context")

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

class ContentModerationResponse(BaseModel):
    approved: bool
    suggestions: List[Dict[str, Any]]
    rule_violations: List[Dict[str, Any]]
    moderation_time: float
    confidence: float

class AutoConfigRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=21, pattern="^[a-zA-Z0-9_]+$", description="Subreddit name")
    description: str = Field(..., min_length=10, max_length=500, description="Subreddit description")
    topics: List[str] = Field(..., min_items=1, max_items=10, description="List of topics")
    moderation_style: str = Field("moderate", pattern="^(strict|moderate|lenient)$", description="Moderation style")

    # Enhanced fields for better configuration
    brief_description: Optional[str] = Field(None, max_length=200, description="Brief one-line description")
    target_audience: Optional[str] = Field(None, max_length=200, description="Target audience")
    content_types: Optional[List[str]] = Field(None, max_items=8, description="Allowed content types")
    community_goals: Optional[str] = Field(None, max_length=300, description="Community goals")
    moderation_philosophy: Optional[str] = Field(None, max_length=300, description="Moderation philosophy")
    language: str = Field("en", pattern="^(en|es|fr|de|zh|ja)$", description="Primary language")
    age_restriction: str = Field("all", pattern="^(all|13\\+|18\\+|21\\+)$", description="Age restriction")
    content_rating: str = Field("general", pattern="^(general|mature|adult)$", description="Content rating")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip().lower()

    @validator('description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()

    @validator('topics')
    def validate_topics(cls, v):
        if not v:
            raise ValueError('At least one topic is required')
        # Remove duplicates and empty strings
        topics = list(set([topic.strip() for topic in v if topic.strip()]))
        if not topics:
            raise ValueError('At least one valid topic is required')
        return topics

    @validator('content_types')
    def validate_content_types(cls, v):
        if v is None:
            return v
        valid_types = ['text', 'image', 'link', 'video', 'poll', 'discussion', 'question', 'announcement']
        invalid_types = [t for t in v if t not in valid_types]
        if invalid_types:
            raise ValueError(f'Invalid content types: {invalid_types}. Valid types: {valid_types}')
        return v

class RuleItem(BaseModel):
    title: str
    description: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    category: str = Field(..., pattern="^(behavior|content|spam|safety|community)$")
    enforcement_level: str = Field(..., pattern="^(warning|removal|ban|mute)$")
    examples: Optional[List[str]] = None
    exceptions: Optional[str] = None
    rationale: Optional[str] = None

class ModerationGuidelines(BaseModel):
    general_approach: str
    content_standards: str
    user_behavior_expectations: str
    enforcement_strategy: str
    appeal_process: str

class AutoModerationSettings(BaseModel):
    auto_remove_spam: bool
    require_approval: bool
    content_filters: List[str]
    min_account_age_hours: int = Field(..., ge=0, le=8760)  # Max 1 year
    min_karma_required: int = Field(..., ge=0, le=10000)
    max_posts_per_hour: int = Field(..., ge=1, le=100)
    max_comments_per_hour: int = Field(..., ge=1, le=1000)
    keyword_filters: List[str]
    domain_blacklist: List[str]
    user_blacklist: List[str]
    auto_approve_trusted_users: bool
    remove_duplicate_posts: bool
    require_post_flair: bool
    require_comment_approval: bool
    auto_lock_controversial_posts: bool
    auto_remove_reported_content: bool
    rate_limit_new_users: bool
    require_email_verification: bool

class CommunitySettings(BaseModel):
    allow_images: bool
    allow_videos: bool
    allow_links: bool
    allow_polls: bool
    allow_live_chat: bool
    post_approval_required: bool
    comment_approval_required: bool
    user_flair_enabled: bool
    post_flair_enabled: bool
    wiki_enabled: bool
    events_enabled: bool

class AutoConfigResponse(BaseModel):
    display_name: str
    description: str
    rules: List[RuleItem]
    moderation_guidelines: ModerationGuidelines
    auto_moderation_settings: AutoModerationSettings
    community_settings: CommunitySettings
    suggested_tags: List[str]
    community_type: str = Field(..., pattern="^(discussion|support|hobby|professional|entertainment)$")
    estimated_activity_level: str = Field(..., pattern="^(low|medium|high|very_high)$")
    configuration_notes: Optional[str] = None
    generation_time: float
    cached: bool = False

class ContentDetectionRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000, description="Content to analyze")
    content_type: str = Field("post", pattern="^(post|comment)$", description="Type of content")

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

class ContentDetectionResponse(BaseModel):
    is_ai_generated: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    detection_methods: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    analysis_time: float

# Error handling middleware (to be added to FastAPI app)
async def error_handling_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
        return response
    except HTTPException:
        raise
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"Unhandled error in {request.method} {request.url.path}: {str(e)} - {process_time:.3f}s")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_type": "internal_error",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# API Endpoints
@router.post("/ai/companion/query", response_model=AIQueryResponse)
@rate_limit
@cache_response(ttl=300)
async def query_ai_companion(
    request: AIQueryRequest,
    db: Session = Depends(get_db)
):
    """Query the AI companion for information about posts and subreddits"""
    start_time = time.time()
    try:
        logger.info(f"AI Companion query: {request.query[:100]}...")

        result = await ai_companion_service.query_companion(
            query=request.query,
            subreddit_id=request.subreddit_id,
            context=request.context,
            db=db
        )

        query_time = time.time() - start_time
        return AIQueryResponse(
            response=result["response"],
            citations=result["citations"],
            sources=result["sources"],
            query_time=query_time,
            cached=False
        )
    except Exception as e:
        logger.error(f"Error querying AI companion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error querying AI companion: {str(e)}"
        )

@router.post("/ai/moderate", response_model=ContentModerationResponse)
@rate_limit
async def moderate_content(
    request: ContentModerationRequest,
    db: Session = Depends(get_db)
):
    """Moderate content for clarity, friendliness, and rule violations"""
    start_time = time.time()
    try:
        logger.info(f"Content moderation request: {request.content_type}")

        result = await content_moderation_service.moderate_content(
            content=request.content,
            content_type=request.content_type,
            subreddit_id=request.subreddit_id,
            db=db
        )

        moderation_time = time.time() - start_time
        return ContentModerationResponse(
            approved=result["approved"],
            suggestions=result["suggestions"],
            rule_violations=result["rule_violations"],
            moderation_time=moderation_time,
            confidence=result.get("confidence", 0.8)
        )
    except Exception as e:
        logger.error(f"Error moderating content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error moderating content: {str(e)}"
        )

@router.post("/ai/auto-config", response_model=AutoConfigResponse)
@rate_limit
@cache_response(ttl=600)  # Cache for 10 minutes
async def auto_configure_subreddit(
    request: AutoConfigRequest,
    db: Session = Depends(get_db)
):
    """Auto-configure a new subreddit with comprehensive rules and settings"""
    start_time = time.time()
    try:
        logger.info(f"Auto-config request for subreddit: {request.name}")

        # Check if subreddit name already exists
        existing_subreddit = db.query(Subreddit).filter(Subreddit.name == request.name).first()
        if existing_subreddit:
            raise HTTPException(
                status_code=400,
                detail=f"Subreddit '{request.name}' already exists"
            )

        result = await auto_config_service.generate_subreddit_config(
            name=request.name,
            description=request.description,
            topics=request.topics,
            moderation_style=request.moderation_style,
            brief_description=request.brief_description,
            target_audience=request.target_audience,
            content_types=request.content_types,
            community_goals=request.community_goals,
            moderation_philosophy=request.moderation_philosophy,
            language=request.language,
            age_restriction=request.age_restriction,
            content_rating=request.content_rating
        )

        generation_time = time.time() - start_time
        logger.info(f"Auto-config completed for {request.name} in {generation_time:.3f}s")

        return AutoConfigResponse(
            display_name=result["display_name"],
            description=result["description"],
            rules=result["rules"],
            moderation_guidelines=result["moderation_guidelines"],
            auto_moderation_settings=result["auto_moderation_settings"],
            community_settings=result["community_settings"],
            suggested_tags=result["suggested_tags"],
            community_type=result["community_type"],
            estimated_activity_level=result["estimated_activity_level"],
            configuration_notes=result.get("configuration_notes"),
            generation_time=generation_time,
            cached=False
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error auto-configuring subreddit: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error auto-configuring subreddit: {str(e)}"
        )

@router.post("/ai/detect-content", response_model=ContentDetectionResponse)
@rate_limit
async def detect_ai_content(
    request: ContentDetectionRequest,
    db: Session = Depends(get_db)
):
    """Detect if content is AI-generated"""
    start_time = time.time()
    try:
        logger.info(f"Content detection request: {request.content_type}")

        result = await content_detection_service.detect_content(
            content=request.content,
            content_type=request.content_type
        )

        analysis_time = time.time() - start_time
        return ContentDetectionResponse(
            is_ai_generated=result["is_ai_generated"],
            confidence=result["confidence"],
            detection_methods=result["detection_methods"],
            recommendations=result["recommendations"],
            analysis_time=analysis_time
        )
    except Exception as e:
        logger.error(f"Error detecting content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting content: {str(e)}"
        )

@router.get("/ai/faq/{subreddit_name}")
@rate_limit
@cache_response(ttl=1800)  # Cache for 30 minutes
async def get_subreddit_faq(
    subreddit_name: str,
    db: Session = Depends(get_db)
):
    """Get frequently asked questions for a subreddit"""
    try:
        logger.info(f"FAQ request for subreddit: {subreddit_name}")

        subreddit = db.query(Subreddit).filter(Subreddit.name == subreddit_name).first()
        if not subreddit:
            raise HTTPException(status_code=404, detail="Subreddit not found")

        # Get recent posts to generate FAQ
        recent_posts = db.query(Post).filter(
            Post.subreddit_id == subreddit.id
        ).order_by(Post.created_at.desc()).limit(20).all()

        if not recent_posts:
            return {
                "subreddit": subreddit_name,
                "faqs": [],
                "message": "No posts found to generate FAQs",
                "cached": False
            }

        # Generate FAQ using AI
        faq_result = await ai_companion_service.generate_faq(
            subreddit=subreddit,
            posts=recent_posts
        )

        return {
            "subreddit": subreddit_name,
            "faqs": faq_result,
            "cached": False
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating FAQ: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating FAQ: {str(e)}"
        )

@router.get("/ai/trending-topics/{subreddit_name}")
@rate_limit
@cache_response(ttl=900)  # Cache for 15 minutes
async def get_trending_topics(
    subreddit_name: str,
    db: Session = Depends(get_db)
):
    """Get trending topics in a subreddit"""
    try:
        logger.info(f"Trending topics request for subreddit: {subreddit_name}")

        subreddit = db.query(Subreddit).filter(Subreddit.name == subreddit_name).first()
        if not subreddit:
            raise HTTPException(status_code=404, detail="Subreddit not found")

        # Get recent posts
        recent_posts = db.query(Post).filter(
            Post.subreddit_id == subreddit.id
        ).order_by(Post.created_at.desc()).limit(50).all()

        if not recent_posts:
            return {
                "subreddit": subreddit_name,
                "trending_topics": [],
                "message": "No posts found to analyze trends",
                "cached": False
            }

        # Analyze trending topics using AI
        topics_result = await ai_companion_service.analyze_trending_topics(
            subreddit=subreddit,
            posts=recent_posts
        )

        return {
            "subreddit": subreddit_name,
            "trending_topics": topics_result,
            "cached": False
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing trending topics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing trending topics: {str(e)}"
        )

# Health check endpoint
@router.get("/ai/health")
async def health_check():
    """Health check for AI services"""
    try:
        # Test Claude service
        claude_status = "healthy" if claude_service else "unhealthy"

        return {
            "status": "healthy",
            "services": {
                "claude": claude_status,
                "auto_config": "healthy",
                "content_moderation": "healthy",
                "content_detection": "healthy"
            },
            "cache_size": len(cache),
            "rate_limit_active_ips": len(rate_limit_storage),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Cache management endpoints
@router.delete("/ai/cache")
async def clear_cache():
    """Clear the response cache"""
    global cache
    cache.clear()
    logger.info("Cache cleared")
    return {"message": "Cache cleared successfully"}

@router.get("/ai/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return {
        "cache_size": len(cache),
        "cache_ttl": cache_ttl,
        "rate_limit_active_ips": len(rate_limit_storage),
        "rate_limit_window": rate_limit_window,
        "rate_limit_max_requests": rate_limit_max_requests
    }
