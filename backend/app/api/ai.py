from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Post, Subreddit
from ..services.claude_service import ClaudeService
from ..services.ai_companion import AICompanionService
from ..services.content_moderation import ContentModerationService
from ..services.auto_config import AutoConfigService
from ..services.content_detection import ContentDetectionService
from pydantic import BaseModel

router = APIRouter()

# Initialize services
claude_service = ClaudeService()
ai_companion_service = AICompanionService()
content_moderation_service = ContentModerationService()
auto_config_service = AutoConfigService()
content_detection_service = ContentDetectionService()

class AIQueryRequest(BaseModel):
    query: str
    subreddit_id: Optional[int] = None
    context: Optional[str] = None

class AIQueryResponse(BaseModel):
    response: str
    citations: List[dict]
    sources: List[dict]

class ContentModerationRequest(BaseModel):
    content: str
    content_type: str = "post"  # "post" or "comment"
    subreddit_id: Optional[int] = None

class ContentModerationResponse(BaseModel):
    approved: bool
    suggestions: List[dict]
    rule_violations: List[dict]

class AutoConfigRequest(BaseModel):
    name: str
    description: str
    topics: List[str]
    moderation_style: str = "moderate"  # "strict", "moderate", "lenient"
    # Enhanced fields for better configuration
    brief_description: Optional[str] = None  # User's initial brief description
    target_audience: Optional[str] = None  # Who the subreddit is for
    content_types: Optional[List[str]] = None  # Allowed content types (text, image, link, video, etc.)
    community_goals: Optional[str] = None  # What the community aims to achieve
    moderation_philosophy: Optional[str] = None  # User's preferred approach to moderation
    language: Optional[str] = "en"  # Primary language of the community
    age_restriction: Optional[str] = "all"  # "all", "13+", "18+", "21+"
    content_rating: Optional[str] = "general"  # "general", "mature", "adult"

class RuleItem(BaseModel):
    title: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    category: str  # "behavior", "content", "spam", "safety", "community"
    enforcement_level: str  # "warning", "removal", "ban", "mute"
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
    min_account_age_hours: int
    min_karma_required: int
    max_posts_per_hour: int
    keyword_filters: List[str]
    image_moderation: bool
    link_validation: bool
    duplicate_detection: bool

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
    community_type: str  # "discussion", "support", "hobby", "professional", "entertainment"
    estimated_activity_level: str  # "low", "medium", "high", "very_high"
    configuration_notes: Optional[str] = None

class ContentDetectionRequest(BaseModel):
    content: str
    content_type: str = "post"  # "post" or "comment"

class ContentDetectionResponse(BaseModel):
    is_ai_generated: bool
    confidence: float
    detection_methods: List[dict]
    recommendations: List[dict]

@router.post("/ai/companion/query", response_model=AIQueryResponse)
async def query_ai_companion(
    request: AIQueryRequest,
    db: Session = Depends(get_db)
):
    """Query the AI companion for information about posts and subreddits"""
    try:
        result = await ai_companion_service.query_companion(
            query=request.query,
            subreddit_id=request.subreddit_id,
            context=request.context,
            db=db
        )
        return AIQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying AI companion: {str(e)}")

@router.post("/ai/moderate", response_model=ContentModerationResponse)
async def moderate_content(
    request: ContentModerationRequest,
    db: Session = Depends(get_db)
):
    """Moderate content for clarity, friendliness, and rule violations"""
    try:
        result = await content_moderation_service.moderate_content(
            content=request.content,
            content_type=request.content_type,
            subreddit_id=request.subreddit_id,
            db=db
        )
        return ContentModerationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error moderating content: {str(e)}")

@router.post("/ai/auto-config", response_model=AutoConfigResponse)
async def auto_configure_subreddit(
    request: AutoConfigRequest,
    db: Session = Depends(get_db)
):
    """Auto-configure a new subreddit with rules and settings"""
    try:
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
        return AutoConfigResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error auto-configuring subreddit: {str(e)}")

@router.post("/ai/detect-content", response_model=ContentDetectionResponse)
async def detect_ai_content(
    request: ContentDetectionRequest,
    db: Session = Depends(get_db)
):
    """Detect if content is AI-generated"""
    try:
        result = await content_detection_service.detect_content(
            content=request.content,
            content_type=request.content_type
        )
        return ContentDetectionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting content: {str(e)}")

@router.get("/ai/faq/{subreddit_name}")
async def get_subreddit_faq(
    subreddit_name: str,
    db: Session = Depends(get_db)
):
    """Get frequently asked questions for a subreddit"""
    try:
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
                "message": "No posts found to generate FAQs"
            }

        # Generate FAQ using AI
        faq_result = await ai_companion_service.generate_faq(
            subreddit=subreddit,
            posts=recent_posts
        )

        return {
            "subreddit": subreddit_name,
            "faqs": faq_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating FAQ: {str(e)}")

@router.get("/ai/trending-topics/{subreddit_name}")
async def get_trending_topics(
    subreddit_name: str,
    db: Session = Depends(get_db)
):
    """Get trending topics in a subreddit"""
    try:
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
                "message": "No posts found to analyze trends"
            }

        # Analyze trending topics using AI
        topics_result = await ai_companion_service.analyze_trending_topics(
            subreddit=subreddit,
            posts=recent_posts
        )

        return {
            "subreddit": subreddit_name,
            "trending_topics": topics_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing trending topics: {str(e)}")
