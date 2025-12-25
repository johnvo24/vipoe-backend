from typing import List
from unittest import case
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from app.auth.dependencies import get_current_user, get_current_user_optional
from app.database import get_db
from app.models.collection_poem import CollectionPoem
from app.models.poem import PoemLike
from app.models.comment import Comment
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
  tags: Optional[str] = None,
  genre_id: Optional[int] = None,
  offset: int = 0,
  limit: int = 20,
  current_user_optional: User = Depends(get_current_user_optional)
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
        Poem.note.ilike(f"%{keyword}%")
      )
    )
  if genre_id:
    query = query.filter(Poem.genre_id == genre_id)
  if tags:
    tag_list = [t.strip() for t in tags.split("#") if t.strip()]
    if tag_list:
      query = query.join(PoemTag).join(Tag).filter(Tag.name.in_(tag_list))

  poems = query.order_by(Poem.created_at.desc()).offset(offset).limit(limit).all()

  poem_ids = [poem.id for poem in poems]

  # Luôn tính like_counts (công khai, không cần auth)
  like_counts = dict(
    db.query(PoemLike.poem_id, func.count(PoemLike.id))
    .filter(PoemLike.poem_id.in_(poem_ids))
    .group_by(PoemLike.poem_id)
    .all()
  )
  
  # Luôn tính comment_counts (công khai)
  comment_counts = dict(
    db.query(Comment.poem_id, func.count(Comment.id))
    .filter(Comment.poem_id.in_(poem_ids))
    .group_by(Comment.poem_id)
    .all()
  )
  
  saved_poems = []
  liked_poems = []
  if current_user_optional:
    # Chỉ tính saved/liked nếu có auth
    saved_poems = db.query(CollectionPoem.poem_id).filter(
      CollectionPoem.user_id == current_user_optional.id,
      CollectionPoem.poem_id.in_(poem_ids)
    ).all()
    liked_poems = db.query(PoemLike.poem_id).filter(
      PoemLike.user_id == current_user_optional.id,
      PoemLike.poem_id.in_(poem_ids)
    ).all()
    saved_poems = [sp.poem_id for sp in saved_poems]
    liked_poems = [lp.poem_id for lp in liked_poems]
  
  return [build_poem_response(poem, like_count = like_counts.get(poem.id, 0), is_saved = poem.id in saved_poems, is_liked = poem.id in liked_poems, comment_count = comment_counts.get(poem.id, 0)) for poem in poems]

@router.get("/feed", response_model=List[PoemResponse])
def get_poem_feed(
  db: Session = Depends(get_db),
  offset: int = 0,
  limit: int = 20,
  current_user_optional: User = Depends(get_current_user_optional),
):
  poems = db.query(Poem).options(
    joinedload(Poem.genre), joinedload(Poem.poem_tags), joinedload(Poem.user)
  ).filter(Poem.is_public == True).order_by(Poem.created_at.desc()).offset(offset).limit(limit).all()
  
  poem_ids = [poem.id for poem in poems]
  # Luôn tính like_counts (công khai, không cần auth)
  like_counts = dict(
    db.query(PoemLike.poem_id, func.count(PoemLike.id))
    .filter(PoemLike.poem_id.in_(poem_ids))
    .group_by(PoemLike.poem_id)
    .all()
  )
  
  # Luôn tính comment_counts (công khai)
  comment_counts = dict(
    db.query(Comment.poem_id, func.count(Comment.id))
    .filter(Comment.poem_id.in_(poem_ids))
    .group_by(Comment.poem_id)
    .all()
  )
  
  saved_poems = []
  liked_poems = []
  if current_user_optional:
    # Chỉ tính saved/liked nếu có auth
    saved_poems = db.query(CollectionPoem.poem_id).filter(
      CollectionPoem.user_id == current_user_optional.id,
      CollectionPoem.poem_id.in_(poem_ids)
    ).all()
    liked_poems = db.query(PoemLike.poem_id).filter(
      PoemLike.user_id == current_user_optional.id,
      PoemLike.poem_id.in_(poem_ids)
    ).all()
    saved_poems = [sp.poem_id for sp in saved_poems]
    liked_poems = [lp.poem_id for lp in liked_poems]
  
  return [build_poem_response(poem, like_count = like_counts.get(poem.id, 0), is_saved = poem.id in saved_poems, is_liked = poem.id in liked_poems, comment_count = comment_counts.get(poem.id, 0)) for poem in poems]

@router.get("/", response_model=List[PoemResponse])
def get_my_poems(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
  offset: int = 0,
  limit: int = 20,
):
  poems = db.query(Poem).options(
    joinedload(Poem.genre), joinedload(Poem.poem_tags), joinedload(Poem.user)
  ).filter(Poem.user_id == current_user.id).order_by(Poem.created_at.desc()).offset(offset).limit(limit).all()
  
  poem_ids = [poem.id for poem in poems]
  
  # Tính toán đầy đủ (vì luôn có auth)
  saved_poems = db.query(CollectionPoem.poem_id).filter(
    CollectionPoem.user_id == current_user.id,
    CollectionPoem.poem_id.in_(poem_ids)
  ).all()
  liked_poems = db.query(PoemLike.poem_id).filter(
    PoemLike.user_id == current_user.id,
    PoemLike.poem_id.in_(poem_ids)
  ).all()
  like_counts = dict(
    db.query(PoemLike.poem_id, func.count(PoemLike.id))
    .filter(PoemLike.poem_id.in_(poem_ids))
    .group_by(PoemLike.poem_id)
    .all()
  )
  comment_counts = dict(
    db.query(Comment.poem_id, func.count(Comment.id))
    .filter(Comment.poem_id.in_(poem_ids))
    .group_by(Comment.poem_id)
    .all()
  )
  saved_poems = [sp.poem_id for sp in saved_poems]
  liked_poems = [lp.poem_id for lp in liked_poems]
  
  return [build_poem_response(poem, like_count = like_counts.get(poem.id, 0), is_saved = poem.id in saved_poems, is_liked = poem.id in liked_poems, comment_count = comment_counts.get(poem.id, 0)) for poem in poems]