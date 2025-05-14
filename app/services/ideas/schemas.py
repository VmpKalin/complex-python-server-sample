"""
Ideas schemas for input validation and serialization, simplified without user authentication.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

# Comment models
class CommentBase(BaseModel):
    content: str
    author: str = "Anonymous"

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: str
    idea_id: str
    date: str
    
    class Config:
        orm_mode = True

# Idea models
class IdeaBase(BaseModel):
    title: str
    description: str

class IdeaCreate(IdeaBase):
    author: str = "Anonymous"
    tags: List[str] = Field(default_factory=list)

class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class Idea(IdeaBase):
    id: str
    author: str
    date: str
    likes: int
    tags: List[str]
    userLiked: bool = False
    comments: int
    
    class Config:
        orm_mode = True

class IdeaDetail(Idea):
    comments_list: List[Comment] = Field(default_factory=list)
    
    class Config:
        orm_mode = True