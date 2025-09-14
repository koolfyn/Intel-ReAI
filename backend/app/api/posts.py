from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional
from ..database import get_db
from ..models import Post, User, Subreddit
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    post_type: str
    label: Optional[str]
    author: dict
    subreddit: dict
    upvotes: int
    downvotes: int
    score: int
    comment_count: int
    is_ai_generated: bool
    ai_confidence: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

class PostCreate(BaseModel):
    title: str
    content: str
    subreddit_id: int
    post_type: str = "text"
    label: Optional[str] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    label: Optional[str] = None

@router.get("/posts/", response_model=dict)
async def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    subreddit_id: Optional[int] = Query(None),
    sort: str = Query("hot", regex="^(hot|new|top)$"),
    db: Session = Depends(get_db)
):
    """Get posts with pagination and filtering"""
    query = db.query(Post)

    if subreddit_id:
        query = query.filter(Post.subreddit_id == subreddit_id)

    # Apply sorting
    if sort == "hot":
        query = query.order_by(desc(Post.upvotes - Post.downvotes))
    elif sort == "new":
        query = query.order_by(desc(Post.created_at))
    elif sort == "top":
        query = query.order_by(desc(Post.upvotes))

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    posts = query.offset(offset).limit(limit).all()

    # Format response
    post_list = []
    for post in posts:
        post_list.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "post_type": post.post_type,
            "label": post.label,
            "author": {
                "id": post.author.id,
                "username": post.author.username,
                "display_name": post.author.display_name
            },
            "subreddit": {
                "id": post.subreddit.id,
                "name": post.subreddit.name,
                "display_name": post.subreddit.display_name
            },
            "upvotes": post.upvotes,
            "downvotes": post.downvotes,
            "score": post.score,
            "comment_count": post.comment_count,
            "is_ai_generated": post.is_ai_generated,
            "ai_confidence": post.ai_confidence,
            "created_at": post.created_at,
            "updated_at": post.updated_at
        })

    return {
        "posts": post_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific post by ID"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        post_type=post.post_type,
        label=post.label,
        author={
            "id": post.author.id,
            "username": post.author.username,
            "display_name": post.author.display_name
        },
        subreddit={
            "id": post.subreddit.id,
            "name": post.subreddit.name,
            "display_name": post.subreddit.display_name
        },
        upvotes=post.upvotes,
        downvotes=post.downvotes,
        score=post.score,
        comment_count=post.comment_count,
        is_ai_generated=post.is_ai_generated,
        ai_confidence=post.ai_confidence,
        created_at=post.created_at,
        updated_at=post.updated_at
    )

@router.post("/posts/", response_model=PostResponse)
async def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    """Create a new post"""
    # Verify subreddit exists
    subreddit = db.query(Subreddit).filter(Subreddit.id == post_data.subreddit_id).first()
    if not subreddit:
        raise HTTPException(status_code=404, detail="Subreddit not found")

    # For MVP, use a random user as author
    author = db.query(User).first()
    if not author:
        raise HTTPException(status_code=500, detail="No users found in database")

    post = Post(
        title=post_data.title,
        content=post_data.content,
        post_type=post_data.post_type,
        label=post_data.label,
        author_id=author.id,
        subreddit_id=post_data.subreddit_id
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        post_type=post.post_type,
        label=post.label,
        author={
            "id": post.author.id,
            "username": post.author.username,
            "display_name": post.author.display_name
        },
        subreddit={
            "id": post.subreddit.id,
            "name": post.subreddit.name,
            "display_name": post.subreddit.display_name
        },
        upvotes=post.upvotes,
        downvotes=post.downvotes,
        score=post.score,
        comment_count=post.comment_count,
        is_ai_generated=post.is_ai_generated,
        ai_confidence=post.ai_confidence,
        created_at=post.created_at,
        updated_at=post.updated_at
    )

@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db)
):
    """Update a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post_data.title is not None:
        post.title = post_data.title
    if post_data.content is not None:
        post.content = post_data.content
    if post_data.label is not None:
        post.label = post_data.label

    post.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(post)

    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        post_type=post.post_type,
        label=post.label,
        author={
            "id": post.author.id,
            "username": post.author.username,
            "display_name": post.author.display_name
        },
        subreddit={
            "id": post.subreddit.id,
            "name": post.subreddit.name,
            "display_name": post.subreddit.display_name
        },
        upvotes=post.upvotes,
        downvotes=post.downvotes,
        score=post.score,
        comment_count=post.comment_count,
        is_ai_generated=post.is_ai_generated,
        ai_confidence=post.ai_confidence,
        created_at=post.created_at,
        updated_at=post.updated_at
    )

@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    """Delete a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()

    return {"message": "Post deleted successfully"}

@router.post("/posts/{post_id}/upvote")
async def upvote_post(post_id: int, db: Session = Depends(get_db)):
    """Upvote a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.upvotes += 1
    db.commit()

    return {"message": "Post upvoted", "upvotes": post.upvotes}

@router.post("/posts/{post_id}/downvote")
async def downvote_post(post_id: int, db: Session = Depends(get_db)):
    """Downvote a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.downvotes += 1
    db.commit()

    return {"message": "Post downvoted", "downvotes": post.downvotes}
