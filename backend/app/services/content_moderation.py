from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import Subreddit
from .claude_service import ClaudeService
import logging

logger = logging.getLogger(__name__)

class ContentModerationService:
    def __init__(self):
        self.claude_service = ClaudeService()

    async def moderate_content(
        self,
        content: str,
        content_type: str = "post",
        subreddit_id: Optional[int] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Moderate content for clarity, friendliness, and rule violations"""
        try:
            # Get subreddit context if provided
            subreddit_context = ""
            if subreddit_id and db:
                subreddit = db.query(Subreddit).filter(Subreddit.id == subreddit_id).first()
                if subreddit:
                    subreddit_context = f"""
                    Subreddit: {subreddit.display_name}
                    Description: {subreddit.description or 'No description'}
                    Rules: {subreddit.rules or 'No specific rules'}
                    """

            # Use Claude service to analyze content
            result = await self.claude_service.analyze_content(
                content=content,
                context=subreddit_context
            )

            # Ensure the result has the expected structure
            if not isinstance(result, dict):
                result = {
                    "approved": True,
                    "suggestions": [],
                    "rule_violations": [],
                    "tone_analysis": {"friendliness_score": 80, "clarity_score": 80}
                }

            # Add additional analysis based on content type
            if content_type == "post":
                result["suggestions"].extend(self._analyze_post_structure(content))
            elif content_type == "comment":
                result["suggestions"].extend(self._analyze_comment_quality(content))

            return result

        except Exception as e:
            logger.error(f"Error moderating content: {e}")
            return {
                "approved": True,
                "suggestions": [],
                "rule_violations": [],
                "tone_analysis": {"friendliness_score": 80, "clarity_score": 80}
            }

    def _analyze_post_structure(self, content: str) -> list:
        """Analyze post structure and provide suggestions"""
        suggestions = []

        # Check for very short posts
        if len(content.strip()) < 50:
            suggestions.append({
                "type": "clarity",
                "message": "Post is quite short",
                "suggestion": "Consider adding more details or context to help others understand your question or topic",
                "severity": "low"
            })

        # Check for very long posts
        if len(content.strip()) > 2000:
            suggestions.append({
                "type": "clarity",
                "message": "Post is quite long",
                "suggestion": "Consider breaking this into multiple posts or adding a summary at the top",
                "severity": "low"
            })

        # Check for all caps
        if content.isupper() and len(content) > 10:
            suggestions.append({
                "type": "friendliness",
                "message": "Text is in all caps",
                "suggestion": "Consider using normal capitalization for better readability",
                "severity": "medium"
            })

        # Check for excessive punctuation
        if content.count('!') > 5 or content.count('?') > 5:
            suggestions.append({
                "type": "friendliness",
                "message": "Excessive punctuation",
                "suggestion": "Consider reducing the number of exclamation marks or question marks",
                "severity": "low"
            })

        return suggestions

    def _analyze_comment_quality(self, content: str) -> list:
        """Analyze comment quality and provide suggestions"""
        suggestions = []

        # Check for very short comments
        if len(content.strip()) < 10:
            suggestions.append({
                "type": "clarity",
                "message": "Comment is very short",
                "suggestion": "Consider adding more context or explanation to your comment",
                "severity": "low"
            })

        # Check for single character responses
        if len(content.strip()) == 1 and content.strip() in "!?.,;:":
            suggestions.append({
                "type": "clarity",
                "message": "Comment is just punctuation",
                "suggestion": "Consider adding actual text to your comment",
                "severity": "medium"
            })

        # Check for repetitive characters
        if len(set(content.strip())) < 3 and len(content.strip()) > 5:
            suggestions.append({
                "type": "friendliness",
                "message": "Comment appears to be repetitive",
                "suggestion": "Consider using actual words instead of repeated characters",
                "severity": "medium"
            })

        return suggestions
