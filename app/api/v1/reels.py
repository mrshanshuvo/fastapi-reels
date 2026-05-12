from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.reel import Reel
from app.schemas.reel import ReelCreate, ReelOut
from app.services.imagekit import get_imagekit_auth_params

router = APIRouter(prefix="/reels", tags=["Reels"])


@router.get("/upload-auth")
async def get_upload_authorization(current_user: User = Depends(get_current_user)):
    """
    Returns ImageKit credentials so the frontend can upload directly.
    User must be authenticated.
    """
    return {
        **get_imagekit_auth_params(),
        "authenticated": True,
        "user_id": str(current_user.id),
    }


@router.post("/", response_model=ReelOut, status_code=status.HTTP_201_CREATED)
async def create_reel(
    title: str = Form(...),
    description: str = Form(""),
    video_url: str = Form(...),
    thumbnail_url: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new reel record with provided video and thumbnail URLs.
    """
    reel = Reel(
        user_id=current_user.id,
        title=title,
        description=description,
        video_url=video_url,
        thumbnail_url=thumbnail_url,
        is_published=True,
    )
    db.add(reel)
    await db.commit()
    await db.refresh(reel)
    return reel


@router.get("/", response_model=list[ReelOut])
async def list_reels(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
):
    """
    List published reels (feed).
    No auth required — public endpoint.
    """
    from sqlalchemy import select

    stmt = (
        select(Reel)
        .where(Reel.is_published == True)
        .order_by(Reel.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    reels = result.scalars().all()
    return reels
