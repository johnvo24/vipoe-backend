from fastapi import APIRouter
from app.api.admin import admin_user

router = APIRouter()

router.include_router(admin_user.admin_router, prefix="/users", tags=["Admin - User Management"])
