from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from ..database import get_db
from ..models import Comment, Post, User
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class CommentResponse(BaseModel):
    id: int
    content: str
    author: dict
    post_id: int
    parent_id: Optional[int]
    upvotes: int
    downvotes: int
    score: int
    is_ai_generated: bool
    ai_confidence: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    replies: List['CommentResponse'] = []

class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[int] = None

class CommentUpdate(BaseModel):
    content: str

# Update forward reference
CommentResponse.model_rebuild()

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def get_post_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get comments for a specific post"""
    # Verify post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Get top-level comments (no parent)
    query = db.query(Comment).filter(
        Comment.post_id == post_id,
        Comment.parent_id.is_(None)
    ).order_by(desc(Comment.upvotes - Comment.downvotes))

    # Apply pagination
    offset = (page - 1) * limit
    comments = query.offset(offset).limit(limit).all()

    # Format response with nested replies
    comment_list = []
    for comment in comments:
        comment_list.append(_format_comment(comment, db))

    return comment_list

@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db)
):
    """Create a new comment"""
    # Verify post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Verify parent comment exists if specified
    if comment_data.parent_id:
        parent = db.query(Comment).filter(Comment.id == comment_data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")

    # For MVP, use a random user as author
    author = db.query(User).first()
    if not author:
        raise HTTPException(status_code=500, detail="No users found in database")

    comment = Comment(
        content=comment_data.content,
        author_id=author.id,
        post_id=post_id,
        parent_id=comment_data.parent_id
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return _format_comment(comment, db)

@router.get("/comments/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """Get a specific comment by ID"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return _format_comment(comment, db)

@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db)
):
    """Update a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.content = comment_data.content
    comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(comment)

    return _format_comment(comment, db)

@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """Delete a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully"}

@router.post("/comments/{comment_id}/upvote")
async def upvote_comment(comment_id: int, db: Session = Depends(get_db)):
    """Upvote a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.upvotes += 1
    db.commit()

    return {"message": "Comment upvoted", "upvotes": comment.upvotes}

@router.post("/comments/{comment_id}/downvote")
async def downvote_comment(comment_id: int, db: Session = Depends(get_db)):
    """Downvote a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.downvotes += 1
    db.commit()

    return {"message": "Comment downvoted", "downvotes": comment.downvotes}

def _format_comment(comment: Comment, db: Session) -> CommentResponse:
    """Helper function to format comment with nested replies"""
    # Get replies for this comment
    replies = db.query(Comment).filter(
        Comment.parent_id == comment.id
    ).order_by(desc(Comment.upvotes - Comment.downvotes)).all()

    # Format replies recursively
    reply_list = []
    for reply in replies:
        reply_list.append(_format_comment(reply, db))

    return CommentResponse(
        id=comment.id,
        content=comment.content,
        author={
            "id": comment.author.id,
            "username": comment.author.username,
            "display_name": comment.author.display_name
        },
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        upvotes=comment.upvotes,
        downvotes=comment.downvotes,
        score=comment.score,
        is_ai_generated=comment.is_ai_generated,
        ai_confidence=comment.ai_confidence,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        replies=reply_list
    )
