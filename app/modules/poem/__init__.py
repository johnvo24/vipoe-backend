from fastapi import APIRouter
from app.modules.poem import crud, fetch

router = APIRouter()

router.include_router(fetch.router, prefix="/poem", tags=["Poem > Fetch"])
router.include_router(crud.router, prefix="/poem", tags=["Poem > CRUD"])