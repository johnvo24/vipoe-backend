from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.poem import PoemBaseResponse, PoemResponse, GenreResponse, TagResponse
from app.models import Poem, User, Genre, Tag, PoemTag
from app.auth.dependencies import get_current_user
from app.utils.cloud_utils import upload_image_to_cloud

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
