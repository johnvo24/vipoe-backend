from fastapi import APIRouter
from app.modules.assistant import chat_api

router = APIRouter()
router.include_router(chat_api.router, prefix="/assistant", tags=["Assistant"])