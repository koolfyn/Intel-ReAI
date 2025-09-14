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
    """Search posts using SQLite FTS5"""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    # Build the search query
    if subreddit:
        # Search within specific subreddit
        subreddit_obj = db.query(Subreddit).filter(Subreddit.name == subreddit).first()
        if not subreddit_obj:
            raise HTTPException(status_code=404, detail="Subreddit not found")

        query = text("""
            SELECT p.id, p.title, p.content, p.upvotes, p.downvotes, p.created_at,
                   u.username, u.display_name, s.name as subreddit_name, s.display_name as subreddit_display_name
            FROM posts_fts fts
            JOIN posts p ON fts.content_rowid = p.id
            JOIN users u ON p.author_id = u.id
            JOIN subreddits s ON p.subreddit_id = s.id
            WHERE posts_fts MATCH :query AND p.subreddit_id = :subreddit_id
        """)
        params = {"query": q, "subreddit_id": subreddit_obj.id}
    else:
        # Search all posts
        query = text("""
            SELECT p.id, p.title, p.content, p.upvotes, p.downvotes, p.created_at,
                   u.username, u.display_name, s.name as subreddit_name, s.display_name as subreddit_display_name
            FROM posts_fts fts
            JOIN posts p ON fts.content_rowid = p.id
            JOIN users u ON p.author_id = u.id
            JOIN subreddits s ON p.subreddit_id = s.id
            WHERE posts_fts MATCH :query
        """)
        params = {"query": q}

    # Apply sorting
    if sort == "date":
        query = text(str(query) + " ORDER BY p.created_at DESC")
    elif sort == "score":
        query = text(str(query) + " ORDER BY (p.upvotes - p.downvotes) DESC")
    else:  # relevance
        query = text(str(query) + " ORDER BY rank")

    # Apply pagination
    offset = (page - 1) * limit
    query = text(str(query) + f" LIMIT {limit} OFFSET {offset}")

    # Execute query
    result = db.execute(query, params).fetchall()

    # Format results
    posts = []
    for row in result:
        posts.append({
            "id": row.id,
            "title": row.title,
            "content": row.content,
            "type": "post",
            "author": {
                "username": row.username,
                "display_name": row.display_name
            },
            "subreddit": {
                "name": row.subreddit_name,
                "display_name": row.subreddit_display_name
            },
            "score": row.upvotes - row.downvotes,
            "created_at": row.created_at.isoformat()
        })

    return {
        "query": q,
        "results": posts,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": len(posts)  # This is approximate for FTS5
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
    """Advanced search with multiple filters"""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")

    # Start with basic search
    query = text("""
        SELECT p.id, p.title, p.content, p.upvotes, p.downvotes, p.created_at,
               u.username, u.display_name, s.name as subreddit_name, s.display_name as subreddit_display_name
        FROM posts_fts fts
        JOIN posts p ON fts.content_rowid = p.id
        JOIN users u ON p.author_id = u.id
        JOIN subreddits s ON p.subreddit_id = s.id
        WHERE posts_fts MATCH :query
    """)

    params = {"query": q}

    # Add filters
    filters = []
    if subreddit:
        subreddit_obj = db.query(Subreddit).filter(Subreddit.name == subreddit).first()
        if not subreddit_obj:
            raise HTTPException(status_code=404, detail="Subreddit not found")
        filters.append("p.subreddit_id = :subreddit_id")
        params["subreddit_id"] = subreddit_obj.id

    if author:
        author_obj = db.query(User).filter(User.username == author).first()
        if not author_obj:
            raise HTTPException(status_code=404, detail="Author not found")
        filters.append("p.author_id = :author_id")
        params["author_id"] = author_obj.id

    if date_from:
        filters.append("p.created_at >= :date_from")
        params["date_from"] = date_from

    if date_to:
        filters.append("p.created_at <= :date_to")
        params["date_to"] = date_to

    # Apply filters
    if filters:
        query = text(str(query) + " AND " + " AND ".join(filters))

    # Order by relevance
    query = text(str(query) + " ORDER BY rank")

    # Apply pagination
    offset = (page - 1) * limit
    query = text(str(query) + f" LIMIT {limit} OFFSET {offset}")

    # Execute query
    result = db.execute(query, params).fetchall()

    # Format results
    posts = []
    for row in result:
        posts.append({
            "id": row.id,
            "title": row.title,
            "content": row.content,
            "type": "post",
            "author": {
                "username": row.username,
                "display_name": row.display_name
            },
            "subreddit": {
                "name": row.subreddit_name,
                "display_name": row.subreddit_display_name
            },
            "score": row.upvotes - row.downvotes,
            "created_at": row.created_at.isoformat()
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
            "total": len(posts)
        }
    }
