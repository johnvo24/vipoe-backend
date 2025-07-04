from fastapi import APIRouter
from app.api import collection, poem, user, assistant

router = APIRouter()

router.include_router(user.router, prefix="/api/v1")
router.include_router(poem.router, prefix="/api/v1")
router.include_router(collection.router, prefix="/api/v1")
router.include_router(assistant.router, prefix="/api/v1")