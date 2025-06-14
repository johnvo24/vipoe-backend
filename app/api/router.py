from fastapi import APIRouter
from app.api import auth, poems, collections

router = APIRouter()
router.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# router.include_router(users.router, prefix="/api/v1/user", tags=["User"])
# router.include_router(poems.router, prefix="/api/v1/poem", tags=["Poem"])
# router.include_router(collections.router, prefix="/api/v1/collection", tags=["Collection"])