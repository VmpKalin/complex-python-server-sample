"""
Posts schemas for input validation and serialization, simplified without user authentication.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Comment models
class PostCommentBase(BaseModel):
    content: str
    author: str = "Anonymous"

class PostCommentCreate(PostCommentBase):
    pass

class PostComment(PostCommentBase):
    id: str
    post_id: str
    created_at: str
    
    class Config:
        orm_mode = True

# Post models
class PostBase(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None

class PostCreate(PostBase):
    author: str = "Anonymous"
    tags: List[str] = Field(default_factory=list)
    is_published: bool = False

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None

class Post(BaseModel):
    id: str
    title: str
    content: str
    excerpt: Optional[str] = None
    author: str
    created_at: str
    updated_at: str
    published_at: Optional[str] = None
    is_published: bool
    tags: List[str]
    comments_count: int
    
    class Config:
        orm_mode = True

class PostDetail(Post):
    comments: List[PostComment] = Field(default_factory=list)
    
    class Config:
        orm_mode = True