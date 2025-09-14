from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    post_type = Column(String(20), default="text")  # text, link, image
    label = Column(String(100), nullable=True)  # Custom label for posts
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subreddit_id = Column(Integer, ForeignKey("subreddits.id"), nullable=False)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    is_ai_generated = Column(Boolean, default=False)
    ai_confidence = Column(Integer, nullable=True)  # 0-100 confidence score
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("User", back_populates="posts")
    subreddit = relationship("Subreddit", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    @property
    def score(self):
        return self.upvotes - self.downvotes

    @property
    def comment_count(self):
        return len(self.comments)
