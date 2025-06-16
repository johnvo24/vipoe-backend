from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.poem import PoemLike
from app.schemas.poem import PoemBaseResponse, PoemResponse, GenreResponse, TagResponse
from app.models import Poem, User, Genre, Tag, PoemTag
from app.auth.dependencies import get_current_user
from app.utils.cloud_utils import upload_image_to_cloud
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func, or_

router = APIRouter()

@router.get("/genres", response_model=list[GenreResponse])
def get_genres(db: Session = Depends(get_db)):
  genres = db.query(Genre).all()
  return genres

@router.get("/tags", response_model=list[TagResponse])
def get_tags(db: Session = Depends(get_db)):
  tags = db.query(Tag).all()
  return tags

@router.post("/", response_model=PoemResponse, status_code=201)
async def create_poem(
  genre_id: int = Form(...),
  prompt: str = Form(...),
  title: str = Form(...),
  content: str = Form(...),
  note: str = Form(None),
  tags: str = Form(""),
  is_public: bool = Form(True),
  image: UploadFile = File(None),
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  # Upload image if provided
  image_url = None
  image_url = await upload_image_to_cloud(image, folder="vipoe/poem_images") if image else ""

  tag_list = [t.strip() for t in tags.split("#") if t.strip()]

  poem = Poem(
    genre_id=genre_id,
    prompt=prompt,
    title=title,
    image_url=image_url,
    content=content,
    note=note,
    is_public=is_public,
    user_id=current_user.id,
  )
  db.add(poem)
  db.flush()  # Ensure the poem is added to get its ID

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
      poem_tag = PoemTag(poem_id=poem.id, tag_id=tag.id)
      db.add(poem_tag)
      tag_objs.append(tag)
    db.commit()
    db.refresh(poem)

  genre = db.query(Genre).filter(Genre.id == poem.genre_id).first()
  poem_base_response = PoemBaseResponse.model_validate(poem)
  return PoemResponse(
    **poem_base_response.model_dump(),
    genre_name=genre.name if genre else "",
    tags=[TagResponse.model_validate(tag) for tag in tag_objs]
  )

@router.put("/{poem_id}", response_model=PoemResponse)
async def update_poem(
  poem_id: int,
  genre_id: int = Form(None),
  prompt: str = Form(None),
  title: str = Form(None),
  content: str = Form(None),
  note: str = Form(None),
  tags: str = Form(None),
  is_public: bool = Form(None),
  image: UploadFile = File(None),
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  poem = db.query(Poem).filter(Poem.id == poem_id, Poem.user_id == current_user.id).first()
  if not poem:
    raise HTTPException(status_code=404, detail="Poem not found")

  if genre_id is not None: poem.genre_id = genre_id
  if prompt is not None: poem.prompt = prompt
  if title is not None: poem.title = title
  if content is not None: poem.content = content
  if note is not None: poem.note = note
  if is_public is not None: poem.is_public = is_public
  if image: poem.image_url = await upload_image_to_cloud(image, folder="vipoe/poem_images")
  tag_objs = []
  if tags is not None:
    tag_list = [t.strip() for t in tags.split("#") if t.strip()]
    db.query(PoemTag).filter(PoemTag.poem_id == poem.id).delete()
    db.flush()
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
        poem_tag = PoemTag(poem_id=poem.id, tag_id=tag.id)
        db.add(poem_tag)
        tag_objs.append(tag)
    else:
      tag_objs = [pt.tag for pt in poem.poem_tags]

  poem.updated_at = datetime.now(timezone.utc)
  db.commit()
  db.refresh(poem)

  genre = db.query(Genre).filter(Genre.id == poem.genre_id).first()
  poem_base_response = PoemBaseResponse.model_validate(poem)
  return PoemResponse(
    **poem_base_response.model_dump(),
    genre_name=genre.name if genre else "",
    tags=[TagResponse.model_validate(tag) for tag in tag_objs]
  )
  
@router.delete("/{poem_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poem(
  poem_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  poem = db.query(Poem).filter(Poem.id == poem_id, Poem.user_id == current_user.id).first()
  if not poem:
    raise HTTPException(status_code=404, detail="Poem not found")
  
  db.delete(poem)
  db.commit()
  return

@router.get("/", response_model=List[PoemResponse])
def search_poems(
  db: Session = Depends(get_db),
  keyword: Optional[str] = None,
  tags: Optional[str] = None,  # đổi từ 'tag' sang 'tags'
  genre_id: Optional[int] = None,
  offset: int = 0,
  limit: int = 20,
):
  query = db.query(Poem).filter(Poem.is_public == True)

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

  result = []
  for poem in poems:
    genre = db.query(Genre).filter(Genre.id == poem.genre_id).first()
    poem_base_response = PoemBaseResponse.model_validate(poem)
    result.append(
      PoemResponse(
        **poem_base_response.model_dump(),
        genre_name=genre.name if genre else "",
        tags=[TagResponse.model_validate(pt.tag) for pt in poem.poem_tags],
      )
    )
  return result

@router.get("/feed", response_model=List[PoemResponse])
def get_poem_feed(
    db: Session = Depends(get_db),
    offset: int = 0,
    limit: int = 20,
):
  poems = (
    db.query(Poem)
    .filter(Poem.is_public == True)
    .order_by(Poem.created_at.desc())
    .offset(offset)
    .limit(limit)
    .all()
  )

  poem_ids = [poem.id for poem in poems]
  likes_counts = dict(
    db.query(PoemLike.poem_id, func.count(PoemLike.id))
      .filter(PoemLike.poem_id.in_(poem_ids))
      .group_by(PoemLike.poem_id)
      .all()
  )

  result = []
  for poem in poems:
    genre = db.query(Genre).filter(Genre.id == poem.genre_id).first()
    poem_base_response = PoemBaseResponse.model_validate(poem)
    poem_data = poem_base_response.model_dump()
    poem_data["likes_count"] = likes_counts.get(poem.id, 0)
    result.append(
      PoemResponse(
        **poem_data,
        genre_name=genre.name if genre else "",
        tags=[TagResponse.model_validate(pt.tag) for pt in poem.poem_tags],
      )
    )
  return result