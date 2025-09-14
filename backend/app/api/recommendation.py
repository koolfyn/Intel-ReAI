
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from ..database import get_db
from ..models import Comment, Post, User, SearchHistory
from pydantic import BaseModel
from datetime import datetime

class SearchHistoryBase(BaseModel):
    user_id: int
    searched_keyword: str

# Schema for creating a new search history entry (input)
class SearchHistoryCreate(SearchHistoryBase):
    pass

# Schema for updating a search history entry (input)
class SearchHistoryUpdate(BaseModel):
    user_id: Optional[int] = None
    searched_keyword: Optional[str] = None

# Schema for returning search history data (output)
class SearchHistory(SearchHistoryBase):
    id: int
    
    class Config:
        from_attributes = True



# Schema for search history response (output)
class SearchHistoryResponse(BaseModel):
    success: bool
    message: str
    data: Optional[SearchHistory] = None

# Schema for search history list response (output)
class SearchHistoryListResponse(BaseModel):
    success: bool
    message: str
    data: list[SearchHistory]
    total: int





router = APIRouter()

@router.get("/search-history", response_model=SearchHistoryListResponse)
def get_all_search_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all search history entries with pagination
    """
    try:
        # Query all search history entries with pagination
        search_history_list = db.query(SearchHistory).offset(skip).limit(limit).all()
        total_count = db.query(SearchHistory).count()
        
        return SearchHistoryListResponse(
            success=True,
            message="Search history retrieved successfully",
            data=search_history_list,
            total=total_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve search history: {str(e)}"
        )


#This will be the search history by the user id. 

@router.get("/search-history/{user_id}", response_model=SearchHistoryListResponse)
def get_search_history_by_user(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get search history entries for a specific user with pagination
    """
    try:
        # Query search history for specific user with pagination
        search_history_list = db.query(SearchHistory).filter(
            SearchHistory.user_id == user_id
        ).offset(skip).limit(limit).all()
        
        total_count = db.query(SearchHistory).filter(
            SearchHistory.user_id == user_id
        ).count()
        
        return SearchHistoryListResponse(
            success=True,
            message=f"Search history for user {user_id} retrieved successfully",
            data=search_history_list,
            total=total_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve search history for user {user_id}: {str(e)}"
        )
