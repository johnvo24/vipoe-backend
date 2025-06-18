from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.poem import PoemLike
from app.models.user import User
from app.schemas.poem import PoemBaseResponse, PoemResponse, GenreResponse, TagResponse
from app.models import Poem, Genre, Tag, PoemTag
from typing import Optional
from sqlalchemy import func, or_
from app.services.poem_service import build_poem_response

router = APIRouter()

@router.get("/genres", response_model=list[GenreResponse])
def get_genres(db: Session = Depends(get_db)):
  print("Fetching genres")
  return db.query(Genre).all()

@router.get("/tags", response_model=list[TagResponse])
def get_tags(db: Session = Depends(get_db)):
  return db.query(Tag).all()

@router.get("/search", response_model=List[PoemResponse])
def search_poems(
  db: Session = Depends(get_db),
  keyword: Optional[str] = None,
  tags: Optional[str] = None,  # đổi từ 'tag' sang 'tags'
  genre_id: Optional[int] = None,
  offset: int = 0,
  limit: int = 20,
):
  query = db.query(Poem).options(
    joinedload(Poem.genre), joinedload(Poem.poem_tags), joinedload(Poem.user)
  ).filter(Poem.is_public == True)

  if keyword:
    query = query.filter(
      or_(
        Poem.title.ilike(f"%{keyword}%"),
        Poem.content.ilike(f"%{keyword}%"),
        Poem.prompt.ilike(f"%{keyword}%"),
        Poem.note.ilike(f"%{keyword}%"),
      )
    )
  if genre_id:
    query = query.filter(Poem.genre_id == genre_id)
  if tags:
    tag_list = [t.strip() for t in tags.split("#") if t.strip()]
    if tag_list:
      for tag_name in tag_list:
        query = query.join(PoemTag, Poem.poem_tags).join(Tag).filter(Tag.name == tag_name)

  poems = query.order_by(Poem.created_at.desc()).offset(offset).limit(limit).all()
  return [build_poem_response(poem) for poem in poems]

@router.get("/feed", response_model=List[PoemResponse])
def get_poem_feed(
  db: Session = Depends(get_db),
  offset: int = 0,
  limit: int = 20,
):
  poems = (
    db.query(Poem)
    .options(joinedload(Poem.genre), joinedload(Poem.poem_tags), joinedload(Poem.user))
    .filter(Poem.is_public == True)
    .order_by(Poem.created_at.desc())
    .offset(offset)
    .limit(limit)
    .all()
  )
  return [build_poem_response(poem) for poem in poems]

@router.get("/", response_model=List[PoemResponse])
def get_my_poems(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
  offset: int = 0,
  limit: int = 20,
):
  poems = (
    db.query(Poem).options(
      joinedload(Poem.genre), joinedload(Poem.poem_tags), joinedload(Poem.user)
    ).filter(Poem.user_id == current_user.id)
    .order_by(Poem.created_at.desc())
    .offset(offset)
    .limit(limit)
    .all()
  )
  print(poems[0].__dict__)
  return [build_poem_response(poem) for poem in poems]
