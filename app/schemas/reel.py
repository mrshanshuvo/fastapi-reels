import uuid
from datetime import datetime
from pydantic import BaseModel


class ReelCreate(BaseModel):
    title: str
    description: str = ""
    video_url: str
    thumbnail_url: str


class ReelOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
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
    created_at: datetime

    class Config:
        from_attributes = True
