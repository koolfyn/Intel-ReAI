from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Tuple
from ..database import get_db
from ..models import Comment, Post
from ..config import settings
from pydantic import BaseModel
import os
import anthropic

router = APIRouter()

# ---------- Pydantic Models ----------
class SummarizePostResponse(BaseModel):
    success: bool
    message: str
    post_summary: Optional[str] = None
    comments_summary: Optional[str] = None
    full_summary: Optional[str] = None

class ValidateKeyResponse(BaseModel):
    success: bool
    message: str
    is_valid: bool


# ---------- Service Layer ----------
class SummarizerService:
    @staticmethod
    def get_api_key() -> str:
        api_key = settings.ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
    
        if not api_key:
            raise ValueError("Claude API key not provided. Set ANTHROPIC_API_KEY env variable.")
        return api_key

    @staticmethod
    def get_client(api_key: Optional[str] = None) -> anthropic.Anthropic:
        return anthropic.Anthropic(api_key=api_key or SummarizerService.get_api_key())

    @staticmethod
    def validate_claude_key(api_key: str) -> Tuple[bool, str]:
        try:
            client = SummarizerService.get_client(api_key)
            client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=5,
                messages=[{"role": "user", "content": "ping"}]
            )
            return True, "Key is valid"
        except anthropic.APIStatusError as e:
            if e.status_code == 401:
                return False, "Authentication failed (401). Check your key."
            return False, f"API error {e.status_code}: {e}"
        except Exception as e:
            return False, f"Error validating key: {str(e)}"

    @staticmethod
    def summarize_text(text: str, context: str = "content") -> str:
        if not text.strip():
            return f"No {context} to summarize."

        client = SummarizerService.get_client()
        prompt = f"Summarize the following {context} in 2–3 sentences:\n\n{text}"

        try:
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                system="You are a helpful assistant that creates concise summaries.",
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Failed to summarize {context}: {str(e)}"

    @staticmethod
    def get_post_and_comments(db: Session, post_id: int) -> Tuple[Optional[Post], List[Comment]]:
        post = db.query(Post).filter(Post.id == post_id).first()
        comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(desc(Comment.created_at)).limit(20).all()
        return post, comments

    @staticmethod
    def summarize_post_and_comments(db: Session, post_id: int) -> Tuple[str, str, str]:
        post, comments = SummarizerService.get_post_and_comments(db, post_id)
        if not post:
            return "Post not found", "", ""

        post_summary = SummarizerService.summarize_text(f"Title: {post.title}\nContent: {post.content}", "post")

        if comments:
            comments_text = "\n".join(
                [f"{c.author.username if c.author else 'Unknown'}: {c.content}" for c in comments]
            )
            comments_summary = SummarizerService.summarize_text(comments_text, "comments")
        else:
            comments_text, comments_summary = "No comments", "No comments to summarize."

        full_content = f"Post: {post.title}\n{post.content}\n\nComments:\n{comments_text}"
        full_summary = SummarizerService.summarize_text(full_content, "discussion")

        return post_summary, comments_summary, full_summary


# ---------- API Routes ----------
@router.get("/summarize-post/{post_id}", response_model=SummarizePostResponse)
def summarize_post(post_id: int, db: Session = Depends(get_db)):
    try:
        post_summary, comments_summary, full_summary = SummarizerService.summarize_post_and_comments(db, post_id)
        return SummarizePostResponse(
            success=True,
            message="Post and comments summarized successfully",
            post_summary=post_summary,
            comments_summary=comments_summary,
            full_summary=full_summary
        )
    except Exception as e:
        return SummarizePostResponse(success=False, message=str(e))

@router.get("/summarize-text")
def summarize_text(text: str = Query(..., description="Text to summarize")):
    if not text.strip():
        return {"success": False, "message": "Text cannot be empty", "summary": None}
    summary = SummarizerService.summarize_text(text, "text")
    return {"success": True, "message": "Text summarized successfully", "summary": summary}

@router.get("/validate-claude-key", response_model=ValidateKeyResponse)
def validate_claude_key(api_key: str = Query(..., description="Claude API key")):
    is_valid, message = SummarizerService.validate_claude_key(api_key)
    return ValidateKeyResponse(success=True, message=message, is_valid=is_valid)
