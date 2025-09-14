from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Subreddit, User, Post
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class SubredditResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    rules: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    post_count: int
    subscriber_count: int = 0  # For MVP, we'll set this to 0

class SubredditCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    rules: Optional[str] = None
    auto_configure: bool = False

class SubredditUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[str] = None

@router.get("/subreddits/", response_model=dict)
async def get_subreddits(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get subreddits with pagination and search"""
    query = db.query(Subreddit)

    if search:
        query = query.filter(
            Subreddit.name.contains(search) |
            Subreddit.display_name.contains(search) |
            Subreddit.description.contains(search)
        )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    subreddits = query.offset(offset).limit(limit).all()

    # Format response
    subreddit_list = []
    for subreddit in subreddits:
        post_count = db.query(Post).filter(Post.subreddit_id == subreddit.id).count()
        subreddit_list.append({
            "id": subreddit.id,
            "name": subreddit.name,
            "display_name": subreddit.display_name,
            "description": subreddit.description,
            "rules": subreddit.rules,
            "created_by": subreddit.created_by,
            "created_at": subreddit.created_at,
            "updated_at": subreddit.updated_at,
            "post_count": post_count,
            "subscriber_count": 0  # MVP: no user subscriptions
        })

    return {
        "subreddits": subreddit_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }

@router.get("/subreddits/{subreddit_name}", response_model=SubredditResponse)
async def get_subreddit(subreddit_name: str, db: Session = Depends(get_db)):
    """Get a specific subreddit by name"""
    subreddit = db.query(Subreddit).filter(Subreddit.name == subreddit_name).first()
    if not subreddit:
        raise HTTPException(status_code=404, detail="Subreddit not found")

    post_count = db.query(Post).filter(Post.subreddit_id == subreddit.id).count()

    return SubredditResponse(
        id=subreddit.id,
        name=subreddit.name,
        display_name=subreddit.display_name,
        description=subreddit.description,
        rules=subreddit.rules,
        created_by=subreddit.created_by,
        created_at=subreddit.created_at,
        updated_at=subreddit.updated_at,
        post_count=post_count,
        subscriber_count=0  # MVP: no user subscriptions
    )

@router.post("/subreddits/", response_model=SubredditResponse)
async def create_subreddit(
    subreddit_data: SubredditCreate,
    db: Session = Depends(get_db)
):
    """Create a new subreddit"""
    # Check if subreddit name already exists
    existing = db.query(Subreddit).filter(Subreddit.name == subreddit_data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Subreddit name already exists")

    # For MVP, use a random user as creator
    creator = db.query(User).first()
    if not creator:
        raise HTTPException(status_code=500, detail="No users found in database")

    subreddit = Subreddit(
        name=subreddit_data.name,
        display_name=subreddit_data.display_name,
        description=subreddit_data.description,
        rules=subreddit_data.rules,
        created_by=creator.id
    )

    db.add(subreddit)
    db.commit()
    db.refresh(subreddit)

    return SubredditResponse(
        id=subreddit.id,
        name=subreddit.name,
        display_name=subreddit.display_name,
        description=subreddit.description,
        rules=subreddit.rules,
        created_by=subreddit.created_by,
        created_at=subreddit.created_at,
        updated_at=subreddit.updated_at,
        post_count=0,
        subscriber_count=0
    )

@router.put("/subreddits/{subreddit_name}", response_model=SubredditResponse)
async def update_subreddit(
    subreddit_name: str,
    subreddit_data: SubredditUpdate,
    db: Session = Depends(get_db)
):
    """Update a subreddit"""
    subreddit = db.query(Subreddit).filter(Subreddit.name == subreddit_name).first()
    if not subreddit:
        raise HTTPException(status_code=404, detail="Subreddit not found")

    if subreddit_data.display_name is not None:
        subreddit.display_name = subreddit_data.display_name
    if subreddit_data.description is not None:
        subreddit.description = subreddit_data.description
    if subreddit_data.rules is not None:
        subreddit.rules = subreddit_data.rules

    subreddit.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(subreddit)

    post_count = db.query(Post).filter(Post.subreddit_id == subreddit.id).count()

    return SubredditResponse(
        id=subreddit.id,
        name=subreddit.name,
        display_name=subreddit.display_name,
        description=subreddit.description,
        rules=subreddit.rules,
        created_by=subreddit.created_by,
        created_at=subreddit.created_at,
        updated_at=subreddit.updated_at,
        post_count=post_count,
        subscriber_count=0
    )

@router.delete("/subreddits/{subreddit_name}")
async def delete_subreddit(subreddit_name: str, db: Session = Depends(get_db)):
    """Delete a subreddit"""
    subreddit = db.query(Subreddit).filter(Subreddit.name == subreddit_name).first()
    if not subreddit:
        raise HTTPException(status_code=404, detail="Subreddit not found")

    db.delete(subreddit)
    db.commit()

    return {"message": "Subreddit deleted successfully"}
