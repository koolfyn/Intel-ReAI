from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from ..database import get_db
from ..models import Post, Subreddit, User
from pydantic import BaseModel

router = APIRouter()

class SearchResult(BaseModel):
    id: int
    title: str
    content: str
    type: str  # "post" or "comment"
    author: dict
    subreddit: dict
    score: int
    created_at: str

@router.get("/search/posts")
async def search_posts(
    q: str = Query(..., description="Search query"),
    subreddit: Optional[str] = Query(None, description="Filter by subreddit name"),
    sort: str = Query("relevance", regex="^(relevance|date|score)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search posts using simple LIKE search (lightweight implementation)"""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    # Build the search query using simple LIKE search
    search_filter = f"%{q}%"

    if subreddit:
        # Search within specific subreddit
        subreddit_obj = db.query(Subreddit).filter(Subreddit.name == subreddit).first()
        if not subreddit_obj:
            raise HTTPException(status_code=404, detail="Subreddit not found")

        query = db.query(Post).filter(
            Post.subreddit_id == subreddit_obj.id,
            (Post.title.ilike(f'%{q}%') | Post.content.ilike(f'%{q}%'))
        )
    else:
        # Search all posts
        query = db.query(Post).filter(
            Post.title.ilike(f'%{q}%') | Post.content.ilike(f'%{q}%')
        )

    # Apply sorting
    if sort == "date":
        query = query.order_by(Post.created_at.desc())
    elif sort == "score":
        query = query.order_by((Post.upvotes - Post.downvotes).desc())
    else:  # relevance - order by score for now
        query = query.order_by((Post.upvotes - Post.downvotes).desc())

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    posts_result = query.offset(offset).limit(limit).all()

    # Format results
    posts = []
    for post in posts_result:
        posts.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "type": "post",
            "author": {
                "username": post.author.username,
                "display_name": post.author.display_name
            },
            "subreddit": {
                "name": post.subreddit.name,
                "display_name": post.subreddit.display_name
            },
            "score": post.upvotes - post.downvotes,
            "created_at": post.created_at.isoformat()
        })

    return {
        "query": q,
        "results": posts,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }

@router.get("/search/subreddits")
async def search_subreddits(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search subreddits by name and description"""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    query = db.query(Subreddit).filter(
        Subreddit.name.contains(q) |
        Subreddit.display_name.contains(q) |
        Subreddit.description.contains(q)
    )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    subreddits = query.offset(offset).limit(limit).all()

    # Format results
    results = []
    for subreddit in subreddits:
        post_count = db.query(Post).filter(Post.subreddit_id == subreddit.id).count()
        results.append({
            "id": subreddit.id,
            "name": subreddit.name,
            "display_name": subreddit.display_name,
            "description": subreddit.description,
            "post_count": post_count,
            "created_at": subreddit.created_at.isoformat()
        })

    return {
        "query": q,
        "results": results,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }

@router.get("/search/advanced")
async def advanced_search(
    q: str = Query(..., description="Search query"),
    subreddit: Optional[str] = Query(None, description="Filter by subreddit name"),
    author: Optional[str] = Query(None, description="Filter by author username"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Advanced search with multiple filters using simple LIKE search"""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    # Start with basic search
    query = db.query(Post).filter(
        Post.title.ilike(f'%{q}%') | Post.content.ilike(f'%{q}%')
    )

    # Add filters
    if subreddit:
        subreddit_obj = db.query(Subreddit).filter(Subreddit.name == subreddit).first()
        if not subreddit_obj:
            raise HTTPException(status_code=404, detail="Subreddit not found")
        query = query.filter(Post.subreddit_id == subreddit_obj.id)

    if author:
        author_obj = db.query(User).filter(User.username == author).first()
        if not author_obj:
            raise HTTPException(status_code=404, detail="Author not found")
        query = query.filter(Post.author_id == author_obj.id)

    if date_from:
        from datetime import datetime
        try:
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.filter(Post.created_at >= date_from_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format. Use YYYY-MM-DD")

    if date_to:
        from datetime import datetime
        try:
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
            query = query.filter(Post.created_at <= date_to_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format. Use YYYY-MM-DD")

    # Order by score (relevance)
    query = query.order_by((Post.upvotes - Post.downvotes).desc())

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    posts_result = query.offset(offset).limit(limit).all()

    # Format results
    posts = []
    for post in posts_result:
        posts.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "type": "post",
            "author": {
                "username": post.author.username,
                "display_name": post.author.display_name
            },
            "subreddit": {
                "name": post.subreddit.name,
                "display_name": post.subreddit.display_name
            },
            "score": post.upvotes - post.downvotes,
            "created_at": post.created_at.isoformat()
        })

    return {
        "query": q,
        "filters": {
            "subreddit": subreddit,
            "author": author,
            "date_from": date_from,
            "date_to": date_to
        },
        "results": posts,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }
