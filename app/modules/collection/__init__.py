from fastapi import APIRouter
from app.modules.collection import crud, fetch

router = APIRouter()

router.include_router(crud.router, prefix="/collection", tags=["Collection"])
router.include_router(fetch.router, prefix="/collection", tags=["Collection"])