from typing import Any
from app.models import Tag, PoemTag, PoemLike
from app.schemas.poem import PoemResponse, TagResponse
from sqlalchemy.orm import Session
from app.models.user import User

def handle_tags(db: Session, poem_id: int, tags: str):
  tag_list = [t.strip() for t in tags.split("#") if t.strip()]
  tag_objs = []
  if tag_list:
    existing_tags = db.query(Tag).filter(Tag.name.in_(tag_list)).all()
    existing_tag_names = {tag.name for tag in existing_tags}
    new_tag_names = set(tag_list) - existing_tag_names
    for name in new_tag_names:
      new_tag = Tag(name=name)
      db.add(new_tag)
      db.flush()
      existing_tags.append(new_tag)
    for tag in existing_tags:
      poem_tag = PoemTag(poem_id=poem_id, tag_id=tag.id)
      db.add(poem_tag)
      tag_objs.append(tag)
  return tag_objs

def build_poem_response(
  poem: Any, 
  like_count: int,
  is_saved = False,
  is_liked = False,
  comment_count: int = 0,
  save_count: int = 0
) -> PoemResponse:
  return PoemResponse(
    id = poem.id,
    genre_id = poem.genre.id,
    genre_name = poem.genre.name,
    user_id = poem.user.id,
    user_name = poem.user.username,
    full_name = poem.user.full_name,
    avt_url = poem.user.avt_url,
    prompt = poem.prompt,
    title = poem.title,
    image_url = poem.image_url,
    content = poem.content,
    note = poem.note,
    is_public = poem.is_public,
    created_at = poem.created_at,
    updated_at = poem.updated_at,
    tags = [TagResponse.model_validate(pt.tag) for pt in poem.poem_tags],
    is_saved = is_saved,
    like_count = like_count,
    is_liked = is_liked,
    comment_count = comment_count,
    save_count = save_count,
  )