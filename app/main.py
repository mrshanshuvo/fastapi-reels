from fastapi import FastAPI
from app.api.v1 import auth, users, reels
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(reels.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"status": "alive", "project": settings.PROJECT_NAME}
