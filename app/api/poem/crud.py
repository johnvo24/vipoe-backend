from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.schemas.poem import PoemResponse
from app.models import Poem, PoemTag, User
from app.auth.dependencies import get_current_user
from app.services.poem_service import build_poem_response, handle_tags
from app.utils.cloud_utils import upload_image_to_cloud
from datetime import datetime, timezone

router = APIRouter()

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
  image_url = await upload_image_to_cloud(image, folder="vipoe/poem_images") if image else ""
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
  db.flush()
  handle_tags(db, poem.id, tags)
  db.commit()
  db.refresh(poem)
  return build_poem_response(poem)

@router.get("/{poem_id}", response_model=PoemResponse)
def get_poem(
  poem_id: int,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  poem = (
    db.query(Poem)
    .options(joinedload(Poem.genre), joinedload(Poem.poem_tags), joinedload(Poem.user))
    .filter(Poem.id == poem_id, Poem.user_id == current_user.id)
    .first()
  )
  if not poem:
    raise HTTPException(status_code=404, detail="Poem not found")
  return build_poem_response(poem)

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
  if tags is not None:
    db.query(PoemTag).filter(PoemTag.poem_id == poem.id).delete()
    db.flush()
    handle_tags(db, poem.id, tags)
  poem.updated_at = datetime.now(timezone.utc)
  db.commit()
  db.refresh(poem)
  return build_poem_response(poem)

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
