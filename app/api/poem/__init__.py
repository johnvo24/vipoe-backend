from fastapi import APIRouter
from app.api.poem import crud, fetch, comment

router = APIRouter()

router.include_router(fetch.router, prefix="/poem", tags=["Poem > Fetch"])
router.include_router(crud.router, prefix="/poem", tags=["Poem > CRUD"])
router.include_router(comment.router, prefix="/poem", tags=["Poem > Comments"])