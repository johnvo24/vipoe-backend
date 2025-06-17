from fastapi import APIRouter
from app.api.collection import crud, fetch

router = APIRouter()

router.include_router(crud.router, prefix="/collection", tags=["Collection"])
router.include_router(fetch.router, prefix="/collection", tags=["Collection"])