from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import CollectionPoem
from app.auth.dependencies import get_current_user
from app.models.poem import Poem
from app.schemas.poem import PoemResponse
from app.services.poem_service import build_poem_response

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[PoemResponse])
def get_poems_in_collection(
  db: Session = Depends(get_db),
  offset: int = 0,
  limit: int = 20,
  current_user = Depends(get_current_user)
):
  collection = db.query(CollectionPoem).filter_by(user_id=current_user.id).all()
  if not collection:
    raise HTTPException(status_code=404, detail="No poems found in collection")
  poem_ids = [cp.poem_id for cp in collection]
  poems = (
    db.query(Poem)
    .options(joinedload(Poem.genre), joinedload(Poem.poem_tags), joinedload(Poem.user))
    .filter(Poem.id.in_(poem_ids))
    .offset(offset)
    .limit(limit)
    .all()
  )
  return [build_poem_response(poem, like_count=0, is_saved=True, is_liked=False) for poem in poems]