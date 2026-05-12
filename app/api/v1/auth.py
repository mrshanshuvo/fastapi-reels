from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.dependencies import get_db
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    # Check if username or email exists
    stmt = select(User).where((User.username == username) | (User.email == email))
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )

    hashed_pw = get_password_hash(password)
    user = User(username=username, email=email, hashed_password=hashed_pw)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(
    username_or_email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    # Allow logging in with either email or username
    stmt = select(User).where(
        (User.email == username_or_email) | (User.username == username_or_email)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
