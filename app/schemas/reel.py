from pydantic import BaseModel
from typing import Optional


class ReelCreate(BaseModel):
    title: str
    description: str = ""


class ReelOut(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    video_url: str
    thumbnail_url: str
    duration: int
    views_count: int
    likes_count: int
    comments_count: int
    shares_count: int
    is_published: bool
    created_at: str

    class Config:
        from_attributes = True
