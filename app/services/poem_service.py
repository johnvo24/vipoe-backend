from typing import Any
from app.models import Tag, PoemTag
from app.schemas.poem import PoemResponse, TagResponse
from sqlalchemy.orm import Session

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

def build_poem_response(poem: Any) -> PoemResponse:
    return PoemResponse(
      id = poem.id,
      genre_id = poem.genre.id,
      genre_name = poem.genre.name,
      user_id = poem.user_id,
      prompt = poem.prompt,
      title = poem.title,
      image_url = poem.image_url,
      content = poem.content,
      note = poem.note,
      is_public = poem.is_public,
      created_at = poem.created_at,
      updated_at = poem.updated_at,
      tags = [TagResponse.model_validate(pt.tag) for pt in poem.poem_tags]
    )